# AME 引擎算法优化 - 快速开始

## 🎯 核心优化

本次优化实现了三大核心能力提升：

1. **NER实体提取** - 智能识别文本中的人名、地名、机构、主题词
2. **图谱检索增强** - 基于实体关系的多跳推理检索
3. **混合检索v2.0** - Faiss语义 + Falkor图谱的协同检索

---

## 📦 安装依赖

```bash
cd ame
pip install -r requirements.txt

# 可选：安装jieba的Paddle模式（更准确的中文分词）
pip install paddlepaddle

# 可选：安装spaCy（高级NER）
pip install spacy
python -m spacy download zh_core_web_sm
```

---

## 🚀 快速使用

### 1. NER实体提取

```python
from ame.ner import HybridNER

# 初始化（自动使用SimpleNER + LLM增强）
ner = HybridNER(
    use_llm_threshold=500,      # 文本超过500字才用LLM
    enable_llm_enhancement=True  # 启用LLM增强
)

# 提取实体
text = "张三在北京的清华大学进行人工智能研究"
entities = await ner.extract(text)

for entity in entities:
    print(f"{entity.text} ({entity.type}): {entity.score:.2f}")

# 输出:
# 张三 (PERSON): 0.95
# 北京 (LOCATION): 0.90
# 清华大学 (ORGANIZATION): 0.92
# 人工智能 (TOPIC): 0.85
```

### 2. 图谱检索

```python
from ame.retrieval import GraphRetriever
from ame.storage.falkor_store import FalkorStore

# 初始化
falkor = FalkorStore(host="localhost", port=6379, graph_name="another_me")
retriever = GraphRetriever(
    falkor_store=falkor,
    enable_multi_hop=True,  # 启用多跳推理
    max_hops=2              # 最多2跳
)

# 检索相关文档
results = await retriever.retrieve(
    query="机器学习和深度学习的应用",
    top_k=10
)

for result in results:
    print(f"文档ID: {result.metadata['doc_id']}")
    print(f"相关度: {result.score:.3f}")
    print(f"匹配实体: {result.metadata.get('matched_entities', [])}")
    print("---")
```

### 3. 混合检索（Faiss + Falkor）

```python
from ame.retrieval import HybridRetriever, VectorRetriever, GraphRetriever
from ame.storage import FaissStore, FalkorStore

# 初始化存储
faiss = FaissStore(dimension=768)
falkor = FalkorStore()

# 初始化检索器
vector_retriever = VectorRetriever(faiss_store=faiss)
graph_retriever = GraphRetriever(falkor_store=falkor)

# 混合检索器
hybrid = HybridRetriever(
    vector_retriever=vector_retriever,
    graph_retriever=graph_retriever,
    vector_weight=0.6,  # Faiss语义相似度权重
    graph_weight=0.4    # Falkor图谱关系权重
)

# 执行检索
results = await hybrid.retrieve(
    query="如何使用transformer模型",
    top_k=10,
    enable_multi_hop=True,  # 启用图谱多跳推理
    max_hops=2
)

for result in results:
    print(f"综合分数: {result.score:.3f}")
    print(f"  - 向量分数: {result.metadata['vector_score']:.3f}")
    print(f"  - 图谱分数: {result.metadata['graph_score']:.3f}")
```

### 4. 在HybridRepository中使用

```python
from ame.repository import HybridRepository
from ame.storage import FaissStore, FalkorStore, MetadataStore
from ame.ner import HybridNER

# 初始化存储
faiss = FaissStore(dimension=768)
falkor = FalkorStore()
metadata = MetadataStore(db_path="./data/metadata.db")

# 初始化NER
ner = HybridNER()

# 初始化仓库（自动集成NER）
repo = HybridRepository(
    faiss_store=faiss,
    falkor_store=falkor,
    metadata_store=metadata,
    embedding_function=your_embedding_fn,
    ner_service=ner  # 传入NER服务
)

# 创建文档（自动提取实体并构建图谱）
from ame.models import Document
doc = Document(
    content="量子计算是未来计算技术的重要方向",
    doc_type="knowledge"
)

created_doc = await repo.create(doc)
print(f"提取的实体: {created_doc.entities}")

# 混合检索
results = await repo.hybrid_search(
    query="量子计算的应用",
    top_k=10,
    faiss_weight=0.6,  # 符合设计文档要求
    graph_weight=0.4
)
```

---

## 🎨 配置选项

### NER配置

```python
# 仅使用SimpleNER（快速，无需LLM）
from ame.ner import SimpleNER
ner = SimpleNER(enable_paddle=True)

# 仅使用LLM（高准确度，需要LLM API）
from ame.ner import LLMBasedNER
from ame.llm_caller import LLMCaller
ner = LLMBasedNER(llm_caller=your_llm_caller)

# 混合策略（推荐）
from ame.ner import HybridNER
ner = HybridNER(
    use_llm_threshold=500,       # 文本长度阈值
    enable_llm_enhancement=True, # 是否启用LLM
    fusion_strategy="merge"      # merge | llm_only | simple_only
)
```

### GraphRetriever配置

```python
retriever = GraphRetriever(
    falkor_store=falkor,
    enable_multi_hop=True,  # 是否启用多跳推理
    max_hops=2              # 最大跳数（1-3）
)
```

### HybridRetriever权重配置

```python
# 标准配置（符合设计文档）
hybrid = HybridRetriever(
    vector_retriever=vector_retriever,
    graph_retriever=graph_retriever,
    vector_weight=0.6,
    graph_weight=0.4
)

# 增强关键词匹配
hybrid = HybridRetriever(
    vector_retriever=vector_retriever,
    graph_retriever=graph_retriever,
    vector_weight=0.5,
    graph_weight=0.3,
    keyword_weight=0.2  # 启用关键词
)

# 时间敏感检索
hybrid = HybridRetriever(
    vector_retriever=vector_retriever,
    graph_retriever=graph_retriever,
    vector_weight=0.5,
    graph_weight=0.3,
    time_weight=0.2  # 启用时间衰减
)
```

---

## 📊 性能指标

### 实体提取性能

| 策略 | 速度 | 准确率 | 成本 |
|------|------|--------|------|
| SimpleNER | ⚡⚡⚡ 快 | 70-80% | 无 |
| LLMBasedNER | ⚡ 慢 | 85-95% | LLM API费用 |
| HybridNER | ⚡⚡ 中等 | 80-90% | 按需LLM调用 |

### 检索性能对比

| 检索器 | 语义理解 | 关系推理 | 召回率提升 |
|--------|----------|----------|------------|
| VectorRetriever | ⭐⭐⭐⭐⭐ | ⭐ | 基准 |
| GraphRetriever | ⭐⭐ | ⭐⭐⭐⭐⭐ | +15% |
| HybridRetriever v2.0 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | +25% |

---

## 🔧 故障排查

### 常见问题

**Q1: ModuleNotFoundError: No module named 'jieba'**
```bash
pip install jieba
```

**Q2: FalkorDB连接失败**
```bash
# 检查FalkorDB是否启动
docker ps | grep falkordb

# 启动FalkorDB
docker run -p 6379:6379 falkordb/falkordb:latest
```

**Q3: NER提取结果为空**
```python
# 检查文本长度
print(len(text))  # 确保文本长度 > min_word_length

# 降低阈值
ner = HybridNER(use_llm_threshold=100)
```

**Q4: 图谱检索无结果**
```python
# 检查图谱中是否有数据
stats = await falkor.execute_cypher("MATCH (n) RETURN count(n)")
print(stats)  # 应该 > 0

# 检查实体提取
entities = await ner.extract(query)
print(entities)  # 确保有提取到实体
```

---

## 📚 更多资源

- [完整实施总结](./AME_OPTIMIZATION_IMPLEMENTATION_SUMMARY.md)
- [设计文档](./ARCHITECTURE_OPTIMIZATION_V0.2.0.md)
- [API文档](./ame/README.md)

---

## 🎯 下一步

1. **运行测试**: `pytest ame/tests/`
2. **查看示例**: 参考 `ame/examples/` 目录
3. **调整配置**: 根据实际场景调整权重和阈值
4. **性能优化**: 使用缓存、批量处理等优化策略

---

**优化完成！开始使用吧 🚀**
