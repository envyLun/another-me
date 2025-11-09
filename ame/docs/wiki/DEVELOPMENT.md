# AME 开发指南

本文档提供 AME 项目的开发规范、最佳实践和常见模式。

---

## 📋 目录

- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [依赖注入规范](#依赖注入规范)
- [测试规范](#测试规范)
- [最佳实践](#最佳实践)
- [常见模式](#常见模式)
- [故障排查](#故障排查)

---

## 🛠️ 开发环境设置

### 1. 环境要求

- **Python**: 3.11+
- **Conda**: 推荐使用 Conda 管理环境
- **IDE**: VSCode / PyCharm (推荐)

### 2. 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/another-me.git
cd another-me/ame

# 2. 创建 Conda 环境
conda create -n ame python=3.11
conda activate ame

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装开发依赖
pip install -r requirements-dev.txt

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API Key 等配置
```

### 3. IDE 配置

#### VSCode

安装推荐插件：
- Python
- Pylance
- Python Test Explorer
- Python Docstring Generator

配置 `.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ]
}
```

---

## 📝 代码规范

### 1. Python 代码规范

遵循 [PEP 8](https://pep8.org/) 规范：

```python
# ✅ 好的命名
class UserService:
    def get_user_by_id(self, user_id: str) -> User:
        pass

# ❌ 不好的命名
class userservice:
    def getUserById(self, userId):
        pass
```

### 2. 类型提示

**必须**添加完整的类型提示：

```python
from typing import List, Dict, Optional, Any

# ✅ 完整类型提示
async def search(
    query: str,
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    pass

# ❌ 缺少类型提示
async def search(query, top_k=5, filters=None):
    pass
```

### 3. 文档字符串

**必须**为类和公共方法添加文档字符串：

```python
class MimicService:
    """
    智能对话服务
    
    职责:
    - 内容安全过滤
    - 意图识别
    - 智能路由
    - 风格模仿
    """
    
    async def chat(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        智能对话
        
        Args:
            user_message: 用户消息
            context: 上下文信息（如 user_id）
        
        Returns:
            Dict[str, Any]: 包含回复内容和元数据的字典
            
        Raises:
            ValueError: 当消息为空时
        
        Example:
            >>> response = await service.chat("你好", {"user_id": "123"})
            >>> print(response["content"])
        """
        pass
```

### 4. 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 类名 | PascalCase | `MimicService`, `HybridRetriever` |
| 函数/方法 | snake_case | `create_retriever`, `get_user_by_id` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| 私有方法 | `_method_name` | `_build_prompt`, `_validate_input` |
| 变量 | snake_case | `user_id`, `total_count` |

### 5. 导入顺序

```python
# 1. 标准库
import os
import sys
from typing import List, Dict
from datetime import datetime

# 2. 第三方库
import numpy as np
from fastapi import FastAPI

# 3. 本地模块
from ame.foundation.llm import OpenAICaller
from ame.capabilities import CapabilityFactory
```

---

## 🏭 依赖注入规范

### 核心原则

**Service 层必须通过 CapabilityFactory 注入依赖，禁止直接传递 Foundation 层组件。**

### ✅ 正确做法

```python
from ame.capabilities import CapabilityFactory

class ReportService:
    def __init__(self, capability_factory: CapabilityFactory):
        """
        初始化报告服务
        
        Args:
            capability_factory: 能力工厂实例（由外部注入）
        """
        self.factory = capability_factory
        
        # 从 factory 获取 LLM
        self.llm = capability_factory.llm
        
        # 使用 factory 创建能力（利用缓存）
        self.analyzer = factory.create_data_analyzer(
            with_retriever=True,
            cache_key="report_analyzer"
        )
        
        self.generator = factory.create_style_generator(
            cache_key="report_generator"
        )
```

### ❌ 错误做法

```python
# ❌ 禁止在 Service 内部创建 Factory
class ReportService:
    def __init__(self, llm, embedding, vector_store, ...):
        # 违反依赖倒置原则
        self.factory = CapabilityFactory(
            llm_caller=llm,
            embedding_function=embedding,
            # ...
        )

# ❌ 禁止直接传递大量 Foundation 层组件
service = ReportService(
    llm_caller=llm,
    embedding=embedding,
    vector_store=vector_store,
    graph_store=graph_store,
    ner=ner,
    # ... 参数过多
)
```

### 使用 cache_key 复用实例

```python
# 在 Factory 层配置
factory = CapabilityFactory(...)

# 多个 Service 共享同一个 retriever
search_service = SearchService(factory)  # cache_key="knowledge_retriever"
doc_service = DocumentService(factory)   # cache_key="knowledge_retriever"

# 两个 Service 使用的是同一个 retriever 实例
assert search_service.retriever is doc_service.retriever  # True
```

---

## 🧪 测试规范

### 1. 测试文件结构

```
tests/
├── foundation/
│   ├── test_llm.py
│   ├── test_embedding.py
│   └── test_inference.py
├── capabilities/
│   ├── test_retrieval.py
│   ├── test_analysis.py
│   └── test_factory.py
└── services/
    ├── test_mimic_service.py
    ├── test_search_service.py
    └── test_report_service.py
```

### 2. 单元测试示例

```python
import pytest
from unittest.mock import Mock, AsyncMock
from ame.capabilities import CapabilityFactory
from ame.services.conversation import MimicService

@pytest.fixture
def mock_factory():
    """创建 Mock Factory"""
    factory = Mock(spec=CapabilityFactory)
    factory.llm = AsyncMock()
    factory.create_retriever = Mock(return_value=AsyncMock())
    factory.create_memory_manager = Mock(return_value=AsyncMock())
    return factory

@pytest.mark.asyncio
async def test_mimic_service_chat(mock_factory):
    """测试 MimicService.chat 方法"""
    # 设置 Mock 返回值
    mock_factory.llm.generate.return_value = Mock(
        content="你好！很高兴见到你。"
    )
    
    # 创建服务
    service = MimicService(capability_factory=mock_factory)
    
    # 调用方法
    response = await service.chat(
        user_message="你好",
        context={"user_id": "test_123"}
    )
    
    # 断言
    assert "content" in response
    assert response["content"] == "你好！很高兴见到你。"
    mock_factory.llm.generate.assert_called_once()
```

### 3. 集成测试示例

```python
import pytest
from ame.capabilities import CapabilityFactory
from ame.services.conversation import MimicService
from ame.foundation.llm import OpenAICaller

@pytest.mark.integration
@pytest.mark.asyncio
async def test_mimic_service_integration():
    """集成测试：使用真实 LLM"""
    # 创建真实组件
    llm = OpenAICaller(
        api_key="sk-test...",
        model="gpt-3.5-turbo"
    )
    
    factory = CapabilityFactory(llm_caller=llm)
    service = MimicService(capability_factory=factory)
    
    # 执行测试
    response = await service.chat("你好")
    
    # 验证
    assert response["content"]
    assert len(response["content"]) > 0
```

### 4. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块
pytest tests/services/test_mimic_service.py -v

# 运行带标记的测试
pytest -m integration -v

# 代码覆盖率
pytest --cov=ame --cov-report=html tests/

# 并行运行
pytest -n auto tests/
```

---

## 💡 最佳实践

### 1. 异常处理

```python
import logging

logger = logging.getLogger(__name__)

async def my_function():
    try:
        result = await some_operation()
        return result
    except SpecificError as e:
        # 记录错误
        logger.error(f"Operation failed: {e}", exc_info=True)
        # 抛出或返回友好错误
        raise ValueError(f"Failed to process: {str(e)}")
    except Exception as e:
        # 捕获未知错误
        logger.exception("Unexpected error occurred")
        raise
```

### 2. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

class MyService:
    def __init__(self, capability_factory):
        self.factory = capability_factory
        logger.info("MyService initialized")
    
    async def process(self, data):
        logger.debug(f"Processing data: {data}")
        
        try:
            result = await self._do_process(data)
            logger.info(f"Process completed successfully")
            return result
        except Exception as e:
            logger.error(f"Process failed: {e}")
            raise
```

### 3. 配置管理

```python
from pydantic import BaseSettings

class AppConfig(BaseSettings):
    """应用配置"""
    openai_api_key: str
    openai_model: str = "gpt-4"
    vector_store_path: str = "./data/vectors"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 使用配置
config = AppConfig()
llm = OpenAICaller(
    api_key=config.openai_api_key,
    model=config.openai_model
)
```

### 4. 性能优化

```python
# 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param: str) -> str:
    # 耗时计算
    return result

# 异步批处理
import asyncio

async def batch_process(items: List[str]) -> List[str]:
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
```

---

## 🎨 常见模式

### 1. 工厂模式

```python
class CapabilityFactory:
    def create_retriever(self, pipeline_mode: str, cache_key: Optional[str] = None):
        # 检查缓存
        if cache_key and cache_key in self._cache:
            return self._cache[cache_key]
        
        # 创建实例
        retriever = HybridRetriever(...)
        
        # 保存到缓存
        if cache_key:
            self._cache[cache_key] = retriever
        
        return retriever
```

### 2. 策略模式

```python
class RetrievalStrategy:
    async def retrieve(self, query: str) -> List[Document]:
        raise NotImplementedError

class VectorStrategy(RetrievalStrategy):
    async def retrieve(self, query: str):
        # 向量检索
        pass

class GraphStrategy(RetrievalStrategy):
    async def retrieve(self, query: str):
        # 图谱检索
        pass

class HybridRetriever:
    def __init__(self, strategy: RetrievalStrategy):
        self.strategy = strategy
    
    async def retrieve(self, query: str):
        return await self.strategy.retrieve(query)
```

### 3. Pipeline 模式

```python
class Stage:
    async def process(self, data):
        raise NotImplementedError

class Pipeline:
    def __init__(self, stages: List[Stage]):
        self.stages = stages
    
    async def run(self, data):
        for stage in self.stages:
            data = await stage.process(data)
        return data
```

---

## 🐛 故障排查

### 1. 常见错误

#### ImportError: No module named 'ame'

```bash
# 解决方案：设置 PYTHONPATH
export PYTHONPATH=/Users/kaiiangs/Desktop/another-me:$PYTHONPATH
```

#### TypeError: 'NoneType' object is not callable

```python
# 检查 Factory 是否正确注入
service = MimicService(capability_factory=factory)  # ✅
service = MimicService(None)  # ❌
```

### 2. 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用 pdb 调试
import pdb; pdb.set_trace()

# 打印变量
logger.debug(f"Variable value: {variable}")
```

### 3. 性能分析

```python
import time
import cProfile

# 简单计时
start = time.time()
result = await some_function()
logger.info(f"Execution time: {time.time() - start:.2f}s")

# 性能分析
cProfile.run('my_function()')
```

---

## 📚 参考资料

- [PEP 8 - Python 代码规范](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest 文档](https://docs.pytest.org/)
- [FastAPI 最佳实践](https://fastapi.tiangolo.com/tutorial/)

---

## 🤝 贡献流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 编写代码和测试
4. 运行测试 (`pytest tests/ -v`)
5. 提交更改 (`git commit -m 'Add amazing feature'`)
6. 推送到分支 (`git push origin feature/amazing-feature`)
7. 创建 Pull Request

---

## 📧 获取帮助

- GitHub Issues: https://github.com/your-repo/another-me/issues
- Email: your-email@example.com
