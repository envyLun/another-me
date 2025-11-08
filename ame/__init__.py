"""
AME - Another Me Engine
独立的技术模块引擎，提供数据处理、向量存储、LLM调用、RAG生成等核心功能
"""

__version__ = "0.2.0"
__author__ = "Another Me Team"

# 导出核心模块
from .data_processor.processor import DataProcessor
from .data_processor.analyzer import DataAnalyzer
from .data_processor.async_processor import AsyncDataProcessor
from .data_processor.base import DataProcessorBase, ProcessedData

from .storage.faiss_store import FaissStore
from .storage.falkor_store import FalkorStore
from .storage.metadata_store import MetadataStore

from .llm_caller.caller import LLMCaller
from .llm_caller.base import LLMCallerBase, LLMResponse

from .rag_generator.generator import RAGGenerator

from .retrieval.factory import RetrieverFactory
from .retrieval.base import RetrieverBase, RetrievalResult
from .retrieval.vector_retriever import VectorRetriever
from .retrieval.hybrid_retriever import HybridRetriever
from .retrieval.reranker import Reranker, LLMReranker, RerankerBase

# 导出引擎层
from .engines.work_engine import WorkEngine
from .engines.life_engine import LifeEngine
from .mem.mimic_engine import MimicEngine
from .mem.analyze_engine import AnalyzeEngine

# 导出模型
from .models.domain import (
    Document,
    DocumentType,
    DataLayer,
    MemoryRetentionType,
    DocumentStatus,
    SearchResult,
)

from .models.report_models import (
    WeeklyReport,
    DailyReport,
    TaskSummary,
    Achievement,
    OrganizedTodos,
    TaskInfo,
    ProjectProgress,
    MoodAnalysis,
    EmotionResult,
    MoodTrend,
    InterestReport,
    InterestTopic,
)

__all__ = [
    # Data Processor
    "DataProcessor",
    "DataAnalyzer",
    "AsyncDataProcessor",
    "DataProcessorBase",
    "ProcessedData",
    
    # Storage
    "FaissStore",
    "FalkorStore",
    "MetadataStore",
    
    # LLM Caller
    "LLMCaller",
    "LLMCallerBase",
    "LLMResponse",
    
    # RAG Generator
    "RAGGenerator",
    
    # Retrieval
    "RetrieverFactory",
    "RetrieverBase",
    "RetrievalResult",
    "VectorRetriever",
    "HybridRetriever",
    "Reranker",
    "LLMReranker",
    "RerankerBase",
    
    # 场景引擎
    "WorkEngine",
    "LifeEngine",
    # 核心引擎
    "MimicEngine",
    "AnalyzeEngine",
    # 域模型
    "Document",
    "DocumentType",
    "DataLayer",
    "MemoryRetentionType",
    "DocumentStatus",
    "SearchResult",
    # 报告模型
    "WeeklyReport",
    "DailyReport",
    "TaskSummary",
    "Achievement",
    "OrganizedTodos",
    "TaskInfo",
    "ProjectProgress",
    "MoodAnalysis",
    "EmotionResult",
    "MoodTrend",
    "InterestReport",
    "InterestTopic",
]
