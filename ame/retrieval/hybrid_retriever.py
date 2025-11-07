"""
混合检索器 - 结合多种检索策略
支持：向量检索 + 图谱检索 + 关键词检索 + 时间加权

优化版本 (v2.0):
- 支持 Faiss 向量检索
- 支持 Falkor 图谱检索
- 多维度融合（向量 + 图谱 + 关键词 + 时间）
"""

import asyncio
import re
import math
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from .base import RetrieverBase, RetrievalResult
from .vector_retriever import VectorRetriever
from .graph_retriever import GraphRetriever


class HybridRetriever(RetrieverBase):
    """混合检索器（优化版 v2.0）"""
    
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        graph_retriever: Optional[GraphRetriever] = None,
        vector_weight: float = 0.6,
        graph_weight: float = 0.4,
        keyword_weight: float = 0.0,
        time_weight: float = 0.0
    ):
        """
        初始化混合检索器
        
        Args:
            vector_retriever: 向量检索器（Faiss）
            graph_retriever: 图谱检索器（Falkor，可选）
            vector_weight: 向量检索权重（默认 0.6）
            graph_weight: 图谱检索权重（默认 0.4）
            keyword_weight: 关键词检索权重（默认 0.0）
            time_weight: 时间权重（默认 0.0）
        """
        self.vector_retriever = vector_retriever
        self.graph_retriever = graph_retriever
        
        # 归一化权重
        total = vector_weight + graph_weight + keyword_weight + time_weight
        self.vector_weight = vector_weight / total
        self.graph_weight = graph_weight / total
        self.keyword_weight = keyword_weight / total
        self.time_weight = time_weight / total
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[RetrievalResult]:
        """
        混合检索策略（优化版）
        
        流程:
        1. 并行执行 Faiss 向量检索和 Falkor 图谱检索
        2. 可选：关键词和时间增强
        3. 多维度融合
        4. 重排序输出
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件
            **kwargs: 其他参数
                - keyword_boost: 关键词加权词列表
                - time_decay_days: 时间衰减天数
                - enable_multi_hop: 是否启用多跳推理（图谱）
                - max_hops: 最大跳数
        """
        tasks = []
        
        # 1. Faiss 向量检索
        tasks.append(self.vector_retriever.retrieve(
            query=query,
            top_k=top_k * 2,  # 召回更多用于融合
            filters=filters
        ))
        
        # 2. Falkor 图谱检索（如果启用）
        if self.graph_retriever and self.graph_weight > 0:
            tasks.append(self.graph_retriever.retrieve(
                query=query,
                top_k=top_k * 2,
                filters=filters,
                enable_multi_hop=kwargs.get("enable_multi_hop", False),
                max_hops=kwargs.get("max_hops", 2)
            ))
        
        # 并行执行
        results_list = await asyncio.gather(*tasks)
        
        vector_results = results_list[0]
        graph_results = results_list[1] if len(results_list) > 1 else []
        
        # 3. 计算增强分数
        keyword_scores = self._calculate_keyword_scores(
            query,
            vector_results,
            boost_keywords=kwargs.get("keyword_boost", [])
        )
        
        time_scores = self._calculate_time_scores(
            vector_results,
            decay_days=kwargs.get("time_decay_days", 365)
        )
        
        # 4. 融合分数
        final_results = self._fuse_multi_source(
            vector_results,
            graph_results,
            keyword_scores,
            time_scores
        )
        
        # 5. 排序并返回
        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results[:top_k]
    
    def _fuse_multi_source(
        self,
        vector_results: List[RetrievalResult],
        graph_results: List[RetrievalResult],
        keyword_scores: Dict[int, float],
        time_scores: Dict[int, float]
    ) -> List[RetrievalResult]:
        """
        多源融合算法
        
        规则:
        1. 按 doc_id 聚合分数
        2. 同文档的不同来源分数累加
        3. 去重并排序
        """
        # 按 doc_id 聚合
        score_map: Dict[str, Dict] = {}
        
        # 1. 向量结果
        for i, result in enumerate(vector_results):
            doc_id = result.metadata.get("doc_id", "")
            score_map[doc_id] = {
                "content": result.content,
                "metadata": result.metadata,
                "vector_score": result.score * self.vector_weight,
                "graph_score": 0.0,
                "keyword_score": keyword_scores.get(i, 0.0) * self.keyword_weight,
                "time_score": time_scores.get(i, 0.5) * self.time_weight
            }
        
        # 2. 图谱结果
        for result in graph_results:
            doc_id = result.metadata.get("doc_id", "")
            if doc_id in score_map:
                score_map[doc_id]["graph_score"] = result.score * self.graph_weight
            else:
                score_map[doc_id] = {
                    "content": result.content,
                    "metadata": result.metadata,
                    "vector_score": 0.0,
                    "graph_score": result.score * self.graph_weight,
                    "keyword_score": 0.0,
                    "time_score": 0.5 * self.time_weight
                }
        
        # 3. 计算最终分数
        final_results = []
        for doc_id, scores in score_map.items():
            final_score = (
                scores["vector_score"] +
                scores["graph_score"] +
                scores["keyword_score"] +
                scores["time_score"]
            )
            
            final_results.append(RetrievalResult(
                content=scores["content"],
                metadata={
                    **scores["metadata"],
                    "vector_score": scores["vector_score"],
                    "graph_score": scores["graph_score"],
                    "keyword_score": scores["keyword_score"],
                    "time_score": scores["time_score"]
                },
                score=final_score,
                source="hybrid_v2"
            ))
        
        return final_results
    
    def _calculate_keyword_scores(
        self,
        query: str,
        results: List[RetrievalResult],
        boost_keywords: List[str] = None
    ) -> Dict[int, float]:
        """计算关键词匹配分数"""
        scores = {}
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        boost_keywords = boost_keywords or []
        boost_set = set(k.lower() for k in boost_keywords)
        
        for i, result in enumerate(results):
            content_lower = result.content.lower()
            content_words = set(re.findall(r'\w+', content_lower))
            
            # 计算词重叠率
            overlap = len(query_words & content_words)
            overlap_ratio = overlap / max(len(query_words), 1)
            
            # 加权词加成
            boost_score = sum(1 for word in boost_set if word in content_lower)
            boost_ratio = boost_score / max(len(boost_set), 1) if boost_set else 0
            
            # 综合分数
            scores[i] = 0.7 * overlap_ratio + 0.3 * boost_ratio
        
        return scores
    
    def _calculate_time_scores(
        self,
        results: List[RetrievalResult],
        decay_days: int = 365
    ) -> Dict[int, float]:
        """计算时间衰减分数（越新越高）"""
        scores = {}
        now = datetime.now()
        
        for i, result in enumerate(results):
            timestamp_str = result.metadata.get("timestamp", "")
            
            try:
                # 尝试解析时间戳
                if timestamp_str:
                    doc_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    days_diff = (now - doc_time).days
                    
                    # 指数衰减：score = e^(-days/decay_days)
                    import math
                    score = math.exp(-days_diff / decay_days)
                    scores[i] = score
                else:
                    # 没有时间戳，给中等分数
                    scores[i] = 0.5
            except:
                # 解析失败，给中等分数
                scores[i] = 0.5
        
        return scores
    
    def get_name(self) -> str:
        return "HybridRetriever"
