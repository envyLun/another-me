# AME (Another Me Engine)

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/yourusername/another-me)
[![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/architecture-3%20layers-orange.svg)](#架构设计)

**AME** 是一个独立的 AI 技术模块引擎，为智能个人助理系统提供核心功能支持。采用**三层架构**（Foundation → Capabilities → Services），实现混合存储（向量+图谱）和多场景应用。

## 🌟 核心特性

### 1. 三层架构设计
- **Foundation Layer**: 基础能力层（LLM、Storage、NLP、Inference）
- **Capabilities Layer**: 能力模块层（Memory、Retrieval、Analysis、Generation）
- **Services Layer**: 业务服务层（Conversation、Knowledge、Work、Life）

### 2. 混合存储架构
- **Faiss 向量存储**: 快速向量相似度检索
- **FalkorDB 图谱存储**: 长期知识图谱分析
- **SQLite 元数据存储**: 统一索引管理和快速查询

### 3. 服务层能力
- **MimicService**: 模仿用户语言风格生成内容
- **SearchService**: 智能文档检索服务
- **DocumentService**: 文档管理 CRUD 服务

### 4. 能力模块
- **ConversationFilter**: 智能对话过滤与分类
- **DataAnalyzer**: 数据分析与洞察生成
- **RAGGenerator**: 检索增强生成（RAG）
- **HybridRetriever**: 混合检索策略

## 📦 项目结构

```
ame/
├── foundation/              # 基础能力层
│   ├── inference/          # 级联推理框架
│   ├── llm/                # LLM 调用封装
│   ├── storage/            # 存储抽象（Vector/Graph/Metadata）
│   ├── embedding/          # Embedding 生成
│   ├── nlp/                # NLP 基础能力
│   │   ├── emotion/        # 情绪识别
│   │   └── ner/            # 命名实体识别
│   └── utils/              # 工具函数
├── capabilities/           # 能力模块层
│   ├── memory/             # 记忆管理
│   ├── retrieval/          # 混合检索
│   ├── intent/             # 意图识别
│   ├── analysis/           # 数据分析
│   └── generation/         # RAG 生成
├── services/               # 业务服务层
│   ├── conversation/       # 对话服务
│   ├── knowledge/          # 知识库服务
│   ├── work/               # 工作场景服务
│   └── life/               # 生活场景服务
├── models/                 # 数据模型
│   ├── domain.py           # 领域模型
│   └── report_models.py    # 报告模型
├── data_processor/         # 数据处理
├── retrieval/              # 检索模块（兼容层）
├── storage/                # 存储层（兼容层）
├── tests/                  # 测试代码
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── fixtures/           # 测试数据
├── __init__.py             # 模块导出
├── requirements.txt        # 依赖列表
└── setup.py               # 安装配置
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/yourusername/another-me.git
cd another-me/ame

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 spacy 中文模型（可选）
python -m spacy download zh_core_web_sm
```

### 2. 环境配置

创建 `.env` 文件：

```bash
# OpenAI API 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# FalkorDB 配置
FALKOR_HOST=localhost
FALKOR_PORT=6379
FALKOR_PASSWORD=

# 数据存储路径
DATA_PATH=/app/data
```

### 3. 基础使用示例

#### 3.1 HybridRepository - 混合存储

```python
from ame.repository.hybrid_repository import HybridRepository
from ame.storage.faiss_store import FaissStore
from ame.storage.falkor_store import FalkorStore
from ame.storage.metadata_store import MetadataStore
from ame.models.domain import Document, DocumentType
from datetime import datetime

# 初始化存储层
faiss_store = FaissStore(dimension=1536, index_path="data/faiss.index")
falkor_store = FalkorStore(host="localhost", port=6379)
metadata_store = MetadataStore(db_path="data/metadata.db")

# 创建混合仓库
repo = HybridRepository(
    faiss_store=faiss_store,
    falkor_store=falkor_store,
    metadata_store=metadata_store
)

# 创建文档
doc = Document(
    content="今天完成了项目设计文档，包含架构设计和接口定义",
    doc_type=DocumentType.WORK_LOG,
    source="daily_log",
    timestamp=datetime.now()
)

# 存储文档（自动双写到 Faiss 和 Falkor）
await repo.create(doc)

# 混合检索
results = await repo.hybrid_search(
    query="项目设计文档",
    top_k=5,
    faiss_weight=0.6,
    graph_weight=0.4
)
```

#### 3.2 WorkEngine - 工作场景

```python
from ame.engines.work_engine import WorkEngine
from ame.llm_caller.caller import LLMCaller
from datetime import datetime, timedelta

# 初始化工作引擎
llm_caller = LLMCaller(api_key="your_key")
work_engine = WorkEngine(
    repository=repo,
    llm_caller=llm_caller
)

# 生成周报
start_date = datetime.now() - timedelta(days=7)
end_date = datetime.now()
weekly_report = await work_engine.generate_weekly_report(
    user_id="user_001",
    start_date=start_date,
    end_date=end_date,
    style="professional"
)

print(weekly_report.content)

# 智能整理待办事项
todos = [
    "完成项目文档",
    "紧急：修复生产环境bug",
    "开会讨论下周计划",
    "学习新技术栈"
]
organized = await work_engine.organize_todos(todos)
print(organized.formatted_text)

# 会议总结
meeting_summary = await work_engine.summarize_meeting(
    meeting_content="会议讨论了项目进度和下一步计划...",
    meeting_date=datetime.now(),
    participants=["张三", "李四"]
)
print(meeting_summary["formatted_minutes"])
```

#### 3.3 LifeEngine - 生活场景

```python
from ame.engines.life_engine import LifeEngine

# 初始化生活引擎
life_engine = LifeEngine(
    repository=repo,
    llm_caller=llm_caller
)

# 心情分析
mood_analysis = await life_engine.analyze_mood(
    mood_entry="今天心情不太好，工作压力有点大",
    user_id="user_001",
    entry_time=datetime.now()
)
print(f"情绪类型: {mood_analysis.emotion_type}")
print(f"情绪强度: {mood_analysis.emotion_intensity}")
print(f"建议: {mood_analysis.suggestions}")

# 兴趣追踪
interest_report = await life_engine.track_interests(
    user_id="user_001",
    period_days=30
)
print(interest_report.report)

# 生活建议
suggestions = await life_engine.generate_life_suggestions(
    user_id="user_001",
    context="最近比较累，想要改善生活状态"
)
print(suggestions)
```

#### 3.4 MimicEngine - 模仿用户风格

```python
from ame.mem.mimic_engine import MimicEngine

# 初始化模仿引擎
mimic_engine = MimicEngine(llm_caller=llm_caller)

# 学习用户对话
await mimic_engine.learn_from_conversation(
    user_message="我觉得这个方案挺好的，简单实用",
    context="讨论项目方案"
)

# 生成用户风格的回复
response = await mimic_engine.generate_response(
    prompt="对这个技术方案的看法",
    temperature=0.8
)
print(response)

# 生成用户风格的周报
report = await mimic_engine.generate_styled_text(
    template="weekly_report",
    data={
        "key_tasks": ["完成项目设计", "修复bug"],
        "achievements": ["上线新功能"],
        "challenges": ["时间紧张"]
    },
    tone="professional"
)
print(report)
```

#### 3.5 RAG 知识库

```python
from ame.rag.knowledge_base import KnowledgeBase

# 初始化知识库
kb = KnowledgeBase(db_path="data/rag_vector_store")

# 添加文档
await kb.add_document(
    file_path="docs/project_design.pdf",
    metadata={"category": "design", "project": "project_a"}
)

# 添加文本
await kb.add_text(
    text="项目采用微服务架构，使用 Python + FastAPI 构建",
    source="manual_input",
    metadata={"category": "architecture"}
)

# 检索知识
results = await kb.search(
    query="微服务架构的设计",
    top_k=5
)
for result in results:
    print(f"Score: {result['score']:.2f}")
    print(f"Content: {result['content'][:100]}...")
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=ame --cov-report=html
```

## 📊 数据流架构

```
┌─────────────┐
│   用户输入   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│   场景引擎层            │
│  (Work/Life/Mimic)     │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  HybridRepository       │
│  (统一数据访问层)        │
└──┬────────────┬─────────┘
   │            │
   ▼            ▼
┌─────────┐  ┌─────────┐
│ Faiss   │  │ Falkor  │
│ (向量)  │  │ (图谱)  │
└─────────┘  └─────────┘
   │            │
   └────┬───────┘
        ▼
   ┌─────────┐
   │ SQLite  │
   │ (元数据) │
   └─────────┘
```

## 🔄 数据生命周期

AME 实现了三层数据管理策略：

- **热数据 (HOT)**: 0-7天，Faiss + Falkor + SQLite
- **温数据 (WARM)**: 7-30天，Faiss + Falkor + SQLite
- **冷数据 (COLD)**: 30天+，仅 Falkor + SQLite

定期执行 `lifecycle_management()` 自动降温：

```python
await repo.lifecycle_management()
```

## 🔌 API 导出

AME 导出以下核心模块：

```python
from ame import (
    # 数据处理
    DataProcessor, DataAnalyzer, AsyncDataProcessor,
    
    # 存储
    FaissStore, FalkorStore, MetadataStore,
    
    # LLM 调用
    LLMCaller,
    
    # RAG
    RAGGenerator, KnowledgeBase,
    
    # 检索
    RetrieverFactory, VectorRetriever, HybridRetriever,
    
    # 场景引擎
    WorkEngine, LifeEngine, MimicEngine, AnalyzeEngine,
    
    # 模型
    Document, DocumentType, SearchResult
)
```

## 🛠️ 配置选项

### LLM 配置

```python
llm_caller = LLMCaller(
    api_key="your_key",
    base_url="https://api.openai.com/v1",
    model="gpt-4",
    timeout=30.0,
    max_retries=3
)
```

### Faiss 配置

```python
faiss_store = FaissStore(
    dimension=1536,              # 向量维度
    index_path="data/faiss.index",
    metric="cosine",             # 距离度量（cosine/l2/ip）
    use_gpu=False               # 是否使用 GPU
)
```

### FalkorDB 配置

```python
falkor_store = FalkorStore(
    host="localhost",
    port=6379,
    password="",
    graph_name="ame_graph",
    max_connections=10
)
```

### 混合检索权重调优

```python
results = await repo.hybrid_search(
    query="查询文本",
    top_k=10,
    faiss_weight=0.6,    # 向量检索权重
    graph_weight=0.4     # 图谱检索权重
)
```

## 📈 性能优化建议

1. **批量写入**: 使用 `add_documents()` 批量添加文档
2. **异步处理**: 使用 `AsyncDataProcessor` 处理大量文件
3. **索引优化**: 定期执行 `faiss_store.optimize_index()`
4. **缓存策略**: 使用 Redis 缓存热点查询结果
5. **分布式部署**: Faiss 和 Falkor 可独立扩展

## 🔒 安全考虑

- API 密钥使用环境变量存储
- 敏感数据加密存储
- 定期备份 SQLite 和 Faiss 索引
- 访问控制和用户隔离

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 使用 Black 格式化代码
- 使用 MyPy 进行类型检查
- 编写单元测试（覆盖率 > 80%）
- 添加文档字符串

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📮 联系方式

- 项目主页: https://github.com/yourusername/another-me
- 问题反馈: https://github.com/yourusername/another-me/issues
- 邮箱: your.email@example.com

## 🙏 致谢

- [Faiss](https://github.com/facebookresearch/faiss) - 高效向量检索
- [FalkorDB](https://www.falkordb.com/) - 图数据库
- [OpenAI](https://openai.com/) - LLM API
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证

## 📝 更新日志

### v0.2.0 (2024-01-XX)
- 新增混合存储架构（Faiss + Falkor + SQLite）
- 新增 WorkEngine 和 LifeEngine 场景引擎
- 新增对话过滤功能（ConversationFilter）
- 优化 NER 实体识别（HybridNER）
- 完善测试覆盖率

### v0.1.0 (2023-12-XX)
- 初始版本发布
- 基础 RAG 功能
- MimicEngine 模仿引擎
- Faiss 向量存储

---

**Built with ❤️ by Another Me Team**
