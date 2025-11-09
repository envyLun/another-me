"""
Document Service - 文档管理服务

提供文档 CRUD 的业务级服务
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from ame.models.domain import Document, DocumentType
from ame.storage.document_store import DocumentStore
from ame.data_processor.document_processor import DocumentProcessor


class DocumentService:
    """
    文档管理服务
    
    职责：
    - 文档的创建、读取、更新、删除
    - 文档预处理（NER + Embedding）
    - 批量操作支持
    """
    
    def __init__(
        self,
        document_store: DocumentStore,
        document_processor: Optional[DocumentProcessor] = None
    ):
        """
        初始化文档服务
        
        Args:
            document_store: 文档存储
            document_processor: 文档处理器（可选）
        """
        self.store = document_store
        self.processor = document_processor
    
    async def create_document(
        self,
        content: str,
        doc_type: DocumentType = DocumentType.GENERAL,
        metadata: Optional[Dict[str, Any]] = None,
        auto_process: bool = True
    ) -> Document:
        """
        创建文档
        
        Args:
            content: 文档内容
            doc_type: 文档类型
            metadata: 元数据
            auto_process: 是否自动预处理（NER + Embedding）
        
        Returns:
            document: 创建的文档对象
        """
        # 创建文档对象
        doc = Document(
            content=content,
            doc_type=doc_type,
            metadata=metadata or {},
            timestamp=datetime.now()
        )
        
        # 自动预处理
        if auto_process and self.processor:
            doc = await self.processor.process(doc)
        
        # 存储
        doc = await self.store.create(doc)
        
        return doc
    
    async def batch_create(
        self,
        documents: List[Dict[str, Any]],
        auto_process: bool = True
    ) -> List[Document]:
        """
        批量创建文档
        
        Args:
            documents: 文档数据列表
            auto_process: 是否自动预处理
        
        Returns:
            created_docs: 创建的文档列表
        """
        docs = []
        
        for doc_data in documents:
            doc = Document(
                content=doc_data["content"],
                doc_type=doc_data.get("doc_type", DocumentType.GENERAL),
                metadata=doc_data.get("metadata", {}),
                timestamp=doc_data.get("timestamp", datetime.now())
            )
            docs.append(doc)
        
        # 批量预处理
        if auto_process and self.processor:
            docs = await self.processor.batch_process(docs)
        
        # 批量存储
        created_docs = []
        for doc in docs:
            created_doc = await self.store.create(doc)
            created_docs.append(created_doc)
        
        return created_docs
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档"""
        return await self.store.get(doc_id)
    
    async def get_documents(self, doc_ids: List[str]) -> List[Document]:
        """批量获取文档"""
        return await self.store.get_by_ids(doc_ids)
    
    async def update_document(
        self,
        doc_id: str,
        updates: Dict[str, Any],
        reprocess: bool = False
    ) -> Optional[Document]:
        """
        更新文档
        
        Args:
            doc_id: 文档 ID
            updates: 更新内容
            reprocess: 是否重新处理（当内容变化时）
        
        Returns:
            updated_doc: 更新后的文档
        """
        # 如果内容变化且需要重新处理
        if reprocess and "content" in updates and self.processor:
            doc = await self.store.get(doc_id)
            if doc:
                doc.content = updates["content"]
                # 重新生成 embedding 和实体
                doc = await self.processor.process(doc)
                updates["embedding"] = doc.embedding
                updates["entities"] = doc.entities
        
        return await self.store.update(doc_id, updates)
    
    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        return await self.store.delete(doc_id)
    
    async def list_documents(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Document]:
        """
        列出文档
        
        Args:
            filters: 过滤条件
            limit: 返回数量
            offset: 偏移量
        
        Returns:
            documents: 文档列表
        """
        query = filters or {}
        query["limit"] = limit
        query["offset"] = offset
        
        return await self.store.list(query)
    
    async def count_documents(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        统计文档数量
        
        Args:
            filters: 过滤条件
        
        Returns:
            count: 文档数量
        """
        return await self.store.count(filters or {})
