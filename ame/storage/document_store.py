"""
文档存储 - 纯 CRUD 职责

重构后版本:
- 职责: 仅负责文档的创建、读取、更新、删除
- 不包含: 检索逻辑、NER处理、结果融合
- 协调: Faiss + Falkor + Metadata 三层存储
"""

import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime

from ame.models.domain import Document
from ame.foundation.storage import VectorStore as FaissStore
from ame.foundation.storage import GraphStore as FalkorStore
from ame.foundation.storage import MetadataStore


class DocumentStore:
    """
    文档存储（纯 CRUD）
    
    设计理念:
    - Faiss: 向量存储
    - Falkor: 图谱存储
    - Metadata: 元数据与索引
    
    数据流:
    - 写入: 并行写入三个存储层
    - 读取: 主要从 Metadata 读取
    - 更新: 同步更新三层
    - 删除: 从所有层删除
    """
    
    def __init__(
        self,
        faiss_store: FaissStore,
        falkor_store: FalkorStore,
        metadata_store: MetadataStore
    ):
        """
        初始化文档存储
        
        Args:
            faiss_store: Faiss 向量存储实例
            falkor_store: Falkor 图谱存储实例
            metadata_store: 元数据存储实例
        """
        self.faiss = faiss_store
        self.graph = falkor_store
        self.metadata = metadata_store
    
    async def create(self, doc: Document) -> Document:
        """
        创建文档（写入所有存储层）
        
        流程:
        1. 并行写入 Faiss 和 Falkor
        2. 保存元数据到 Metadata Store
        
        Args:
            doc: 文档对象（需包含 embedding 和 entities）
        
        Returns:
            doc: 更新后的文档对象
        """
        # 1. 并行写入 Faiss 和 Falkor
        tasks = []
        
        if doc.embedding:
            tasks.append(self._write_to_faiss(doc))
        
        if doc.entities:
            tasks.append(self._write_to_graph(doc))
        
        # 等待所有写入完成
        if tasks:
            await asyncio.gather(*tasks)
        
        # 2. 保存元数据
        doc.status = "active"
        doc.updated_at = datetime.now()
        self.metadata.insert(doc)
        
        return doc
    
    async def get(self, doc_id: str) -> Optional[Document]:
        """
        获取单个文档
        
        Args:
            doc_id: 文档 ID
        
        Returns:
            doc: 文档对象，如果不存在返回 None
        """
        return self.metadata.get(doc_id)
    
    async def get_by_ids(self, doc_ids: List[str]) -> List[Document]:
        """
        批量获取文档
        
        Args:
            doc_ids: 文档 ID 列表
        
        Returns:
            docs: 文档列表
        """
        return self.metadata.get_by_ids(doc_ids)
    
    async def update(
        self,
        doc_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Document]:
        """
        更新文档
        
        注意:
        - 如果更新了 content，需要外部重新生成 embedding
        - 如果更新了 embedding，需要更新 Faiss
        
        Args:
            doc_id: 文档 ID
            updates: 更新字段字典
        
        Returns:
            doc: 更新后的文档对象
        """
        doc = await self.get(doc_id)
        if not doc:
            return None
        
        # 如果更新了 embedding，需要更新 Faiss
        if "embedding" in updates:
            new_embedding = updates["embedding"]
            
            # 先删除旧向量
            if doc.stored_in_faiss:
                await self.faiss.remove(doc_id)
            
            # 添加新向量
            if new_embedding:
                await self._write_to_faiss_with_embedding(
                    doc_id,
                    new_embedding,
                    doc.metadata
                )
        
        # 如果更新了 entities，需要更新 Falkor
        if "entities" in updates:
            new_entities = updates["entities"]
            
            # 删除旧图谱节点
            if doc.stored_in_graph and doc.graph_node_id:
                await self.graph.delete_node(doc.graph_node_id)
            
            # 创建新图谱节点
            if new_entities:
                doc_with_updates = Document(**{**doc.dict(), **updates})
                await self._write_to_graph(doc_with_updates)
        
        # 更新元数据
        updates["updated_at"] = datetime.now()
        self.metadata.update(doc_id, updates)
        
        return await self.get(doc_id)
    
    async def delete(self, doc_id: str) -> bool:
        """
        删除文档（从所有存储层）
        
        流程:
        1. 从 Faiss 删除向量
        2. 从 Falkor 删除图谱节点
        3. 从 Metadata 删除元数据
        
        Args:
            doc_id: 文档 ID
        
        Returns:
            success: 是否删除成功
        """
        doc = await self.get(doc_id)
        if not doc:
            return False
        
        # 并行删除
        tasks = []
        
        if doc.stored_in_faiss:
            tasks.append(self.faiss.remove(doc_id))
        
        if doc.stored_in_graph and doc.graph_node_id:
            tasks.append(self.graph.delete_node(doc.graph_node_id))
        
        if tasks:
            await asyncio.gather(*tasks)
        
        # 删除元数据
        self.metadata.delete(doc_id)
        
        return True
    
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        列出文档（支持过滤）
        
        Args:
            filters: 过滤条件字典
                - doc_type: 文档类型
                - after: 开始时间 (datetime)
                - before: 结束时间 (datetime)
                - limit: 返回数量限制
                - status: 文档状态
        
        Returns:
            docs: 文档列表
        """
        filters = filters or {}
        
        return self.metadata.list(
            doc_type=filters.get("doc_type"),
            after=filters.get("after"),
            before=filters.get("before"),
            limit=filters.get("limit", 100),
            status=filters.get("status")
        )
    
    async def count(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        统计文档数量
        
        Args:
            filters: 过滤条件（同 list 方法）
        
        Returns:
            count: 文档数量
        """
        docs = await self.list(filters)
        return len(docs)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取存储统计信息
        
        Returns:
            stats: 统计信息字典
        """
        return {
            "faiss": self.faiss.get_stats(),
            "graph": self.graph.get_stats() if hasattr(self.graph, "get_stats") else {},
            "metadata": self.metadata.get_stats() if hasattr(self.metadata, "get_stats") else {}
        }
    
    # ========== 私有方法 ==========
    
    async def _write_to_faiss(self, doc: Document) -> None:
        """写入 Faiss 向量存储"""
        if not doc.embedding:
            return
        
        await self.faiss.add(
            vector=doc.embedding,
            doc_id=doc.id,
            metadata={
                "content": doc.content[:500],  # 截断内容
                "doc_type": doc.doc_type,
                "timestamp": doc.timestamp.isoformat() if doc.timestamp else None
            }
        )
        
        doc.stored_in_faiss = True
    
    async def _write_to_faiss_with_embedding(
        self,
        doc_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """使用指定 embedding 写入 Faiss"""
        await self.faiss.add(
            vector=embedding,
            doc_id=doc_id,
            metadata=metadata
        )
    
    async def _write_to_graph(self, doc: Document) -> None:
        """写入 Falkor 图谱存储"""
        if not doc.entities:
            return
        
        # 创建图谱节点
        node_id = await self.graph.add_document(
            doc_id=doc.id,
            content=doc.content,
            entities=doc.entities,
            metadata={
                "doc_type": doc.doc_type,
                "timestamp": doc.timestamp.isoformat() if doc.timestamp else None
            }
        )
        
        doc.graph_node_id = node_id
        doc.stored_in_graph = True

