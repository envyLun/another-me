# AME 架构设计

本文档详细介绍 AME (Another Me Engine) 的四层架构设计。

---

## 📋 目录

- [设计理念](#设计理念)
- [架构总览](#架构总览)
- [各层详解](#各层详解)
  - [Foundation Layer](#1-foundation-layer-基础层)
  - [Capabilities Layer](#2-capabilities-layer-能力层)
  - [Services Layer](#3-services-layer-服务层)
  - [Application Layer](#4-application-layer-应用层)
- [依赖注入模式](#依赖注入模式)
- [数据流转](#数据流转)
- [扩展性设计](#扩展性设计)

---

## 🎯 设计理念

AME 的架构设计遵循以下核心原则：

### 1. 单一职责原则 (SRP)
每一层都有明确的职责边界，不跨层处理逻辑。

### 2. 依赖倒置原则 (DIP)
- 高层模块不依赖低层模块，都依赖抽象
- Service 层依赖 CapabilityFactory，而非具体实现

### 3. 开闭原则 (OCP)
- 对扩展开放：可轻松添加新能力、新服务
- 对修改封闭：核心架构保持稳定

### 4. 接口隔离原则 (ISP)
每个能力提供最小化的接口，避免臃肿。

### 5. 可测试性优先
- 每层都可独立测试
- 使用依赖注入，便于 Mock

---

## 🏗️ 架构总览

```
┌──────────────────────────────────────────────────────────────┐
│                    Application Layer                          │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  FastAPI     │  │     CLI      │  │     SDK      │       │
│  │   Backend    │  │    Tools     │  │   Library    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                     Services Layer                            │
│                                                                │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐      │
│  │ Conversation  │ │   Knowledge   │ │     Life      │      │
│  │   Services    │ │   Services    │ │   Services    │      │
│  │ • MimicService│ │ • SearchService│ │• MoodService │      │
│  └───────────────┘ └───────────────┘ │• InterestSvc │      │
│                                       └───────────────┘      │
│  ┌───────────────┐                                           │
│  │     Work      │                                           │
│  │   Services    │                                           │
│  │ • ReportService│                                          │
│  │ • TodoService │                                           │
│  └───────────────┘                                           │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                   Capabilities Layer                          │
│                                                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│  │ Retrieval  │ │  Analysis  │ │ Generation │ │  Memory  │ │
│  │            │ │            │ │            │ │          │ │
│  │• Hybrid    │ │• Data      │ │• RAG       │ │• Manager │ │
│  │  Retriever │ │  Analyzer  │ │  Generator │ │• Filter  │ │
│  │• Pipeline  │ │• Insight   │ │• Style     │ │          │ │
│  │            │ │  Generator │ │  Generator │ │          │ │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘ │
│                                                                │
│  ┌────────────┐                 ┌──────────────────────────┐ │
│  │   Intent   │                 │   CapabilityFactory      │ │
│  │ Recognizer │                 │   (依赖注入管理)          │ │
│  └────────────┘                 └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    Foundation Layer                           │
│                                                                │
│  ┌──────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │ LLM  │ │Embedding │ │ Storage │ │   NLP   │ │ Utils   │ │
│  │      │ │          │ │         │ │         │ │         │ │
│  │• API │ │• OpenAI  │ │• Vector │ │• NER    │ │• Text   │ │
│  │ Call │ │  Embed   │ │• Graph  │ │• Emotion│ │  Utils  │ │
│  │• Cache│ │          │ │• Doc    │ │         │ │• Time   │ │
│  └──────┘ └──────────┘ └─────────┘ └─────────┘ └─────────┘ │
│                                                                │
│  ┌──────────────┐                                             │
│  │  Inference   │                                             │
│  │  (级联推理)   │                                             │
│  └──────────────┘                                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 📚 各层详解

### 1. Foundation Layer (基础层)

**职责**: 提供原子化的技术能力，无业务逻辑。

#### 1.1 核心模块

| 模块 | 职责 | 示例 |
|------|------|------|
| **LLM** | LLM 调用封装 | `OpenAICaller` |
| **Embedding** | 文本向量化 | `OpenAIEmbedding` |
| **Storage** | 数据存储接口 | `VectorStore`, `GraphStore`, `DocumentStore` |
| **NLP** | 基础 NLP 能力 | `NER`, `EmotionDetector` |
| **Inference** | 级联推理引擎 | `CascadeInferenceEngine` |
| **Utils** | 工具函数 | `TextProcessor`, `TimeUtils` |

#### 1.2 设计特点

- ✅ **独立性**: 每个模块可独立使用
- ✅ **可测试**: 100% 单元测试覆盖
- ✅ **接口清晰**: 提供抽象基类 (`LLMCallerBase`, `EmbeddingBase` 等)
- ✅ **无业务逻辑**: 只提供技术能力

#### 1.3 示例代码

```python
from ame.foundation.llm import OpenAICaller

# 直接使用基础能力
llm = OpenAICaller(api_key="sk-...", model="gpt-4")
response = await llm.generate(
    messages=[{"role": "user", "content": "Hello"}]
)
```

📖 [Foundation Layer 详细文档](../../foundation/README.md)

---

### 2. Capabilities Layer (能力层)

**职责**: 组合基础能力，提供高级功能。

#### 2.1 核心能力

| 能力 | 组合的基础能力 | 功能 |
|------|----------------|------|
| **HybridRetriever** | Embedding + VectorStore + GraphStore + NER | 混合检索 (向量+图谱) |
| **DataAnalyzer** | LLM + Retriever | 数据统计、趋势分析 |
| **InsightGenerator** | LLM | 洞察提取 |
| **RAGGenerator** | Retriever + LLM | RAG 问答生成 |
| **StyleGenerator** | LLM + Retriever | 风格化文本生成 |
| **MemoryManager** | DocumentStore + VectorStore + Embedding | 记忆存储与管理 |
| **IntentRecognizer** | LLM + Embedding | 意图识别 |

#### 2.2 CapabilityFactory (能力工厂)

能力工厂负责**统一管理依赖注入**，避免重复创建实例。

```python
from ame.capabilities import CapabilityFactory

# 创建工厂（注入所有 Foundation 层依赖）
factory = CapabilityFactory(
    llm_caller=llm,
    embedding_function=embedding,
    vector_store=vector_store,
    graph_store=graph_store,
    document_store=document_store,
    ner_service=ner
)

# 通过工厂创建能力
retriever = factory.create_retriever(
    pipeline_mode="advanced",
    cache_key="my_retriever"  # 使用缓存，避免重复创建
)

analyzer = factory.create_data_analyzer(
    with_retriever=True,
    cache_key="my_analyzer"
)
```

#### 2.3 Pipeline 模式

检索系统采用 **Pipeline 模式**，支持灵活组合检索阶段：

```python
# 基础管道 (仅向量检索)
retriever = factory.create_retriever(pipeline_mode="basic")

# 高级管道 (向量 + 图谱 + 重排序)
retriever = factory.create_retriever(pipeline_mode="advanced")

# 语义管道 (意图自适应 + 多样性 + 融合)
retriever = factory.create_retriever(pipeline_mode="semantic")
```

📖 [Capabilities Layer 详细文档](../../capabilities/README.md)

---

### 3. Services Layer (服务层)

**职责**: 封装业务逻辑，提供场景化服务。

#### 3.1 服务分类

| 服务分类 | 具体服务 | 职责 |
|----------|----------|------|
| **Conversation** | `MimicService` | 智能对话、风格模仿 |
| **Knowledge** | `SearchService`, `DocumentService` | 知识检索、文档管理 |
| **Life** | `MoodService`, `InterestService`, `MemoryService` | 情绪追踪、兴趣发现、记忆时间线 |
| **Work** | `ReportService`, `TodoService`, `MeetingService`, `ProjectService` | 工作报告、待办管理、会议纪要、项目追踪 |

#### 3.2 依赖注入规范

**所有 Service 层必须遵循以下规范**：

✅ **正确做法**:
```python
class MyService:
    def __init__(self, capability_factory: CapabilityFactory):
        self.factory = capability_factory
        self.llm = factory.llm
        self.retriever = factory.create_retriever(cache_key="my_retriever")
```

❌ **错误做法**:
```python
# 禁止在 Service 内部创建 Factory
class MyService:
    def __init__(self, llm, embedding, vector_store, ...):
        self.factory = CapabilityFactory(...)  # ❌
```

#### 3.3 示例代码

```python
from ame.services.conversation import MimicService

# 创建服务（注入工厂）
mimic_service = MimicService(capability_factory=factory)

# 使用服务
response = await mimic_service.chat(
    user_message="你好",
    context={"user_id": "user_123"}
)
```

📖 [Services Layer 详细文档](../../services/README.md)

---

### 4. Application Layer (应用层)

**职责**: 对外接口，集成各种服务。

#### 4.1 应用形式

| 应用 | 技术栈 | 用途 |
|------|--------|------|
| **FastAPI Backend** | FastAPI + Uvicorn | REST API 服务 |
| **CLI Tools** | Click / Typer | 命令行工具 |
| **SDK Library** | Python Package | Python SDK |

#### 4.2 FastAPI 集成示例

```python
from fastapi import FastAPI, Depends
from ame.capabilities import CapabilityFactory
from ame.services.conversation import MimicService

app = FastAPI()

# 全局工厂（单例）
def get_capability_factory() -> CapabilityFactory:
    return CapabilityFactory(...)

# 服务依赖注入
def get_mimic_service(
    factory: CapabilityFactory = Depends(get_capability_factory)
) -> MimicService:
    return MimicService(capability_factory=factory)

# API 路由
@app.post("/api/chat")
async def chat(
    user_message: str,
    service: MimicService = Depends(get_mimic_service)
):
    response = await service.chat(user_message)
    return response
```

---

## 🔗 依赖注入模式

AME 使用 **CapabilityFactory** 实现依赖注入，解决以下问题：

### 问题

传统方式需要在 Service 层传递大量参数：

```python
# ❌ 参数过多，难以维护
service = MimicService(
    llm=llm,
    embedding=embedding,
    vector_store=vector_store,
    graph_store=graph_store,
    ner=ner,
    document_store=document_store
)
```

### 解决方案

使用 CapabilityFactory 统一管理：

```python
# ✅ 简洁清晰
factory = CapabilityFactory(
    llm_caller=llm,
    embedding_function=embedding,
    vector_store=vector_store,
    # ... 其他依赖
)

service = MimicService(capability_factory=factory)
```

### 优势

1. **集中管理**: 所有依赖在 Factory 层统一配置
2. **能力复用**: 通过 `cache_key` 复用实例
3. **易于测试**: 只需 Mock Factory 一个对象
4. **降低耦合**: Service 层不关心底层实现

---

## 🔄 数据流转

### 1. 用户请求流程

```
用户请求
    ↓
Application Layer (FastAPI)
    ↓
Services Layer (MimicService)
    ↓
Capabilities Layer (HybridRetriever, StyleGenerator)
    ↓
Foundation Layer (LLM, VectorStore)
    ↓
返回结果
```

### 2. 具体示例：智能对话

```
用户: "帮我总结一下上周的工作"
    ↓
FastAPI: POST /api/chat
    ↓
MimicService.chat()
    ├─ 1. 内容安全检测 (LLM)
    ├─ 2. 意图识别 (IntentRecognizer) → "分析"
    ├─ 3. 检索相关记忆 (HybridRetriever)
    ├─ 4. 数据分析 (DataAnalyzer)
    ├─ 5. 生成报告 (StyleGenerator)
    └─ 6. 保存对话记忆 (MemoryManager)
    ↓
返回结果: "上周你完成了..."
```

---

## 🚀 扩展性设计

### 1. 添加新的基础能力

```python
# 1. 在 Foundation Layer 创建新模块
from ame.foundation.base import BaseCapability

class MyNewCapability(BaseCapability):
    async def process(self, input_data):
        # 实现逻辑
        pass

# 2. 在 CapabilityFactory 中注册
class CapabilityFactory:
    def create_my_capability(self, cache_key: Optional[str] = None):
        # ...
        pass
```

### 2. 添加新的组合能力

```python
# 在 Capabilities Layer 创建新能力
class MyComplexCapability:
    def __init__(
        self,
        llm: LLMCallerBase,
        retriever: HybridRetriever,
        analyzer: DataAnalyzer
    ):
        self.llm = llm
        self.retriever = retriever
        self.analyzer = analyzer
    
    async def execute(self, input_data):
        # 组合使用多个基础能力
        pass
```

### 3. 添加新的服务

```python
# 在 Services Layer 创建新服务
class MyNewService:
    def __init__(self, capability_factory: CapabilityFactory):
        self.factory = capability_factory
        self.llm = factory.llm
        self.retriever = factory.create_retriever(cache_key="my_retriever")
    
    async def my_business_logic(self, params):
        # 实现业务逻辑
        pass
```

---

## 📊 架构对比

### 旧架构 (双层引擎)

```
Application
    ↓
Engine (RAG / MEM)
    ↓
Foundation
```

**问题**:
- ❌ 职责不清晰
- ❌ 业务逻辑与技术能力耦合
- ❌ 难以复用和测试

### 新架构 (四层架构)

```
Application
    ↓
Services
    ↓
Capabilities
    ↓
Foundation
```

**优势**:
- ✅ 职责清晰
- ✅ 高度可复用
- ✅ 易于测试
- ✅ 便于扩展

---

## 🎯 总结

AME 的四层架构设计实现了：

1. **清晰的职责分离**: 每一层都有明确的职责
2. **高度的可复用性**: Foundation 和 Capabilities 可独立使用
3. **强大的扩展性**: 可轻松添加新能力和新服务
4. **优秀的可测试性**: 依赖注入使得每层都可独立测试
5. **良好的可维护性**: 模块化设计降低维护成本

这种设计为构建复杂的 AI 应用提供了坚实的基础。

---

## 📖 相关文档

- [开发指南](DEVELOPMENT.md)
- [API 参考](API_REFERENCE.md)
- [部署指南](DEPLOYMENT.md)
