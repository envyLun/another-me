# Foundation Layer - 基础能力层

Foundation Layer 提供原子化的技术能力，无业务逻辑，可独立使用和测试。

## 设计原则

1. **独立性**: 每个模块可独立使用，不依赖业务逻辑
2. **可测试性**: 100% 可单元测试
3. **可复用性**: 为上层（Capabilities/Services）提供基础能力
4. **接口清晰**: 提供清晰的抽象接口

## 模块列表

### 1. Inference (推理框架)

级联推理引擎，支持多层级推理（规则 → 快速模型 → LLM）。

**使用场景**:
- NER 实体识别
- 情绪识别
- 意图分类
- 任何需要「快速 + 准确」的推理任务

**快速开始**:
```python
from foundation.inference import CascadeInferenceEngine, create_rule_level, create_llm_level

# 创建级联引擎
engine = CascadeInferenceEngine(
    confidence_threshold=0.7,  # 置信度阈值
    enable_cache=True,         # 启用缓存
    fallback_strategy="cascade"  # 级联策略
)

# 定义规则层级
def rule_ner(text, context):
    entities = extract_by_rules(text)
    return InferenceResult(
        value=entities,
        confidence=0.9 if entities else 0.3,
        level=InferenceLevel.RULE
    )

# 定义 LLM 层级
def llm_prompt_builder(text, context):
    return f"Extract entities from: {text}"

def llm_result_parser(response):
    entities = parse_llm_response(response)
    return InferenceResult(
        value=entities,
        confidence=0.95,
        level=InferenceLevel.LLM
    )

# 添加层级
engine.add_level(create_rule_level(rule_ner, name="Rule NER"))
engine.add_level(create_llm_level(llm_caller, llm_prompt_builder, llm_result_parser, name="LLM NER"))

# 执行推理
result = await engine.infer("今天天气真好", context={})
print(f"Result: {result.value}, Confidence: {result.confidence}, Level: {result.level}")
```

**API 文档**:
- `CascadeInferenceEngine`: 级联推理引擎
  - `add_level(level)`: 添加推理层级
  - `infer(input_data, context, force_level)`: 执行推理
  - `clear_cache()`: 清空缓存
  - `get_statistics()`: 获取统计信息
  
- `InferenceLevelBase`: 推理层级抽象基类
  - `infer(input_data, context) -> InferenceResult`: 执行推理
  - `get_level() -> InferenceLevel`: 获取层级
  - `get_name() -> str`: 获取名称

- `InferenceResult`: 推理结果
  - `value: Any`: 结果值
  - `confidence: float`: 置信度（0-1）
  - `level: InferenceLevel`: 推理层级
  - `metadata: Dict`: 元数据

### 2. LLM (LLM 调用)

统一的 LLM 调用接口，支持 OpenAI 和兼容 API。

**特性**:
- ✅ 自动重试（指数退避）
- ✅ 请求缓存（基于消息内容）
- ✅ 流式输出支持
- ✅ 完整的错误处理

**快速开始**:
```python
from foundation.llm import OpenAICaller

# 初始化调用器
llm = OpenAICaller(
    api_key="sk-...",
    base_url="https://api.openai.com/v1",
    model="gpt-4",
    max_retries=3,
    timeout=60.0,
    cache_enabled=True
)

# 检查是否已配置
if not llm.is_configured():
    raise ValueError("LLM 未配置")

# 生成回复
response = await llm.generate(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(f"Content: {response.content}")
print(f"Model: {response.model}")
print(f"Tokens: {response.usage['total_tokens']}")

# 使用便捷方法
response = await llm.generate_with_system(
    prompt="Hello!",
    system_prompt="You are a helpful assistant.",
    temperature=0.7
)

# 流式生成
async for chunk in llm.generate_stream(
    messages=[{"role": "user", "content": "Tell me a story"}],
    temperature=0.8
):
    print(chunk, end="", flush=True)

# 清空缓存
llm.clear_cache()
print(f"Cache size: {llm.get_cache_size()}")
```

**API 文档**:
- `OpenAICaller`: OpenAI LLM 调用器
  - `generate(messages, temperature, max_tokens, model, **kwargs) -> LLMResponse`: 生成回复
  - `generate_stream(messages, ...) -> AsyncIterator[str]`: 流式生成
  - `generate_with_system(prompt, system_prompt, ...) -> LLMResponse`: 便捷方法
  - `get_model_name() -> str`: 获取模型名称
  - `is_configured() -> bool`: 检查是否已配置
  - `clear_cache()`: 清空缓存
  - `get_cache_size() -> int`: 获取缓存大小

- `LLMResponse`: LLM 响应
  - `content: str`: 生成的内容
  - `model: str`: 使用的模型
  - `usage: Dict[str, int]`: Token 使用情况
    - `prompt_tokens`: 提示词 Token 数
    - `completion_tokens`: 生成 Token 数
    - `total_tokens`: 总 Token 数
  - `metadata: Dict`: 元数据
  - `to_dict() -> dict`: 转换为字典

### 3. Storage (存储能力) - 待实现

向量存储、图谱存储、元数据存储、文档存储。

### 4. NLP (NLP 基础能力) - 待实现

NER、情绪识别、文本处理、关键词提取。

### 5. Embedding (向量化能力) - 待实现

文本向量化。

### 6. Utils (工具函数) - 待实现

时间处理、文本处理、数据验证。

## 依赖关系

```
Foundation Layer (无外部依赖，除了第三方库)
    ↓
Capabilities Layer (依赖 Foundation)
    ↓
Services Layer (依赖 Capabilities)
```

**重要**: Foundation Layer 不应该依赖 Capabilities 或 Services Layer！

## 测试

每个模块都应该有对应的单元测试：

```bash
cd /Users/kaiiangs/Desktop/another-me/ame
conda activate another
python -m pytest tests/foundation/ -v
```

测试文件结构：
```
tests/
└── foundation/
    ├── test_inference.py
    ├── test_llm.py
    ├── test_storage.py
    ├── test_nlp.py
    ├── test_embedding.py
    └── test_utils.py
```

## 开发规范

### 1. 代码规范
- Python 3.11+
- 类型提示 (Type Hints)
- 文档字符串 (Docstrings)
- 遵循 PEP 8

### 2. 命名规范
- 类名: PascalCase (如 `CascadeInferenceEngine`)
- 函数名: snake_case (如 `create_rule_level`)
- 常量: UPPER_CASE (如 `DEFAULT_TIMEOUT`)
- 私有方法: `_method_name`

### 3. 异常处理
```python
try:
    result = await some_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### 4. 日志记录
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug info")
logger.info("Important info")
logger.warning("Warning")
logger.error("Error occurred")
```

## 贡献指南

1. 创建新模块前，先在 `new_arch.md` 中查看设计方案
2. 编写代码前，先编写测试（TDD）
3. 提交前，运行测试和类型检查
4. 添加完整的文档字符串

## 常见问题

### Q: Foundation Layer 可以调用业务逻辑吗？
**A**: 不可以！Foundation Layer 应该是纯技术能力，不包含任何业务逻辑。

### Q: 如何添加新的 LLM 提供商支持？
**A**: 继承 `LLMCallerBase` 并实现所有抽象方法：
```python
from foundation.llm import LLMCallerBase, LLMResponse

class MyLLMCaller(LLMCallerBase):
    async def generate(self, messages, ...):
        # 实现生成逻辑
        pass
    
    async def generate_stream(self, messages, ...):
        # 实现流式生成
        pass
    
    def get_model_name(self):
        return "my-model"
    
    def is_configured(self):
        return bool(self.api_key)
```

### Q: 如何创建新的推理层级？
**A**: 使用便捷函数或继承 `InferenceLevelBase`：
```python
# 方法 1: 使用便捷函数
level = create_rule_level(rule_func, name="My Rule")

# 方法 2: 继承基类
class MyInferenceLevel(InferenceLevelBase):
    async def infer(self, input_data, context):
        # 实现推理逻辑
        return InferenceResult(...)
    
    def get_level(self):
        return InferenceLevel.RULE
    
    def get_name(self):
        return "My Level"
```

## 更新日志

### 0.3.0 (2025-11-09)
- ✅ 创建 Foundation Layer 架构
- ✅ 实现 Inference 模块（级联推理引擎）
- ✅ 实现 LLM 模块（OpenAI 调用器）

### 待发布
- ⏳ Storage 模块
- ⏳ NLP 模块
- ⏳ Embedding 模块
- ⏳ Utils 模块

## 联系方式

- 项目文档: [README.md](../README.md)
- 架构设计: [new_arch.md](../new_arch.md)
- 重构指南: [REFACTORING_GUIDE.md](../REFACTORING_GUIDE.md)
