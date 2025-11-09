"""
HybridRetriever - 混合检索器
"""
from typing import List, Optional, Dict, Any
import logging

from ame.foundation.embedding import EmbeddingBase
from ame.foundation.storage import VectorStore, GraphStore, MetadataStore
from ame.foundation.nlp.ner import NERBase
from ame.foundation.utils import validate_text

from .base import RetrieverBase, RetrievalResult, RetrievalStrategy


logger = logging.getLogger(__name__)


class HybridRetriever(RetrieverBase):
    """
    混合检索器
    
    特性：
    - 向量检索 + 图谱检索
    - 自适应策略选择
    - 结果融合与重排序
    - 多样性增强
    """
    
    def __init__(
        self,
        embedding: EmbeddingBase,
        vector_store: VectorStore,
        graph_store: Optional[GraphStore] = None,
        metadata_store: Optional[MetadataStore] = None,
        ner: Optional[NERBase] = None,
        vector_weight: float = 0.6,
        graph_weight: float = 0.4,
    ):
        """
        Args:
            embedding: 嵌入向量生成器
            vector_store: 向量存储
            graph_store: 图谱存储（可选）
            metadata_store: 元数据存储（可选）
            ner: 命名实体识别器（可选）
            vector_weight: 向量检索权重
            graph_weight: 图谱检索权重
        """
        self.embedding = embedding
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.metadata_store = metadata_store
        self.ner = ner
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        strategy: RetrievalStrategy = RetrievalStrategy.HYBRID,
        rerank: bool = False,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """检索文档"""
        if not validate_text(query):
            return []
        
        # 根据策略选择检索方法
        if strategy == RetrievalStrategy.VECTOR_ONLY:
            results = await self._vector_retrieve(query, top_k, filters)
        
        elif strategy == RetrievalStrategy.GRAPH_ONLY:
            if not self.graph_store:
                logger.warning("Graph store not available, fallback to vector")
                results = await self._vector_retrieve(query, top_k, filters)
            else:
                results = await self._graph_retrieve(query, top_k, filters)
        
        elif strategy == RetrievalStrategy.HYBRID:
            results = await self._hybrid_retrieve(query, top_k, filters)
        
        elif strategy == RetrievalStrategy.ADAPTIVE:
            results = await self._adaptive_retrieve(query, top_k, filters)
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # 重排序
        if rerank and len(results) > 0:
            results = await self._rerank(query, results)
        
        return results[:top_k]
    
    async def _vector_retrieve(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """向量检索"""
        # 生成查询向量
        embedding_result = await self.embedding.embed_text(query)
        
        # 向量检索
        vector_results = await self.vector_store.search(
            query=embedding_result.vector,
            top_k=top_k,
            filters=filters
        )
        
        # 获取文档内容
        results = []
        for r in vector_results:
            content = await self._get_content(r["doc_id"])
            if content:
                results.append(RetrievalResult(
                    doc_id=r["doc_id"],
                    content=content,
                    score=r["score"],
                    source="vector",
                    metadata=r.get("metadata")
                ))
        
        return results
    
    async def _graph_retrieve(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """图谱检索"""
        if not self.graph_store or not self.ner:
            return []
        
        # 提取实体
        entities = await self.ner.extract(query)
        entity_names = [e.text for e in entities]
        
        if not entity_names:
            logger.info("No entities found, fallback to vector")
            return await self._vector_retrieve(query, top_k, filters)
        
        # 基于实体检索
        graph_results = await self.graph_store.search_by_entities(
            entities=entity_names,
            top_k=top_k
        )
        
        # 转换结果
        results = []
        for r in graph_results:
            content = await self._get_content(r["doc_id"])
            if content:
                results.append(RetrievalResult(
                    doc_id=r["doc_id"],
                    content=content,
                    score=r["score"],
                    source="graph",
                    matched_entities=r.get("matched_entities", [])
                ))
        
        return results
    
    async def _hybrid_retrieve(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """混合检索"""
        # 向量检索
        vector_results = await self._vector_retrieve(query, top_k * 2, filters)
        
        # 图谱检索
        graph_results = []
        if self.graph_store and self.ner:
            graph_results = await self._graph_retrieve(query, top_k * 2, filters)
        
        # 融合结果
        results = self._fuse_results(vector_results, graph_results)
        
        return results
    
    async def _adaptive_retrieve(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """自适应检索"""
        # 分析查询特征
        has_entities = False
        if self.ner:
            entities = await self.ner.extract(query)
            has_entities = len(entities) > 0
        
        # 根据查询特征选择策略
        if has_entities and self.graph_store:
            # 实体丰富 → 图谱检索为主
            strategy = RetrievalStrategy.HYBRID
            self.vector_weight = 0.3
            self.graph_weight = 0.7
        else:
            # 语义查询 → 向量检索为主
            strategy = RetrievalStrategy.HYBRID
            self.vector_weight = 0.7
            self.graph_weight = 0.3
        
        return await self.retrieve(query, top_k, strategy, rerank=False, filters=filters)
    
    def _fuse_results(
        self,
        vector_results: List[RetrievalResult],
        graph_results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """融合向量和图谱检索结果"""
        # 创建文档映射
        doc_map: Dict[str, RetrievalResult] = {}
        
        # 添加向量结果
        for r in vector_results:
            if r.doc_id not in doc_map:
                r.score *= self.vector_weight
                doc_map[r.doc_id] = r
        
        # 融合图谱结果
        for r in graph_results:
            if r.doc_id in doc_map:
                # 已存在，融合分数
                existing = doc_map[r.doc_id]
                existing.score += r.score * self.graph_weight
                existing.source = "hybrid"
                if r.matched_entities:
                    existing.matched_entities = r.matched_entities
            else:
                # 新结果
                r.score *= self.graph_weight
                doc_map[r.doc_id] = r
        
        # 排序并返回
        results = list(doc_map.values())
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
    
    async def _rerank(
        self,
        query: str,
        results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """重排序（简化版 - 基于关键词匹配）"""
        query_lower = query.lower()
        query_tokens = set(query_lower.split())
        
        for result in results:
            content_lower = result.content.lower()
            content_tokens = set(content_lower.split())
            
            # 计算关键词重叠度
            overlap = len(query_tokens.intersection(content_tokens))
            overlap_ratio = overlap / len(query_tokens) if query_tokens else 0
            
            # 调整分数
            result.score = result.score * 0.7 + overlap_ratio * 0.3
        
        # 重新排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    async def _get_content(self, doc_id: str) -> Optional[str]:
        """获取文档内容"""
        if self.metadata_store:
            metadata = await self.metadata_store.get(doc_id)
            if metadata:
                return metadata.get("content")
        
        return None
