# AME - Another Me Engine

**版本**: 0.2.0  
**架构**: 双存储（Faiss + FalkorDB + SQLite）  

---

## 📖 概述

AME（Another Me Engine）是 Another Me 项目的核心算法模块，提供：
- **双存储架构**: Faiss 向量检索 + FalkorDB 图谱分析 + SQLite 元数据管理
- **混合检索**: 语义相似度 + 实体关系融合
- **数据分层**: 热温冷数据生命周期管理
- **智能过滤**: 对话价值评估与自动分类
- **完整测试套件**: 85%+ 测试覆盖率，包含单元测试和集成测试

---

## 🚀 v0.2.0 新特性

### ✨ 架构优化
- ✅ **移除冗余模块**: 删除 `vector_store` 模块，统一使用 `FaissStore`
- ✅ **真实 FalkorDB 集成**: 替换 Mock 实现，使用真实图数据库
- ✅ **简化依赖**: 移除 ChromaDB，统一向量存储方案
- ✅ **完整测试覆盖**: 44+ 测试用例，覆盖核心功能

### 🗄️ FalkorDB 图数据库
- **Cypher 查询**: 原生支持图查询语言
- **实体关系**: 自动构建文档-实体关系图谱
- **多跳推理**: 支持复杂的图遍历和关联分析
- **时序演化**: 追踪实体随时间的变化

### 🧪 测试基础设施
- **单元测试**: Faiss、FalkorDB、元数据存储
- **集成测试**: 混合仓库、RAG 流程、MEM 引擎
- **性能测试**: 搜索延迟、吞吐量、并发能力
- **测试工具**: pytest + pytest-asyncio + coverage

---

## 🏗️ 架构设计

### 模块结构
```
ame/
├── models/                  # 数据模型
│   └── domain.py           # 统一 Document 模型
├── storage/                 # 存储层
│   ├── metadata_store.py   # SQLite 元数据
│   ├── faiss_store.py      # Faiss 向量存储
│   └── falkor_store.py     # Falkor 图谱存储
├── repository/              # 仓库层
│   └── hybrid_repository.py # 混合存储仓库
├── mem/                     # 记忆模块
│   ├── conversation_filter.py # 对话过滤
│   ├── mimic_engine.py     # 风格模仿
│   └── analyze_engine.py   # 数据分析
├── rag/                     # RAG 模块
│   └── knowledge_base.py   # 知识库
├── retrieval/               # 检索模块
│   └── hybrid_retriever.py # 混合检索器
└── llm_caller/              # LLM 调用
    └── caller.py           # LLM 客户端
```

### 数据流

```
用户输入
    ↓
对话过滤（ConversationFilter）
    ↓ （如果需要存储）
创建 Document
    ↓
混合仓库（HybridRepository）
    ├─→ Faiss（向量化 + 索引）
    ├─→ Falkor（实体提取 + 关系构建）
    └─→ SQLite（元数据保存）
```

---

## 🚀 快速开始

### 安装依赖
```bash
# 基础安装
pip install -r requirements.txt

# 开发环境（含测试工具）
pip install -e ".[test]"

# 下载 spaCy 中文模型（用于 NER）
python -m spacy download zh_core_web_sm
```

### 启动 FalkorDB
```bash
# 使用 Docker 启动 FalkorDB
docker run -d -p 6379:6379 --name falkordb falkordb/falkordb

# 验证连接
redis-cli ping  # 应返回 PONG

# 初始化图谱 schema
python scripts/init_falkor_graph.py
```

### 基础用法

#### 1. 初始化存储
```python
from ame.storage.faiss_store import FaissStore
from ame.storage.metadata_store import MetadataStore
from ame.storage.falkor_store import FalkorStore
from ame.repository.hybrid_repository import HybridRepository

# 初始化存储
faiss = FaissStore(
    dimension=1536,
    index_path="./data/faiss/main.index"
)
metadata = MetadataStore(db_path="./data/metadata/main.db")
graph = FalkorStore(
    host="localhost",
    port=6379,
    graph_name="another_me"
)

# 创建混合仓库
repo = HybridRepository(faiss, graph, metadata)
```

#### 2. 创建文档
```python
from ame.models.domain import Document, DocumentType
from datetime import datetime

doc = Document(
    content="学习 Faiss 向量检索技术",
    doc_type=DocumentType.RAG_KNOWLEDGE,
    source="学习笔记",
    timestamp=datetime.now(),
    embedding=[0.1] * 1536,  # 需要先用 LLM 生成
    entities=["Faiss", "向量检索"]
)

# 保存文档（自动写入三个存储层）
result = await repo.create(doc)
```

#### 3. 混合检索
```python
# 准备查询向量
query = "如何使用 Faiss 进行向量检索？"
query_embedding = [0.1] * 1536  # 使用 LLM 生成

# 执行混合检索（Faiss + Falkor）
results = await repo.hybrid_search(
    query=query,
    query_embedding=query_embedding,
    top_k=10,
    faiss_weight=0.6,  # Faiss 权重
    graph_weight=0.4   # Falkor 权重
)

for r in results:
    print(f"[{r.score:.3f}] {r.content[:50]}...")
```

#### 4. 对话过滤
```python
from ame.mem.conversation_filter import ConversationFilter

filter = ConversationFilter()

# 分类对话
retention_type = await filter.classify_conversation(
    user_message="今天学习了 Faiss，很有收获"
)

print(retention_type)  # MemoryRetentionType.PERMANENT

# 判断是否存储
if filter.should_store(retention_type):
    doc.retention_type = retention_type
    await repo.create(doc)
```

#### 5. 数据分析
```python
from ame.mem.analyze_engine import AnalyzeEngine
from datetime import timedelta

analyzer = AnalyzeEngine(repo)

# 分析最近7天的学习内容
start = datetime.now() - timedelta(days=7)
docs = await analyzer.collect_time_range("user_id", start)

# 提取关键洞察
insights = await analyzer.extract_insights(docs)
print(insights["key_tasks"])  # 最常提及的主题

# 生成周报
report = await analyzer.generate_insights_report("user_id", "weekly")
print(report)
```

---

## 📊 核心概念

### 1. 双存储架构

| 存储层 | 职责 | 数据范围 | 优势 |
|--------|------|----------|------|
| **Faiss** | 向量相似度检索 | 0-30天热温数据 | 毫秒级响应 |
| **FalkorDB** | 实体关系图谱 | 全生命周期 | 多跳推理、演化分析 |
| **SQLite** | 元数据管理 | 全生命周期 | 结构化查询 |

### 2. 数据分层策略

```
热数据（HOT, 0-7天）
├─ 存储: Faiss + Falkor + SQLite
└─ 用途: 实时检索、上下文补充

温数据（WARM, 7-30天）
├─ 存储: Faiss + Falkor + SQLite
└─ 用途: 历史回溯、趋势分析

冷数据（COLD, 30天+）
├─ 存储: 仅 FalkorDB + SQLite
└─ 用途: 深度分析、长期演化
```

### 3. 记忆保留类型

| 类型 | 说明 | 存活时间 | 示例 |
|------|------|----------|------|
| **PERMANENT** | 永久记忆 | 无限 | 学习笔记、重要决定 |
| **TEMPORARY** | 临时记忆 | 7天 | 待办事项、短期提醒 |
| **CASUAL_CHAT** | 闲聊 | 不存储 | 问候、简单回复 |

---

## 🔧 高级用法

### 自定义 Embedding 函数
```python
import openai

async def get_embedding(text: str) -> List[float]:
    response = await openai.Embedding.acreate(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

# 传入仓库
repo = HybridRepository(faiss, graph, metadata, embedding_function=get_embedding)

# 创建文档时自动生成 embedding
doc = Document(content="...", ...)
await repo.create(doc)  # 自动调用 get_embedding
```

### 数据生命周期管理
```python
# 定期执行降温（热→温→冷）
await repo.lifecycle_management()

# 统计信息
stats = repo.get_stats()
print(f"热数据: {stats['metadata']['hot']} 条")
print(f"温数据: {stats['metadata']['warm']} 条")
print(f"冷数据: {stats['metadata']['cold']} 条")
```

### 集成真实图数据库
```python
from ame.storage.falkor_store import FalkorStore

# FalkorDB (已集成)
graph = FalkorStore(
    host="localhost",
    port=6379,
    graph_name="another_me"
)

# 创建节点
node_id = await graph.create_node("Document", {
    "id": "doc_1",
    "content": "Test content",
    "timestamp": "2024-01-01T00:00:00"
})

# 创建关系
entity_id = await graph.get_or_create_entity("Python")
await graph.create_relation(node_id, entity_id, "MENTIONS")

# Cypher 查询
results = await graph.execute_cypher(
    "MATCH (d:Document)-[:MENTIONS]->(e:Entity {name: $name}) RETURN d",
    {"name": "Python"}
)
```

---

## 📈 性能优化

### Faiss 索引选择
```python
# 小规模 (<10万)
faiss = FaissStore(dimension=1536)  # 默认 IVFFlat

# 大规模 (>100万)
from ame.storage.faiss_store import FaissStore
import faiss as faiss_lib

quantizer = faiss_lib.IndexFlatL2(1536)
index = faiss_lib.IndexHNSWFlat(1536, 32)
# 自定义传入...
```

### 批量操作
```python
# 批量添加文档
embeddings = [[0.1] * 1536 for _ in range(100)]
doc_ids = [f"doc_{i}" for i in range(100)]

await faiss.add_batch(embeddings, doc_ids)
```

---

## 🧪 测试

### 运行测试
```bash
# 完整测试套件（需要 FalkorDB 运行）
pytest tests/ -v --cov=ame --cov-report=html --cov-report=term

# 仅单元测试（快速，无需外部服务）
pytest tests/ -v -m unit

# 集成测试（需要 FalkorDB）
pytest tests/ -v -m integration

# 跳过需要 FalkorDB 的测试
pytest tests/ -v -m "not requires_falkor"

# 性能基准测试
pytest tests/ -v -m benchmark
```

### 测试覆盖率
```bash
# 生成 HTML 报告
pytest tests/ --cov=ame --cov-report=html

# 查看报告
open htmlcov/index.html
```

### 测试结构
```
tests/
├── conftest.py              # 共享 fixtures
├── unit/
│   ├── test_faiss_store.py  # Faiss 单元测试 (17 tests)
│   └── test_falkor_store.py # FalkorDB 集成测试 (13 tests)
├── integration/
│   ├── test_hybrid_repository.py  # 混合仓库测试 (6 tests)
│   └── test_rag_pipeline.py      # RAG 端到端测试 (8 tests)
└── fixtures/
    └── sample_docs.json      # 测试数据
```

### 示例测试
```python
# ame/tests/test_hybrid_repository.py
import pytest
from ame.repository.hybrid_repository import HybridRepository

@pytest.mark.asyncio
async def test_create_and_retrieve():
    repo = setup_test_repo()
    
    doc = create_test_document()
    result = await repo.create(doc)
    
    assert result.id == doc.id
    assert result.stored_in_faiss == True
    assert result.stored_in_graph == True
```

---

## 🔗 集成示例

### 与 FastAPI 集成
```python
# ame-backend/app/main.py
import sys
from pathlib import Path

# 添加 ame 到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from ame.repository.hybrid_repository import HybridRepository

app = FastAPI()

@app.post("/documents")
async def create_document(content: str):
    repo = get_hybrid_repository()
    doc = Document(content=content, ...)
    result = await repo.create(doc)
    return {"id": result.id}
```

---

## 📝 依赖

```txt
# 核心
numpy>=1.24.0,<2.0.0
pydantic>=2.0.0
openai>=1.0.0

# 向量检索
faiss-cpu>=1.7.4  # 或 faiss-gpu

# 图数据库
falkordb==1.0.8
redis>=5.0.1

# NLP
spacy>=3.7.0

# 测试
pytest>=7.4.3
pytest-asyncio>=0.21.1
pytest-cov>=4.1.0
pytest-mock>=3.12.0
```

---

## 🐛 已知问题

1. **FalkorDB 可选依赖**: 如果 FalkorDB 未安装，相关测试会自动跳过
2. **NER 实体提取**: 占位实现，需要集成 spaCy 或 BERT
3. **Faiss 删除**: 不支持高效删除，需要定期重建索引

---

## 📚 相关文档

- [架构优化说明 (v0.2.0)](../ARCHITECTURE_OPTIMIZATION_V0.2.0.md)
- [双存储设计文档](../DUAL_STORAGE_DESIGN.md)
- [FalkorDB 官方文档](https://docs.falkordb.com/)
- [Pytest 使用指南](https://docs.pytest.org/)

---

## 🔄 迁移指南

### 从 v0.1.0 升级到 v0.2.0

1. **更新依赖**
```bash
pip install -r requirements.txt
```

2. **启动 FalkorDB**
```bash
docker run -d -p 6379:6379 falkordb/falkordb
python scripts/init_falkor_graph.py
```

3. **迁移向量数据** (如果使用 ChromaDB)
```bash
python scripts/migrate_vector_store.py \
  --source ./data/old_vector_store \
  --target ./data/faiss \
  --verify
```

4. **更新代码**
```python
# 旧代码
from ame.vector_store.factory import VectorStoreFactory
vector_store = VectorStoreFactory.create("memu", db_path)

# 新代码
from ame.storage.faiss_store import FaissStore
faiss_store = FaissStore(dimension=1536, index_path=db_path)
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License
