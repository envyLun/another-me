# AME 文档索引

本文档提供 AME 项目的完整文档导航。

---

## 📚 文档体系结构

```
ame/
├── README.md                          # 项目主文档
├── DOCUMENTATION_INDEX.md             # 本文档（文档索引）
│
├── foundation/
│   └── README.md                      # 基础层文档
│
├── capabilities/
│   └── (能力层，待补充文档)
│
├── services/
│   ├── conversation/
│   │   └── README.md                  # 对话服务文档
│   ├── knowledge/
│   │   └── README.md                  # 知识服务文档
│   ├── life/
│   │   └── README.md                  # 生活服务文档
│   └── work/
│       └── README.md                  # 工作服务文档
│
└── docs/
    ├── wiki/                          # Wiki 文档
    │   ├── README.md                  # Wiki 首页
    │   ├── ARCHITECTURE.md            # 架构设计
    │   └── DEVELOPMENT.md             # 开发指南
    │
    └── examples/                      # 示例代码
        ├── README.md                  # 示例索引
        ├── 01_basic_usage.py          # 基础使用
        ├── 02_capability_factory.py   # 能力工厂
        ├── 04_mimic_service.py        # 智能对话
        └── 07_work_report.py          # 工作报告
```

---

## 🎯 快速导航

### 新手入门

1. **[项目主文档](README.md)** - 从这里开始
   - 项目简介
   - 快速开始
   - 核心功能
   
2. **[基础使用示例](docs/examples/01_basic_usage.py)** - 第一个程序
   - 环境初始化
   - 创建服务
   - 基础对话

3. **[架构设计](docs/wiki/ARCHITECTURE.md)** - 理解设计理念
   - 四层架构
   - 设计原则
   - 依赖关系

---

### 开发者

1. **[开发指南](docs/wiki/DEVELOPMENT.md)** - 开发规范
   - 环境设置
   - 代码规范
   - 测试规范
   - 最佳实践

2. **[依赖注入规范](docs/wiki/DEVELOPMENT.md#依赖注入规范)** - 核心模式
   - 正确用法
   - 错误示例
   - cache_key 使用

3. **[能力工厂示例](docs/examples/02_capability_factory.py)** - 核心组件
   - 检索能力
   - 分析能力
   - 生成能力
   - 能力组合

---

### 功能模块

#### Foundation Layer (基础层)

- **[Foundation README](foundation/README.md)**
  - LLM 调用
  - Embedding
  - 级联推理
  - 存储接口
  - NLP 能力

#### Services Layer (服务层)

- **[Conversation Services](services/conversation/README.md)**
  - MimicService - 智能对话
  - [使用示例](docs/examples/04_mimic_service.py)

- **[Knowledge Services](services/knowledge/README.md)**
  - SearchService - 智能搜索
  - DocumentService - 文档管理

- **[Life Services](services/life/README.md)**
  - MoodService - 情绪追踪
  - InterestService - 兴趣发现
  - MemoryService - 记忆管理

- **[Work Services](services/work/README.md)**
  - ReportService - 报告生成
  - TodoService - 待办管理
  - MeetingService - 会议纪要
  - ProjectService - 项目追踪
  - [使用示例](docs/examples/07_work_report.py)

---

## 📖 文档分类

### 按内容类型

| 类型 | 文档 | 说明 |
|------|------|------|
| **概览文档** | [README.md](README.md) | 项目总览 |
| **架构文档** | [ARCHITECTURE.md](docs/wiki/ARCHITECTURE.md) | 架构设计 |
| **开发文档** | [DEVELOPMENT.md](docs/wiki/DEVELOPMENT.md) | 开发指南 |
| **API 文档** | 各层 README | 模块文档 |
| **示例代码** | [examples/](docs/examples/) | 使用示例 |

### 按技术层级

| 层级 | 文档 | 示例 |
|------|------|------|
| **Foundation** | [foundation/README.md](foundation/README.md) | - |
| **Capabilities** | 待补充 | [02_capability_factory.py](docs/examples/02_capability_factory.py) |
| **Services** | [services/*/README.md](services/) | [04_mimic_service.py](docs/examples/04_mimic_service.py) |
| **Application** | [DEVELOPMENT.md](docs/wiki/DEVELOPMENT.md) | [10_service_integration.py](docs/examples/) |

---

## 🎓 学习路径

### 初学者路径 (2-3 小时)

```
1. README.md (项目概览)
   ↓
2. docs/examples/01_basic_usage.py (基础使用)
   ↓
3. docs/wiki/ARCHITECTURE.md (理解架构)
   ↓
4. docs/examples/04_mimic_service.py (对话服务)
```

### 开发者路径 (5-8 小时)

```
1-4. 完成初学者路径
   ↓
5. docs/wiki/DEVELOPMENT.md (开发规范)
   ↓
6. docs/examples/02_capability_factory.py (能力工厂)
   ↓
7. services/*/README.md (各服务文档)
   ↓
8. foundation/README.md (基础层详解)
```

### 高级开发者路径 (10+ 小时)

```
1-8. 完成开发者路径
   ↓
9. 阅读所有示例代码
   ↓
10. 研究源代码实现
   ↓
11. 扩展自定义功能
```

---

## 📝 示例代码索引

### 基础示例

| 文件 | 功能 | 难度 |
|------|------|------|
| [01_basic_usage.py](docs/examples/01_basic_usage.py) | 基础使用 | ⭐ |
| [02_capability_factory.py](docs/examples/02_capability_factory.py) | 能力工厂 | ⭐⭐ |

### 服务示例

| 文件 | 功能 | 难度 |
|------|------|------|
| [04_mimic_service.py](docs/examples/04_mimic_service.py) | 智能对话 | ⭐⭐ |
| [07_work_report.py](docs/examples/07_work_report.py) | 工作报告 | ⭐⭐⭐ |

### 高级示例

| 文件 | 功能 | 难度 |
|------|------|------|
| 08_custom_capability.py | 自定义能力 | ⭐⭐⭐ |
| 09_custom_pipeline.py | 自定义 Pipeline | ⭐⭐⭐⭐ |
| 10_service_integration.py | 服务集成 | ⭐⭐⭐⭐ |

> 注：高级示例正在编写中

---

## 🔍 查找指南

### 我想了解...

**"AME 是什么？"**
→ [README.md](README.md#项目简介)

**"如何快速开始？"**
→ [README.md](README.md#快速开始) + [01_basic_usage.py](docs/examples/01_basic_usage.py)

**"架构是怎样的？"**
→ [ARCHITECTURE.md](docs/wiki/ARCHITECTURE.md)

**"如何开发新功能？"**
→ [DEVELOPMENT.md](docs/wiki/DEVELOPMENT.md)

**"如何使用对话服务？"**
→ [conversation/README.md](services/conversation/README.md) + [04_mimic_service.py](docs/examples/04_mimic_service.py)

**"如何生成工作报告？"**
→ [work/README.md](services/work/README.md) + [07_work_report.py](docs/examples/07_work_report.py)

**"如何自定义能力？"**
→ [08_custom_capability.py](docs/examples/) (待补充)

---

## 📊 文档统计

### 已完成文档

- ✅ 项目主文档 (README.md)
- ✅ 架构设计文档 (ARCHITECTURE.md)
- ✅ 开发指南 (DEVELOPMENT.md)
- ✅ Wiki 首页 (wiki/README.md)
- ✅ 示例索引 (examples/README.md)
- ✅ Foundation 层文档
- ✅ Services 层文档 (4个服务)
- ✅ 基础示例代码 (4个)

### 待补充文档

- ⏳ API 参考文档 (API_REFERENCE.md)
- ⏳ 部署指南 (DEPLOYMENT.md)
- ⏳ Capabilities 层文档
- ⏳ 高级示例代码 (3个)
- ⏳ 测试文档
- ⏳ 性能优化指南

---

## 🤝 贡献文档

欢迎贡献文档！请遵循以下规范：

### 文档规范

1. **Markdown 格式**: 所有文档使用 Markdown
2. **添加目录**: 长文档添加目录导航
3. **代码示例**: 提供可运行的代码示例
4. **图表说明**: 必要时添加架构图、流程图

### 提交流程

1. 在 `docs/` 目录下添加/修改文档
2. 更新本索引文档
3. 提交 PR
4. 等待审核

---

## 📧 反馈与建议

如果你发现文档有任何问题或建议，欢迎：

- 提交 [GitHub Issue](https://github.com/your-repo/another-me/issues)
- 发送邮件至 your-email@example.com
- 直接提交 PR 改进

---

## 📅 更新日志

### 2025-01-09
- ✅ 创建完整文档体系
- ✅ 添加主 README
- ✅ 添加 Wiki 文档
- ✅ 添加示例代码
- ✅ 创建文档索引

---

<div align="center">

**📚 完整、清晰、实用的文档是优秀项目的基础**

[返回主页](README.md) • [Wiki 文档](docs/wiki/README.md) • [示例代码](docs/examples/README.md)

</div>
