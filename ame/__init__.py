"""
AME - Another Me Engine
独立的算法能力引擎，提供检索、分析、生成等核心能力

架构：Foundation (基础能力层) → Capabilities (能力模块层) → Services (业务服务层)
"""

__version__ = "0.3.0"
__author__ = "Another Me Team"

# ========== Foundation Layer (基础能力层) ==========
# Inference - 推理框架
from .foundation.inference import (
    CascadeInferenceEngine,
    InferenceLevelBase,
    InferenceResult,
    InferenceLevel,
    create_rule_level,
    create_llm_level,
)

# LLM - LLM 调用
from .foundation.llm import (
    LLMCallerBase,
    LLMResponse,
    OpenAICaller,
)

# Storage - 存储能力
from .foundation.storage import (
    StorageBase,
    VectorStore,
    GraphStore,
    MetadataStore,
    DocumentStore,
)

# NLP - NLP 基础能力
from .foundation.nlp.emotion import (
    EmotionDetectorBase,
    EmotionResult,
    EmotionType,
    RuleEmotionDetector,
    LLMEmotionDetector,
    HybridEmotionDetector,
)

from .foundation.nlp.ner import (
    NERBase,
    HybridNER,
    Entity,
)

# ========== Capabilities Layer (能力模块层) ==========
# Memory - 记忆管理
from .capabilities.memory import (
    MemoryBase,
    MemoryItem,
    MemoryManager,
    ConversationFilter,
)

# Retrieval - 混合检索
from .capabilities.retrieval import (
    RetrieverBase as CapRetrieverBase,
    RetrievalResult as CapRetrievalResult,
    HybridRetriever,
)

# Intent - 意图识别
from .capabilities.intent import (
    IntentRecognizerBase,
    IntentResult,
    UserIntent,
    IntentRecognizer,
)

# Analysis - 数据分析
from .capabilities.analysis import (
    DataAnalyzer,
    InsightGenerator,
)

# Generation - RAG 生成
from .capabilities.generation import (
    RAGGenerator,
)

# ========== Services Layer (业务服务层) ==========
# Conversation Services
from .services.conversation import (
    MimicService,
)

# Knowledge Services
from .services.knowledge import (
    SearchService,
    DocumentService,
)

# ========== 旧模块（兼容性，将逐步废弃）==========
from .data_processor.processor import DataProcessor
from .data_processor.base import DataProcessorBase, ProcessedData
from .data_processor.document_processor import DocumentProcessor

# Storage (旧模块，使用 foundation.storage 替代)
from .storage.falkor_store import FalkorStore
from .storage.metadata_store import MetadataStore

# 旧的 RAG (使用 capabilities.generation.RAGGenerator 替代)

from .retrieval.factory import RetrieverFactory
from .retrieval.base import RetrieverBase, RetrievalResult
from .retrieval.vector_retriever import VectorRetriever
from .retrieval.pipeline import RetrievalPipeline
from .retrieval.reranker import Reranker, LLMReranker, RerankerBase

# 导出引擎层 (待 Phase 3 重构)
# from .engines.work_engine import WorkEngine
# from .engines.life_engine import LifeEngine
# from .mem.mimic_engine import MimicEngine
# from .mem.analyze_engine import AnalyzeEngine

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
    # ========== Foundation Layer ==========
    # Inference
    "CascadeInferenceEngine",
    "InferenceLevelBase",
    "InferenceResult",
    "InferenceLevel",
    "create_rule_level",
    "create_llm_level",
    
    # LLM
    "OpenAICaller",
    "LLMCallerBase",
    "LLMResponse",
    
    # Storage
    "StorageBase",
    "VectorStore",
    "GraphStore",
    "MetadataStore",
    "DocumentStore",
    
    # NLP - Emotion
    "EmotionDetectorBase",
    "EmotionResult",
    "EmotionType",
    "RuleEmotionDetector",
    "LLMEmotionDetector",
    "HybridEmotionDetector",
    
    # NLP - NER
    "NERBase",
    "HybridNER",
    "Entity",
    
    # ========== Capabilities Layer ==========
    # Memory
    "MemoryBase",
    "MemoryItem",
    "MemoryManager",
    "ConversationFilter",
    
    # Retrieval (Capabilities)
    "CapRetrieverBase",
    "CapRetrievalResult",
    "HybridRetriever",
    
    # Intent
    "IntentRecognizerBase",
    "IntentResult",
    "UserIntent",
    "IntentRecognizer",
    
    # Analysis
    "DataAnalyzer",
    "InsightGenerator",
    
    # Generation
    "RAGGenerator",
    
    # ========== Services Layer ==========
    # Conversation
    "MimicService",
    
    # Knowledge
    "SearchService",
    "DocumentService",
    
    # ========== 旧模块（兼容性） ==========
    # Data Processor (旧模块)
    "DataProcessor",
    "DataProcessorBase",
    "ProcessedData",
    "DocumentProcessor",
    
    # Storage (旧模块，使用 foundation.storage 替代)
    "FaissStore",
    "FalkorStore",
    "MetadataStore",
    
    # Retrieval
    "RetrieverFactory",
    "RetrieverBase",
    "RetrievalResult",
    "VectorRetriever",
    "RetrievalPipeline",
    "Reranker",
    "LLMReranker",
    "RerankerBase",
    
    # 场景引擎 (待 Phase 3 重构)
    # "WorkEngine",
    # "LifeEngine",
    # 核心引擎
    # "MimicEngine",
    # "AnalyzeEngine",
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
