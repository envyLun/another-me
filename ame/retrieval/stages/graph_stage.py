"""
图谱召回阶段

职责：
1. 提取查询实体
2. Falkor 图谱检索
3. 可选多跳推理扩展
"""

import logging
from typing import List, Dict, Any, Optional

from ame.retrieval.stages.base import StageBase
from ame.retrieval.base import RetrievalResult
from ame.retrieval.graph_retriever import GraphRetriever

logger = logging.getLogger(__name__)


class GraphRetrievalStage(StageBase):
    """图谱召回阶段"""
    
    def __init__(
        self,
        graph_retriever: GraphRetriever,
        weight: float = 1.0,
        enable_multi_hop: bool = False,
        max_hops: int = 2
    ):
        """
        初始化图谱召回阶段
        
        Args:
            graph_retriever: 图谱检索器实例
            weight: 分数权重（默认 1.0）
            enable_multi_hop: 是否启用多跳推理
            max_hops: 最大跳数
        """
        self.retriever = graph_retriever
        self.weight = weight
        self.enable_multi_hop = enable_multi_hop
        self.max_hops = max_hops
        
        logger.debug(
            f"GraphRetrievalStage 初始化 "
            f"(weight={weight}, multi_hop={enable_multi_hop}, max_hops={max_hops})"
        )
    
    async def process(
        self,
        query: str,
        previous_results: Optional[List[RetrievalResult]],
        context: Dict[str, Any]
    ) -> List[RetrievalResult]:
        """
        执行图谱召回
        
        Args:
            query: 查询文本
            previous_results: 前序结果
            context: 上下文信息
        
        Returns:
            results: 图谱检索结果 + 前序结果
        """
        top_k = context.get("top_k", 10)
        recall_k = top_k * 2
        
        logger.debug(f"GraphRetrievalStage: 召回 top_{recall_k} 结果")
        
        try:
            results = await self.retriever.retrieve(
                query=query,
                top_k=recall_k,
                enable_multi_hop=self.enable_multi_hop,
                max_hops=self.max_hops
            )
            
            # 应用权重
            for r in results:
                r.score *= self.weight
                r.metadata["stage"] = self.get_name()
                r.metadata["original_score"] = r.score / self.weight
            
            logger.info(f"GraphRetrievalStage: 检索到 {len(results)} 个结果")
            
            # 合并前序结果
            if previous_results:
                results = previous_results + results
            
            return results
            
        except Exception as e:
            logger.error(f"GraphRetrievalStage 执行失败: {e}", exc_info=True)
            
            # 失败时返回前序结果
            return previous_results if previous_results else []
    
    def get_name(self) -> str:
        return "GraphRetrieval"
