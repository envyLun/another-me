# AME Wiki

欢迎来到 AME (Another Me Engine) 的 Wiki 文档中心！

---

## 📚 文档导航

### 🏗️ 架构与设计

- **[架构设计](ARCHITECTURE.md)** - 四层架构详解
  - 设计理念
  - 各层职责
  - 依赖关系
  - 数据流转
  - 扩展性设计

### 💻 开发指南

- **[开发指南](DEVELOPMENT.md)** - 开发规范和最佳实践
  - 环境设置
  - 代码规范
  - 依赖注入规范
  - 测试规范
  - 最佳实践

### 📖 API 参考

- **[API 参考](API_REFERENCE.md)** - 完整 API 文档
  - Foundation Layer API
  - Capabilities Layer API
  - Services Layer API
  - 完整类型定义

### 🚀 部署指南

- **[部署指南](DEPLOYMENT.md)** - 生产环境部署
  - Docker 部署
  - 配置管理
  - 性能优化
  - 监控告警

---

## 🎯 快速链接

### 新手入门
1. [快速开始](../../README.md#快速开始)
2. [基础示例](../examples/01_basic_usage.py)
3. [架构概览](ARCHITECTURE.md)

### 开发者
1. [开发规范](DEVELOPMENT.md#代码规范)
2. [依赖注入](DEVELOPMENT.md#依赖注入规范)
3. [测试指南](DEVELOPMENT.md#测试规范)

### 高级用户
1. [扩展能力](../examples/08_custom_capability.py)
2. [自定义 Pipeline](../examples/09_custom_pipeline.py)
3. [服务集成](../examples/10_service_integration.py)

---

## 📋 文档概览

### Foundation Layer (基础层)

**职责**: 提供原子化技术能力

**核心模块**:
- LLM - 大模型调用
- Embedding - 向量化
- Storage - 数据存储
- NLP - 基础 NLP
- Inference - 级联推理

📖 [详细文档](../../foundation/README.md)

---

### Capabilities Layer (能力层)

**职责**: 组合基础能力，提供高级功能

**核心能力**:
- HybridRetriever - 混合检索
- DataAnalyzer - 数据分析
- StyleGenerator - 风格生成
- MemoryManager - 记忆管理
- IntentRecognizer - 意图识别

📖 [能力工厂](../examples/02_capability_factory.py)

---

### Services Layer (服务层)

**职责**: 封装业务逻辑，提供场景化服务

**服务分类**:
- **Conversation** - 对话服务
  - [MimicService](../../services/conversation/README.md)
  
- **Knowledge** - 知识服务
  - [SearchService](../../services/knowledge/README.md)
  - [DocumentService](../../services/knowledge/README.md)
  
- **Life** - 生活服务
  - [MoodService](../../services/life/README.md)
  - [InterestService](../../services/life/README.md)
  - [MemoryService](../../services/life/README.md)
  
- **Work** - 工作服务
  - [ReportService](../../services/work/README.md)
  - [TodoService](../../services/work/README.md)
  - [MeetingService](../../services/work/README.md)
  - [ProjectService](../../services/work/README.md)

---

## 🎓 学习资源

### 教程

1. **基础教程**
   - [AME 快速入门](../../README.md)
   - [第一个应用](../examples/01_basic_usage.py)

2. **进阶教程**
   - [理解四层架构](ARCHITECTURE.md)
   - [掌握依赖注入](DEVELOPMENT.md#依赖注入规范)

3. **高级教程**
   - [扩展自定义能力](../examples/08_custom_capability.py)
   - [构建完整应用](../examples/10_service_integration.py)

### 示例代码

- [所有示例](../examples/README.md)
- [基础使用](../examples/01_basic_usage.py)
- [对话服务](../examples/04_mimic_service.py)
- [工作报告](../examples/07_work_report.py)

---

## 🔍 常见问题 (FAQ)

### 架构相关

**Q: 为什么使用四层架构？**

A: 四层架构实现了清晰的职责分离，每一层都有明确的职责：
- Foundation: 原子技术能力
- Capabilities: 能力组合
- Services: 业务逻辑
- Application: 对外接口

这样的设计使得代码高度可复用、可测试、易扩展。

**Q: Service 层为什么不能直接使用 Foundation 层？**

A: 遵循依赖倒置原则，Service 层应该依赖抽象的 CapabilityFactory，而非具体的 Foundation 组件。这样：
- 降低耦合
- 便于测试
- 易于扩展

---

### 开发相关

**Q: 如何添加新的服务？**

A: 创建新服务的步骤：

```python
from ame.capabilities import CapabilityFactory

class MyNewService:
    def __init__(self, capability_factory: CapabilityFactory):
        self.factory = capability_factory
        # 使用 factory 创建所需能力
        self.retriever = factory.create_retriever(cache_key="my_retriever")
    
    async def my_method(self, params):
        # 实现业务逻辑
        pass
```

📖 [详细指南](DEVELOPMENT.md)

**Q: 如何扩展新的能力？**

A: 参考 [自定义能力示例](../examples/08_custom_capability.py)

---

### 使用相关

**Q: 如何初始化 AME？**

A: 基本初始化流程：

```python
# 1. 创建基础组件
llm = OpenAICaller(api_key="...")
embedding = OpenAIEmbedding(api_key="...")
vector_store = VectorStore(...)

# 2. 创建工厂
factory = CapabilityFactory(
    llm_caller=llm,
    embedding_function=embedding,
    vector_store=vector_store
)

# 3. 创建服务
service = MimicService(capability_factory=factory)
```

📖 [完整示例](../examples/01_basic_usage.py)

**Q: 如何使用流式对话？**

A: 使用 `chat_stream` 方法：

```python
async for chunk in service.chat_stream(user_message="..."):
    print(chunk, end="", flush=True)
```

---

## 🛠️ 开发工具

### IDE 配置

推荐使用 VSCode，安装以下插件：
- Python
- Pylance
- Python Test Explorer

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用 pdb 调试
import pdb; pdb.set_trace()
```

---

## 📈 性能优化

### 使用缓存

```python
# 复用能力实例
retriever = factory.create_retriever(cache_key="my_retriever")
```

### 批处理

```python
# 异步批处理
tasks = [process_item(item) for item in items]
results = await asyncio.gather(*tasks)
```

---

## 🤝 贡献指南

欢迎贡献文档！

### 文档规范

- 使用 Markdown 格式
- 添加代码示例
- 保持结构清晰
- 添加目录导航

### 提交流程

1. Fork 项目
2. 修改文档
3. 提交 PR
4. 等待审核

---

## 📧 获取帮助

- **GitHub Issues**: https://github.com/your-repo/another-me/issues
- **Email**: your-email@example.com
- **Discord**: https://discord.gg/your-server

---

## 📝 更新日志

### 2025-01-09
- ✅ 创建完整文档体系
- ✅ 添加架构设计文档
- ✅ 添加开发指南
- ✅ 添加示例代码

---

<div align="center">

**📚 持续完善中，欢迎贡献！**

[返回主页](../../README.md) • [示例代码](../examples/README.md) • [GitHub](https://github.com/your-repo/another-me)

</div>
