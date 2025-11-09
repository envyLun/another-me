"""
检索模块 - 支持多种复杂召回策略

重构后版本：
- 移除 HybridRetriever（已废弃，使用 Pipeline 替代）
- 统一使用 RetrieverFactory.create_pipeline()
"""

from .base import RetrieverBase
from .vector_retriever import VectorRetriever
from .graph_retriever import GraphRetriever
from .reranker import Reranker, RerankerBase
from .pipeline import RetrievalPipeline
from .factory import RetrieverFactory

__all__ = [
    "RetrieverBase",
    "VectorRetriever",
    "GraphRetriever",
    "Reranker",
    "RerankerBase",
    "RetrievalPipeline",
    "RetrieverFactory",
]
