"""
混合存储仓库
职责：协调 Faiss（向量）+ Falkor（图谱）+ SQLite（元数据）的统一访问
"""
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from ame.models.domain import Document, DocumentType, DataLayer, SearchResult
from ame.storage.faiss_store import FaissStore
from ame.storage.falkor_store import FalkorStore, MockFalkorStore
from ame.storage.metadata_store import MetadataStore
from ame.ner.base import NERBase
from ame.ner.hybrid_ner import HybridNER


class HybridRepository:
    """
    混合存储仓库
    
    设计理念：
    - Faiss: 快速向量检索（0-30天热温数据）
    - Falkor: 长期图谱分析（全生命周期）
    - SQLite: 元数据与索引管理
    
    数据流：
    1. 写入：并行写入三个存储层
    2. 检索：混合检索 + 融合排序
    3. 生命周期：定期降温（热→温→冷）
    """
    
    def __init__(
        self,
        faiss_store: FaissStore,
        falkor_store: FalkorStore,
        metadata_store: MetadataStore,
        embedding_function: Optional[Any] = None,
        ner_service: Optional[NERBase] = None
    ):
        """
        Args:
            faiss_store: Faiss 向量存储
            falkor_store: Falkor 图谱存储
            metadata_store: 元数据存储
            embedding_function: 向量化函数（用于生成 embedding）
            ner_service: NER 实体提取服务（可选，默认使用 HybridNER）
        """
        self.faiss = faiss_store
        self.graph = falkor_store
        self.metadata = metadata_store
        self.embedding_fn = embedding_function
        self.ner = ner_service or HybridNER()
    
    async def create(self, doc: Document) -> Document:
        """
        创建文档（双写策略）
        
        流程：
        1. 生成 embedding（如果需要）
        2. 并行写入 Faiss 和 Falkor
        3. 保存元数据到 SQLite
        
        Args:
            doc: 文档对象
        
        Returns:
            doc: 更新后的文档对象
        """
        # 1. 生成 embedding
        if not doc.embedding and self.embedding_fn:
            doc.embedding = await self.embedding_fn(doc.content)
        
        # 2. 并行写入 Faiss 和 Falkor
        tasks = []
        
        if doc.embedding:
            tasks.append(self._write_to_faiss(doc))
        
        tasks.append(self._write_to_graph(doc))
        
        # 等待所有写入完成
        await asyncio.gather(*tasks)
        
        # 3. 保存元数据
        doc.status = "active"
        doc.updated_at = datetime.now()
        self.metadata.insert(doc)
        
        return doc
    
    async def get(self, doc_id: str) -> Optional[Document]:
        """获取单个文档"""
        return self.metadata.get(doc_id)
    
    async def get_by_ids(self, doc_ids: List[str]) -> List[Document]:
        """批量获取文档"""
        return self.metadata.get_by_ids(doc_ids)
    
    async def update(self, doc_id: str, updates: Dict[str, Any]) -> Optional[Document]:
        """
        更新文档
        
        注意：如果更新了 content，需要重新生成 embedding 并更新 Faiss
        """
        doc = await self.get(doc_id)
        if not doc:
            return None
        
        # 如果更新了内容，重新生成 embedding
        if "content" in updates:
            new_content = updates["content"]
            if self.embedding_fn:
                new_embedding = await self.embedding_fn(new_content)
                updates["embedding"] = new_embedding
                
                # 更新 Faiss（需要先删除再添加）
                if doc.faiss_index is not None:
                    await self.faiss.remove(doc_id)
                await self.faiss.add(new_embedding, doc_id)
        
        # 更新元数据
        self.metadata.update(doc_id, updates)
        
        return await self.get(doc_id)
    
    async def delete(self, doc_id: str) -> bool:
        """
        删除文档（从所有存储层）
        
        流程：
        1. 从 Faiss 删除
        2. 从 Falkor 删除节点
        3. 从 SQLite 删除元数据
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
        
        await asyncio.gather(*tasks)
        
        # 删除元数据
        self.metadata.delete(doc_id)
        
        return True
    
    async def hybrid_search(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        top_k: int = 10,
        faiss_weight: float = 0.6,
        graph_weight: float = 0.4,
        filters: Optional[Dict] = None
    ) -> List[SearchResult]:
        """
        混合检索（Faiss + Falkor 融合）
        
        流程：
        1. 并行执行 Faiss 向量检索和 Falkor 图谱检索
        2. 融合结果（加权求和）
        3. 去重排序
        4. 获取完整文档
        
        Args:
            query: 查询文本
            query_embedding: 查询向量（可选，如果提供则跳过向量化）
            top_k: 返回前 K 个结果
            faiss_weight: Faiss 检索权重（默认 0.6）
            graph_weight: Falkor 检索权重（默认 0.4）
            filters: 过滤条件
        
        Returns:
            results: 检索结果列表
        """
        # 1. 生成查询向量
        if not query_embedding and self.embedding_fn:
            query_embedding = await self.embedding_fn(query)
        
        # 2. 并行检索
        tasks = []
        
        # Faiss 向量检索
        if query_embedding:
            tasks.append(self.faiss.search(query_embedding, top_k * 2))
        else:
            tasks.append(asyncio.sleep(0))  # 占位
        
        # Falkor 图谱检索（基于实体）
        tasks.append(self._graph_search(query, top_k))
        
        faiss_results, graph_results = await asyncio.gather(*tasks)
        
        # 3. 融合结果
        merged = self._merge_results(
            faiss_results if isinstance(faiss_results, list) else [],
            graph_results,
            faiss_weight,
            graph_weight
        )
        
        # 4. 应用过滤器
        if filters:
            merged = self._apply_filters(merged, filters)
        
        # 5. 获取完整文档
        top_results = merged[:top_k]
        doc_ids = [r["doc_id"] for r in top_results]
        docs = await self.get_by_ids(doc_ids)
        
        # 6. 构建搜索结果
        doc_map = {doc.id: doc for doc in docs}
        
        search_results = []
        for r in top_results:
            doc = doc_map.get(r["doc_id"])
            if doc:
                search_results.append(SearchResult(
                    doc_id=doc.id,
                    content=doc.content,
                    score=r["score"],
                    source=r["source"],
                    metadata=doc.metadata,
                    entities=doc.entities
                ))
        
        return search_results
    
    async def lifecycle_management(self):
        """
        数据生命周期管理（热→温→冷）
        
        规则：
        - 7天前：热 → 温（保留在 Faiss，降低重要性）
        - 30天前：温 → 冷（从 Faiss 删除，仅保留在 Falkor）
        """
        now = datetime.now()
        
        # 1. 热 → 温（7天）
        hot_docs = self.metadata.list(
            layer=DataLayer.HOT,
            before=now - timedelta(days=7),
            limit=1000
        )
        
        for doc in hot_docs:
            if doc.importance > 0.7:
                # 重要文档：降级为温
                self.metadata.update(doc.id, {"layer": DataLayer.WARM})
            else:
                # 普通文档：直接冷存储
                await self.faiss.remove(doc.id)
                self.metadata.update(doc.id, {
                    "layer": DataLayer.COLD,
                    "stored_in_faiss": False
                })
        
        # 2. 温 → 冷（30天）
        warm_docs = self.metadata.list(
            layer=DataLayer.WARM,
            before=now - timedelta(days=30),
            limit=1000
        )
        
        for doc in warm_docs:
            await self.faiss.remove(doc.id)
            self.metadata.update(doc.id, {
                "layer": DataLayer.COLD,
                "stored_in_faiss": False
            })
    
    async def _write_to_faiss(self, doc: Document):
        """写入 Faiss"""
        if not doc.embedding:
            return
        
        faiss_id = await self.faiss.add(doc.embedding, doc.id)
        doc.faiss_index = faiss_id
        doc.stored_in_faiss = True
    
    async def _write_to_graph(self, doc: Document):
        """
        写入 Falkor（包含 NER 实体提取与关系构建）
        
        流程：
        1. 创建文档节点
        2. 提取实体（使用 NER 服务）
        3. 创建实体节点（带类型）
        4. 创建 MENTIONS 关系（带权重）
        """
        # 1. 创建文档节点
        node_id = await self.graph.create_node("Document", {
            "id": doc.id,
            "content": doc.content[:500],  # 存储前500字符
            "doc_type": doc.doc_type,
            "timestamp": doc.timestamp.isoformat() if doc.timestamp else None
        })
        doc.graph_node_id = node_id
        doc.stored_in_graph = True
        
        # 2. 提取实体（使用 NER 服务，返回 Entity 对象）
        entity_objects = await self._extract_entity_objects(doc.content)
        
        # 3. 创建实体关系（带类型和权重）
        for entity_obj in entity_objects:
            # 创建或获取实体节点（带类型）
            entity_id = await self.graph.get_or_create_entity(
                entity_name=entity_obj.text,
                entity_type=entity_obj.type,
                metadata={"score": entity_obj.score}
            )
            
            # 创建 MENTIONS 关系（权重基于实体置信度）
            await self.graph.create_relation(
                source_id=node_id,
                target_id=entity_id,
                relation_type="MENTIONS",
                weight=entity_obj.score  # 使用实体置信度作为关系权重
            )
        
        # 保存实体名列表到文档（向后兼容）
        if not doc.entities:
            doc.entities = [entity.text for entity in entity_objects]
    
    async def _extract_entities(self, text: str) -> List[str]:
        """
        提取实体（NER）
        
        使用 NER 服务提取文本中的实体
        """
        if not text or not text.strip():
            return []
        
        try:
            entities = await self.ner.extract(text)
            # 转换为字符串列表（仅保留实体文本）
            return [entity.text for entity in entities]
        except Exception as e:
            # 如果 NER 服务失败，返回空列表
            import logging
            logging.error(f"NER 实体提取失败: {e}")
            return []
    
    async def _extract_entity_objects(self, text: str):
        """
        提取实体对象（带类型和分数）
        
        Returns:
            List[Entity]: 实体对象列表
        """
        if not text or not text.strip():
            return []
        
        try:
            entities = await self.ner.extract(text)
            return entities
        except Exception as e:
            import logging
            logging.error(f"NER 实体提取失败: {e}")
            return []
    
    async def _graph_search(self, query: str, top_k: int) -> List[Dict]:
        """图谱检索（基于实体）"""
        # 提取查询中的实体
        entities = await self._extract_entities(query)
        
        if not entities:
            return []
        
        # 图谱检索
        return await self.graph.search_by_entities(query, entities, top_k)
    
    def _merge_results(
        self,
        faiss_results: List[Dict],
        graph_results: List[Dict],
        faiss_weight: float = 0.6,
        graph_weight: float = 0.4
    ) -> List[Dict]:
        """
        融合检索结果（加权求和）
        
        融合策略：
        - Faiss 分数 * 0.6 + Graph 分数 * 0.4
        - 去重（同一文档只保留最高分）
        - 按分数降序排序
        """
        scores: Dict[str, Dict] = {}
        
        # 1. 累加 Faiss 分数
        for r in faiss_results:
            doc_id = r["doc_id"]
            scores[doc_id] = {
                "doc_id": doc_id,
                "score": r["score"] * faiss_weight,
                "source": "faiss"
            }
        
        # 2. 累加 Graph 分数
        for r in graph_results:
            doc_id = r["doc_id"]
            if doc_id in scores:
                scores[doc_id]["score"] += r["score"] * graph_weight
                scores[doc_id]["source"] = "hybrid"
            else:
                scores[doc_id] = {
                    "doc_id": doc_id,
                    "score": r["score"] * graph_weight,
                    "source": "graph"
                }
        
        # 3. 排序
        sorted_results = sorted(
            scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        return sorted_results
    
    def _apply_filters(
        self,
        results: List[Dict],
        filters: Dict[str, Any]
    ) -> List[Dict]:
        """应用过滤条件"""
        # TODO: 实现基于元数据的过滤
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        return {
            "faiss": self.faiss.get_stats(),
            "metadata": {
                "total": self.metadata.count(),
                "hot": self.metadata.count(layer=DataLayer.HOT),
                "warm": self.metadata.count(layer=DataLayer.WARM),
                "cold": self.metadata.count(layer=DataLayer.COLD),
            }
        }
