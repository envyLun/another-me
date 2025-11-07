# AME 引擎算法优化 - 测试指南

## 📋 测试概览

本测试套件包含完整的单元测试和集成测试，验证AME引擎算法优化的所有功能。

---

## 🗂️ 测试结构

```
ame/tests/
├── unit/                                # 单元测试
│   ├── test_ner.py                     # NER服务测试 (418行)
│   ├── test_graph_retriever.py         # GraphRetriever测试 (309行)
│   ├── test_faiss_store.py             # Faiss存储测试
│   └── test_falkor_store.py            # Falkor存储测试
│
├── integration/                         # 集成测试
│   ├── test_hybrid_retrieval_optimization.py  # 混合检索优化对比 (482行)
│   ├── test_hybrid_repository.py       # 混合仓库测试
│   └── test_rag_pipeline.py            # RAG流程测试
│
├── fixtures/                            # 测试数据
│   └── sample_docs.json
│
├── conftest.py                          # pytest配置
├── pytest.ini                           # pytest设置
└── README.md                            # 本文件
```

---

## 🚀 运行测试

### 1. 安装测试依赖

```bash
cd /Users/kailiangsennew/Desktop/another-me/ame
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### 2. 运行所有测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 显示print输出
pytest -s

# 生成覆盖率报告
pytest --cov=ame --cov-report=html
```

### 3. 运行特定测试

```bash
# 仅运行NER测试
pytest tests/unit/test_ner.py -v

# 仅运行GraphRetriever测试
pytest tests/unit/test_graph_retriever.py -v

# 仅运行集成测试
pytest tests/integration/test_hybrid_retrieval_optimization.py -v

# 运行特定测试类
pytest tests/unit/test_ner.py::TestSimpleNER -v

# 运行特定测试方法
pytest tests/unit/test_ner.py::TestSimpleNER::test_simple_ner_extract -v
```

### 4. 并行执行（加速）

```bash
# 安装pytest-xdist
pip install pytest-xdist

# 并行运行（4个worker）
pytest -n 4
```

---

## 📊 测试覆盖

### 单元测试覆盖

#### test_ner.py (418行)
- ✅ Entity数据结构测试（创建、相等性、哈希）
- ✅ NERBase基类测试（过滤、去重）
- ✅ SimpleNER测试（提取、停用词、词性映射）
- ✅ LLMBasedNER测试（提取、解析、fallback）
- ✅ HybridNER测试（融合策略、优先级判断）
- ✅ 集成测试（端到端）

**测试用例数**: 20+

#### test_graph_retriever.py (309行)
- ✅ 基本检索测试
- ✅ 多跳推理测试
- ✅ 实体提取测试
- ✅ 结果转换测试
- ✅ Fallback机制测试
- ✅ Top-K限制测试
- ✅ 分数排序测试
- ✅ 距离衰减测试

**测试用例数**: 15+

### 集成测试覆盖

#### test_hybrid_retrieval_optimization.py (482行)
- ✅ 基线对比（Vector Only vs Hybrid v2.0）
- ✅ 召回率提升验证
- ✅ 多跳推理效果测试
- ✅ 权重配置影响分析
- ✅ 分数融合正确性验证
- ✅ 并行执行测试
- ✅ 优化效果总结

**测试用例数**: 10+

---

## ✅ 测试检查清单

### 代码质量
- [x] 所有测试文件无语法错误
- [x] 使用Mock避免外部依赖
- [x] 测试覆盖关键路径
- [x] 异步测试正确使用pytest-asyncio

### NER模块
- [x] Entity数据结构完整性
- [x] SimpleNER词性标注正确性
- [x] LLMBasedNER JSON解析健壮性
- [x] HybridNER融合策略正确性
- [x] 实体过滤和去重功能

### GraphRetriever
- [x] 实体提取集成
- [x] 图谱检索功能
- [x] 多跳推理扩展
- [x] 距离衰减算法
- [x] Fallback机制

### HybridRetriever v2.0
- [x] 多源融合算法
- [x] 权重配置（Faiss 0.6 + Falkor 0.4）
- [x] 并行检索执行
- [x] 分数计算正确性

---

## 🔧 调试技巧

### 1. 查看详细日志

```bash
# 启用详细日志
pytest -v -s --log-cli-level=DEBUG
```

### 2. 跳过慢速测试

```python
# 标记慢速测试
@pytest.mark.slow
def test_slow_function():
    pass

# 跳过慢速测试
pytest -m "not slow"
```

### 3. 调试失败的测试

```bash
# 进入pdb调试器
pytest --pdb

# 仅运行失败的测试
pytest --lf
```

### 4. 生成HTML报告

```bash
# 安装pytest-html
pip install pytest-html

# 生成报告
pytest --html=report.html --self-contained-html
```

---

## 📈 预期测试结果

### 成功标准

```
================== test session starts ===================
platform darwin -- Python 3.11.x
collected 45+ items

tests/unit/test_ner.py ...................... [ 44%]
tests/unit/test_graph_retriever.py ......... [ 78%]
tests/integration/test_hybrid_retrieval_optimization.py .......... [100%]

================== 45+ passed in X.XXs ===================
```

### 覆盖率目标

- **总体覆盖率**: > 80%
- **NER模块**: > 90%
- **GraphRetriever**: > 85%
- **HybridRetriever**: > 85%

---

## ⚠️ 常见问题

### Q1: ImportError: No module named 'jieba'

**解决方案**:
```bash
pip install jieba
```

### Q2: 测试跳过（SKIPPED）

某些测试在依赖不可用时会自动跳过：
```python
pytest.skip("jieba not installed")
```

这是正常行为，不影响核心功能验证。

### Q3: 异步测试失败

确保安装了pytest-asyncio:
```bash
pip install pytest-asyncio
```

### Q4: Mock对象行为异常

检查Mock配置是否正确：
```python
mock_obj = AsyncMock()  # 异步方法用AsyncMock
mock_obj.method = AsyncMock(return_value={"key": "value"})
```

---

## 📚 扩展阅读

- [pytest官方文档](https://docs.pytest.org/)
- [pytest-asyncio文档](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock文档](https://docs.python.org/3/library/unittest.mock.html)

---

## 🎯 下一步

1. **运行测试**: `pytest -v`
2. **查看覆盖率**: `pytest --cov=ame --cov-report=html`
3. **打开报告**: `open htmlcov/index.html`
4. **补充测试**: 根据覆盖率报告补充测试用例

---

**祝测试顺利！** 🚀
