"""
检索器工厂 - 创建和配置检索管道

重构后版本：
- 移除 HybridRetriever（已废弃）
- 统一使用 Pipeline 模式
- 提供 basic/advanced/semantic 预设配置
"""

from typing import Optional
from .vector_retriever import VectorRetriever
from .graph_retriever import GraphRetriever
from .pipeline import RetrievalPipeline
from .stages import (
    VectorRetrievalStage,
    GraphRetrievalStage,
    FusionStage,
    IntentAdaptiveStage,
    SemanticRerankStage,
    DiversityFilterStage
)
from ame.foundation.storage import VectorStore as FaissStore
from ame.foundation.storage import GraphStore as FalkorStore


class RetrieverFactory:
    """检索器工厂类（重构后：统一使用 Pipeline）"""
    
    @staticmethod
    def create_pipeline(
        preset: str = "basic",
        vector_store: FaissStore = None,
        graph_store: Optional[FalkorStore] = None,
        llm_caller=None,
        ner_extractor=None,
        **kwargs
    ) -> RetrievalPipeline:
        """
        创建检索管道（统一入口）
        
        Args:
            preset: 预设配置类型
                - basic: 基础管道（向量检索 + 重排序）
                - advanced: 高级管道（向量 + 图谱 + 融合 + 重排序）
                - semantic: 语义管道（向量 + 意图自适应 + 多样性）
            vector_store: Faiss 向量存储（必需）
            graph_store: Falkor 图谱存储（可选）
            llm_caller: LLM 调用器（可选）
            ner_extractor: NER 提取器（可选）
            **kwargs: 其他参数
                - vector_weight: 向量权重（默认 0.6）
                - graph_weight: 图谱权重（默认 0.4）
                - lambda_param: MMR 多样性参数（默认 0.7）
                - enable_multi_hop: 启用多跳推理（默认 False）
                - max_hops: 最大跳数（默认 2）
        
        Returns:
            pipeline: 检索管道实例
        
        Raises:
            ValueError: 未知的预设类型
        """
        if not vector_store:
            raise ValueError("vector_store is required")
        
        if preset == "basic":
            return RetrieverFactory._create_basic_pipeline(
                vector_store, llm_caller, **kwargs
            )
        elif preset == "advanced":
            return RetrieverFactory._create_advanced_pipeline(
                vector_store, graph_store, llm_caller, ner_extractor, **kwargs
            )
        elif preset == "semantic":
            return RetrieverFactory._create_semantic_pipeline(
                vector_store, llm_caller, ner_extractor, **kwargs
            )
        else:
            raise ValueError(
                f"Unknown preset: {preset}. "
                f"Available: basic, advanced, semantic"
            )
    
    @staticmethod
    def _create_basic_pipeline(
        vector_store: FaissStore,
        llm_caller=None,
        **kwargs
    ) -> RetrievalPipeline:
        """
        基础管道：向量检索 + 重排序
        
        适用场景：
        - 简单查询场景
        - 无图谱数据
        - 对速度要求高
        """
        vector_retriever = VectorRetriever(vector_store)
        
        pipeline = RetrievalPipeline(name="basic")
        pipeline\
            .add_stage(VectorRetrievalStage(vector_retriever))\
            .add_stage(SemanticRerankStage(llm_caller, use_llm=False))
        
        return pipeline
    
    @staticmethod
    def _create_advanced_pipeline(
        vector_store: FaissStore,
        graph_store: Optional[FalkorStore],
        llm_caller,
        ner_extractor,
        **kwargs
    ) -> RetrievalPipeline:
        """
        高级管道：向量 + 图谱 + 融合 + 重排序
        
        适用场景：
        - 复杂查询场景
        - 有图谱数据支持
        - 需要高召回率和准确性
        """
        vector_retriever = VectorRetriever(vector_store)
        
        vector_weight = kwargs.get("vector_weight", 0.6)
        graph_weight = kwargs.get("graph_weight", 0.4)
        enable_multi_hop = kwargs.get("enable_multi_hop", False)
        max_hops = kwargs.get("max_hops", 2)
        
        pipeline = RetrievalPipeline(name="advanced")
        pipeline.add_stage(VectorRetrievalStage(vector_retriever, weight=vector_weight))
        
        # 添加图谱检索阶段（如果可用）
        if graph_store and ner_extractor:
            graph_retriever = GraphRetriever(
                graph_store,
                ner_extractor,
                enable_multi_hop=enable_multi_hop,
                max_hops=max_hops
            )
            pipeline.add_stage(GraphRetrievalStage(graph_retriever, weight=graph_weight))
            pipeline.add_stage(FusionStage(fusion_method="rrf"))
        
        # 重排序
        pipeline.add_stage(SemanticRerankStage(llm_caller, use_llm=False))
        
        return pipeline
    
    @staticmethod
    def _create_semantic_pipeline(
        vector_store: FaissStore,
        llm_caller,
        ner_extractor,
        **kwargs
    ) -> RetrievalPipeline:
        """
        语义管道：向量 + 意图自适应 + 多样性
        
        适用场景：
        - 需要理解用户意图
        - 结果多样性要求高
        - 无图谱数据或图谱数据质量不高
        """
        vector_retriever = VectorRetriever(vector_store)
        
        lambda_param = kwargs.get("lambda_param", 0.7)
        
        pipeline = RetrievalPipeline(name="semantic")
        pipeline\
            .add_stage(VectorRetrievalStage(vector_retriever))\
            .add_stage(IntentAdaptiveStage(ner_extractor))\
            .add_stage(SemanticRerankStage(llm_caller, use_llm=False))\
            .add_stage(DiversityFilterStage(lambda_param=lambda_param))
        
        return pipeline
