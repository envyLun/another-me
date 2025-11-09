# AME 示例代码

本目录包含了 AME 引擎的各种使用示例，从基础到高级，涵盖所有核心功能。

---

## 📚 示例列表

### 🔰 基础示例

#### [01_basic_usage.py](01_basic_usage.py) - 基础使用
**适合**: 初学者，第一次使用 AME

**内容**:
- 初始化基础组件
- 创建 CapabilityFactory
- 使用 MimicService 进行对话
- 流式对话
- 内容安全检测

**运行**:
```bash
python 01_basic_usage.py
```

---

#### [02_capability_factory.py](02_capability_factory.py) - 能力工厂详解
**适合**: 理解 AME 的核心设计模式

**内容**:
- 检索能力演示
- 分析能力演示
- 生成能力演示
- 记忆能力演示
- 意图识别演示
- 能力组合演示

**运行**:
```bash
python 02_capability_factory.py
```

**关键学习点**:
- 如何使用 `cache_key` 复用能力实例
- 不同 pipeline 模式的区别
- 如何组合多个能力

---

### 🔍 检索系统示例

#### [03_retrieval_system.py](03_retrieval_system.py) - 检索系统
**适合**: 需要构建智能检索的开发者

**内容**:
- 向量检索
- 图谱检索
- 混合检索
- Pipeline 模式对比
- 检索结果重排序

**运行**:
```bash
python 03_retrieval_system.py
```

---

### 💬 对话系统示例

#### [04_mimic_service.py](04_mimic_service.py) - 智能对话进阶
**适合**: 构建智能对话应用

**内容**:
- 基础对话
- 流式对话
- 意图识别和路由
- 内容安全过滤
- 记忆管理
- 风格模仿
- 上下文感知

**运行**:
```bash
python 04_mimic_service.py
```

**关键学习点**:
- 如何实现多轮对话
- 如何利用历史对话上下文
- 如何模仿用户说话风格

---

### 📚 知识管理示例

#### [05_knowledge_qa.py](05_knowledge_qa.py) - 知识问答系统
**适合**: 构建知识库问答应用

**内容**:
- 文档上传和处理
- 智能检索
- RAG 问答生成
- 多文档问答
- 引用溯源

**运行**:
```bash
python 05_knowledge_qa.py
```

---

### 📊 数据分析示例

#### [06_mood_tracking.py](06_mood_tracking.py) - 情绪追踪
**适合**: 构建个人数据分析应用

**内容**:
- 情绪检测
- 情绪趋势分析
- 情绪报告生成
- 数据可视化建议

**运行**:
```bash
python 06_mood_tracking.py
```

---

### 💼 工作管理示例

#### [07_work_report.py](07_work_report.py) - 工作报告生成
**适合**: 构建工作管理系统

**内容**:
- 周报/月报生成
- 待办事项管理
- 会议纪要提取
- 项目进度追踪
- 综合工作流

**运行**:
```bash
python 07_work_report.py
```

**关键学习点**:
- 如何组合多个 Work Services
- 如何构建完整的工作流
- 如何生成结构化报告

---

### 🔧 高级示例

#### [08_custom_capability.py](08_custom_capability.py) - 自定义能力
**适合**: 需要扩展 AME 功能的开发者

**内容**:
- 创建自定义能力
- 集成到 CapabilityFactory
- 在 Service 中使用自定义能力

**运行**:
```bash
python 08_custom_capability.py
```

---

#### [09_custom_pipeline.py](09_custom_pipeline.py) - 自定义 Pipeline
**适合**: 需要定制检索流程的开发者

**内容**:
- 创建自定义检索阶段
- 组装自定义 Pipeline
- Pipeline 性能优化

**运行**:
```bash
python 09_custom_pipeline.py
```

---

#### [10_service_integration.py](10_service_integration.py) - 多服务集成
**适合**: 构建复杂应用的开发者

**内容**:
- FastAPI 集成
- 多服务协同
- 统一错误处理
- 性能监控

**运行**:
```bash
python 10_service_integration.py
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r ../../requirements.txt

# 配置环境变量
export OPENAI_API_KEY=sk-...
```

### 2. 运行示例

```bash
# 从基础示例开始
python 01_basic_usage.py

# 然后尝试其他示例
python 02_capability_factory.py
python 04_mimic_service.py
```

### 3. 修改示例

所有示例都可以修改和扩展，建议：
1. 先运行原始示例
2. 理解代码逻辑
3. 修改参数测试效果
4. 应用到自己的项目

---

## 📖 学习路径

### 入门路径 (1-2 小时)

1. **01_basic_usage.py** - 了解基础概念
2. **02_capability_factory.py** - 理解核心设计
3. **04_mimic_service.py** - 掌握对话服务

### 进阶路径 (3-5 小时)

4. **03_retrieval_system.py** - 深入检索系统
5. **05_knowledge_qa.py** - 构建知识问答
6. **07_work_report.py** - 工作管理应用

### 高级路径 (5+ 小时)

7. **08_custom_capability.py** - 扩展功能
8. **09_custom_pipeline.py** - 定制流程
9. **10_service_integration.py** - 应用集成

---

## 💡 最佳实践

### 1. 使用依赖注入

```python
# ✅ 正确
factory = CapabilityFactory(...)
service = MimicService(capability_factory=factory)

# ❌ 错误
service = MimicService(llm, embedding, vector_store, ...)
```

### 2. 复用能力实例

```python
# ✅ 使用 cache_key
retriever1 = factory.create_retriever(cache_key="my_retriever")
retriever2 = factory.create_retriever(cache_key="my_retriever")
assert retriever1 is retriever2  # 同一个实例

# ❌ 不使用缓存，每次都创建新实例
retriever = factory.create_retriever()  # 每次都是新实例
```

### 3. 错误处理

```python
try:
    response = await service.chat(user_message)
except Exception as e:
    logger.error(f"Chat failed: {e}")
    # 返回友好错误信息
```

### 4. 日志记录

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Processing request...")
```

---

## 🐛 常见问题

### Q: 示例运行失败，提示 ImportError

**A**: 确保设置了 PYTHONPATH：

```bash
export PYTHONPATH=/Users/kaiiangs/Desktop/another-me:$PYTHONPATH
```

### Q: OpenAI API 调用失败

**A**: 检查环境变量：

```bash
echo $OPENAI_API_KEY
# 应该输出你的 API Key
```

### Q: 找不到某个模块

**A**: 确保安装了所有依赖：

```bash
pip install -r ../../requirements.txt
```

---

## 📚 相关文档

- [AME README](../../README.md)
- [架构设计](../wiki/ARCHITECTURE.md)
- [开发指南](../wiki/DEVELOPMENT.md)
- [API 参考](../wiki/API_REFERENCE.md)

---

## 🤝 贡献示例

欢迎贡献新的示例！提交前请确保：

1. 代码可运行
2. 添加详细注释
3. 更新本 README
4. 遵循代码规范

---

## 📧 获取帮助

- GitHub Issues: https://github.com/your-repo/another-me/issues
- Email: your-email@example.com
