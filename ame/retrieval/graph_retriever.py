"""
GraphRetriever: 基于 Falkor 图谱的检索器

特点：
- 实体关系检索
- 多跳推理扩展
- 关系权重计算
"""

import logging
from typing import List, Dict, Optional, Any

from ame.retrieval.base import RetrieverBase, RetrievalResult
from ame.foundation.storage import GraphStore as FalkorStore
from ame.foundation.nlp.ner import NERBase, Entity
from ame.foundation.nlp.ner import HybridNER

logger = logging.getLogger(__name__)


class GraphRetriever(RetrieverBase):
    """图谱检索器（基于 Falkor）"""
    
    def __init__(
        self,
        falkor_store: FalkorStore,
        ner_service: Optional[NERBase] = None,
        enable_multi_hop: bool = True,
        max_hops: int = 2
    ):
        """
        初始化 GraphRetriever
        
        Args:
            falkor_store: Falkor 图谱存储
            ner_service: NER 服务（用于提取查询实体）
            enable_multi_hop: 是否启用多跳推理
            max_hops: 最大跳数（默认 2）
        """
        self.graph = falkor_store
        self.ner = ner_service or HybridNER()
        self.enable_multi_hop = enable_multi_hop
        self.max_hops = max_hops
        
        logger.info(
            f"GraphRetriever 初始化完成 (多跳: {enable_multi_hop}, 最大跳数: {max_hops})"
        )
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
        **kwargs
    ) -> List[RetrievalResult]:
        """
        图谱检索
        
        流程:
        1. NER 提取查询实体
        2. Falkor 查询相关文档
        3. 多跳推理（可选）
        4. 返回结果
        
        Args:
            query: 查询文本
            top_k: 返回前 K 个结果
            filters: 过滤条件（可选）
            **kwargs: 扩展参数
                - enable_multi_hop: 是否启用多跳推理（覆盖默认值）
                - max_hops: 最大跳数（覆盖默认值）
        
        Returns:
            results: 检索结果列表
        """
        if not query or not query.strip():
            return []
        
        # 1. 提取实体
        entities = await self._extract_entities(query)
        
        if not entities:
            logger.debug(f"GraphRetriever: 未从查询中提取到实体: {query}")
            return []
        
        logger.debug(f"GraphRetriever: 提取到 {len(entities)} 个实体: {entities}")
        
        # 2. 图谱检索
        graph_results = await self.graph.search_by_entities(
            query=query,
            entities=entities,
            top_k=top_k * 2  # 召回更多，后续过滤
        )
        
        if not graph_results:
            logger.debug("GraphRetriever: 图谱检索未找到结果")
            return []
        
        # 3. 多跳推理（扩展相关文档）
        enable_multi_hop = kwargs.get("enable_multi_hop", self.enable_multi_hop)
        if enable_multi_hop:
            max_hops = kwargs.get("max_hops", self.max_hops)
            graph_results = await self._expand_with_multi_hop(
                graph_results,
                max_hops=max_hops
            )
        
        # 4. 转换为 RetrievalResult
        results = self._convert_to_results(graph_results)
        
        # 5. 排序并返回 top_k
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results[:top_k]
    
    async def _extract_entities(self, text: str) -> List[str]:
        """
        实体提取
        
        Args:
            text: 输入文本
        
        Returns:
            entities: 实体名列表
        """
        try:
            entity_objects = await self.ner.extract(text)
            # 转换为字符串列表
            return [entity.text for entity in entity_objects]
        except Exception as e:
            logger.error(f"GraphRetriever 实体提取失败: {e}")
            
            # Fallback: 简单分词
            return self._fallback_extract(text)
    
    def _fallback_extract(self, text: str) -> List[str]:
        """
        备用实体提取（简单分词）
        
        Args:
            text: 输入文本
        
        Returns:
            words: 关键词列表
        """
        try:
            import jieba
            words = jieba.lcut(text)
            # 过滤短词和停用词
            return [w for w in words if len(w) > 1 and w not in {"的", "了", "在", "是"}]
        except ImportError:
            # 如果 jieba 不可用，简单按空格分割
            return text.split()
    
    async def _expand_with_multi_hop(
        self,
        initial_results: List[Dict],
        max_hops: int = 2
    ) -> List[Dict]:
        """
        多跳推理扩展
        
        Args:
            initial_results: 初始检索结果
            max_hops: 最大跳数
        
        Returns:
            expanded_results: 扩展后的结果
        """
        expanded = list(initial_results)
        existing_doc_ids = {r["doc_id"] for r in initial_results}
        
        # 取前 5 个结果进行扩展（避免性能问题）
        top_results = initial_results[:5]
        
        for result in top_results:
            doc_id = result["doc_id"]
            
            # 查找相关文档
            try:
                related_docs = await self.graph.find_related_docs(
                    doc_id=doc_id,
                    max_hops=max_hops,
                    limit=10
                )
                
                # 添加新文档
                for related in related_docs:
                    related_doc_id = related.get("doc_id")
                    
                    if related_doc_id and related_doc_id not in existing_doc_ids:
                        # 计算衰减分数
                        distance = related.get("distance", 1)
                        decay_factor = 0.7 ** distance  # 距离越远衰减越多
                        
                        expanded.append({
                            "doc_id": related_doc_id,
                            "score": result["score"] * decay_factor,
                            "source": "graph_expanded",
                            "hop_distance": distance,
                            "base_doc_id": doc_id
                        })
                        
                        existing_doc_ids.add(related_doc_id)
            
            except Exception as e:
                logger.error(f"GraphRetriever 多跳推理失败 (doc_id={doc_id}): {e}")
                continue
        
        logger.debug(
            f"GraphRetriever: 多跳推理扩展 {len(initial_results)} -> {len(expanded)} 个结果"
        )
        
        return expanded
    
    def _convert_to_results(self, graph_results: List[Dict]) -> List[RetrievalResult]:
        """
        转换为 RetrievalResult 对象
        
        Args:
            graph_results: 图谱检索原始结果
        
        Returns:
            results: RetrievalResult 列表
        """
        results = []
        
        for r in graph_results:
            doc_id = r.get("doc_id")
            if not doc_id:
                continue
            
            # 构建元数据
            metadata = {
                "doc_id": doc_id,
                "source": r.get("source", "graph"),
            }
            
            # 添加可选字段
            if "matched_entities" in r:
                metadata["matched_entities"] = r["matched_entities"]
            
            if "hop_distance" in r:
                metadata["hop_distance"] = r["hop_distance"]
            
            if "base_doc_id" in r:
                metadata["base_doc_id"] = r["base_doc_id"]
            
            if "shared_entities" in r:
                metadata["shared_entities"] = r["shared_entities"]
            
            results.append(RetrievalResult(
                content="",  # 内容在后续从 Repository 获取
                metadata=metadata,
                score=r.get("score", 0.5),
                source=metadata["source"]
            ))
        
        return results
