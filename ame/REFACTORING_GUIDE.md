# AME 项目重构指南

## 重构目标

将 AME 重构为清晰的三层架构：Foundation → Capabilities → Services

## 重构原则

1. **无需兼容旧版本** - 这是一次彻底的架构重构
2. **从零开始思考** - 按照最佳实践重新设计
3. **分层清晰** - 严格遵守三层依赖关系
4. **职责单一** - 每个模块只做一件事

## 架构设计

```
ame/
├── foundation/          # 基础能力层 - 原子化的技术能力
│   ├── storage/         # 存储能力
│   ├── nlp/            # NLP 基础能力
│   ├── llm/            # LLM 调用能力
│   ├── embedding/      # 向量化能力
│   ├── inference/      # 推理框架能力
│   └── utils/          # 工具函数
│
├── capabilities/        # 能力模块层 - 组合基础能力
│   ├── retrieval/      # 检索能力
│   ├── analysis/       # 分析能力
│   ├── generation/     # 生成能力
│   └── memory/         # 记忆能力
│
└── services/           # 业务服务层 - 组合能力模块
    ├── work/           # 工作场景服务
    ├── life/           # 生活场景服务
    ├── knowledge/      # 知识库服务
    └── conversation/   # 对话服务
```

## 重构进度

### Phase 1: Foundation Layer ✅ 进行中
- [x] 创建目录结构
- [ ] 迁移存储模块
- [ ] 迁移 LLM 模块
- [ ] 提取情绪识别模块
- [ ] 迁移级联推理框架
- [ ] 迁移 NER 模块

### Phase 2: Capabilities Layer ⏳ 待开始
- [ ] 合并 RAG 模块
- [ ] 合并数据分析模块
- [ ] 重构检索模块
- [ ] 创建记忆能力模块

### Phase 3: Services Layer ⏳ 待开始
- [ ] 拆分 WorkEngine
- [ ] 拆分 LifeEngine
- [ ] 拆分 HybridRepository

### Phase 4: Testing & Documentation ⏳ 待开始
- [ ] 编写单元测试
- [ ] 更新文档
- [ ] 性能优化

## 实施日期

- 开始时间: 2025-11-09
- 预计完成: TBD

## 注意事项

1. 所有新代码必须遵循 Python 3.11+ 特性
2. 使用类型提示 (Type Hints)
3. 添加完整的文档字符串
4. 每个模块都要有对应的测试

## 参考文档

- [new_arch.md](./new_arch.md) - 详细的重构方案
- [README.md](./README.md) - 项目文档
