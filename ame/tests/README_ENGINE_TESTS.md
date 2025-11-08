# AME 引擎层测试文档

## 概述

本目录包含 AME 引擎层（v2.0.0）的单元测试和集成测试。

## 测试结构

```
ame/tests/
├── unit/
│   ├── test_work_engine.py       # WorkEngine 单元测试
│   └── test_life_engine.py       # LifeEngine 单元测试
├── integration/
│   └── test_engine_integration.py # 引擎集成测试
└── README_ENGINE_TESTS.md        # 本文档
```

## 测试覆盖

### 1. WorkEngine 单元测试

**文件**: `unit/test_work_engine.py`

**测试类**:
- `TestWorkEngine` - 工作引擎核心功能测试
  - ✅ 周报生成成功
  - ✅ 日报生成成功
  - ✅ 待办整理成功
  - ✅ 待办优先级算法
  - ✅ 项目进度追踪
  - ✅ 无数据时的处理
  
- `TestTaskPrioritization` - 任务优先级算法测试
  - ✅ 紧急关键词检测
  - ✅ 重要性关键词检测
  - ✅ 组合优先级评分

**集成测试**:
- ✅ 完整工作流测试

### 2. LifeEngine 单元测试

**文件**: `unit/test_life_engine.py`

**测试类**:
- `TestLifeEngine` - 生活引擎核心功能测试
  - ✅ 心情分析成功
  - ✅ 心情分析包含趋势
  - ✅ 兴趣追踪成功
  - ✅ 兴趣演化分析
  - ✅ 生活建议生成
  - ✅ 记忆回忆

- `TestMoodAnalysis` - 心情分析专项测试
  - ✅ 情绪检测
  - ✅ 触发因素提取
  - ✅ 情绪趋势分析

- `TestInterestTracking` - 兴趣追踪专项测试
  - ✅ 兴趣演化分析

**集成测试**:
- ✅ 完整生活分析流程

### 3. 引擎集成测试

**文件**: `integration/test_engine_integration.py`

**测试类**:
- `TestWorkEngineIntegration` - WorkEngine 集成测试
  - ✅ 与 AnalyzeEngine 集成
  - ✅ 与 MimicEngine 集成

- `TestLifeEngineIntegration` - LifeEngine 集成测试
  - ✅ 与 AnalyzeEngine 集成
  - ✅ 心情分析完整流程

- `TestCrossEngineIntegration` - 跨引擎集成测试
  - ✅ 工作和生活引擎数据隔离
  - ✅ AnalyzeEngine 共享

**完整系统测试**:
- ✅ 全系统集成测试

## 运行测试

### 环境准备

1. 激活 conda 环境：
```bash
conda activate another
```

2. 安装测试依赖：
```bash
cd /Users/kaiiangs/Desktop/another-me/ame
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### 运行所有测试

```bash
# 运行所有引擎测试
pytest ame/tests/unit/test_work_engine.py -v
pytest ame/tests/unit/test_life_engine.py -v
pytest ame/tests/integration/test_engine_integration.py -v

# 或运行所有测试
pytest ame/tests/ -v
```

### 运行特定测试

```bash
# 运行 WorkEngine 测试
pytest ame/tests/unit/test_work_engine.py::TestWorkEngine::test_generate_weekly_report_success -v

# 运行 LifeEngine 测试
pytest ame/tests/unit/test_life_engine.py::TestLifeEngine::test_analyze_mood_success -v

# 运行集成测试
pytest ame/tests/integration/test_engine_integration.py::test_full_system_integration -v
```

### 生成覆盖率报告

```bash
# 生成覆盖率报告
pytest ame/tests/ --cov=ame/engines --cov=ame/mem --cov-report=html

# 查看报告
open htmlcov/index.html
```

## 测试数据

所有测试使用 Mock 对象，不依赖真实数据库或 API。

**Mock 组件**:
- `Mock()` - 模拟对象
- `AsyncMock()` - 异步模拟对象
- `@patch` - 打补丁装饰器

## 测试覆盖率目标

- **单元测试覆盖率**: >= 80%
- **集成测试覆盖率**: >= 60%
- **总体覆盖率**: >= 75%

## 已知问题

1. **MimicEngine 依赖**: 需要 mock FaissStore 和 RetrieverFactory
2. **时间敏感**: 部分测试依赖时间计算，可能需要固定时间

## 测试最佳实践

### 1. 使用 Fixture

```python
@pytest.fixture
def work_engine(mock_repository, mock_llm_caller):
    return WorkEngine(
        repository=mock_repository,
        llm_caller=mock_llm_caller
    )
```

### 2. 异步测试

```python
@pytest.mark.asyncio
async def test_async_function(work_engine):
    result = await work_engine.generate_weekly_report(...)
    assert result is not None
```

### 3. Mock 配置

```python
mock_analyzer.collect_time_range = AsyncMock(return_value=mock_docs)
mock_llm.generate = AsyncMock(return_value=Mock(content="测试"))
```

## 持续集成

建议在 CI/CD 流程中运行测试：

```yaml
# .github/workflows/test.yml
- name: Run Engine Tests
  run: |
    conda run -n another pytest ame/tests/unit/test_work_engine.py -v
    conda run -n another pytest ame/tests/unit/test_life_engine.py -v
    conda run -n another pytest ame/tests/integration/test_engine_integration.py -v
```

## 贡献指南

添加新测试时请遵循：

1. **命名规范**: `test_<功能>_<场景>`
2. **文档注释**: 每个测试添加清晰的文档字符串
3. **断言充分**: 验证所有关键输出
4. **Mock 清理**: 使用 fixture 确保 Mock 对象正确初始化

## 参考资料

- [pytest 文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock 文档](https://docs.python.org/3/library/unittest.mock.html)

---

**测试文档版本**: 1.0  
**最后更新**: 2025-01-07
