# 变更日志

## [0.4.0] - 2025-11-09

### 新增 (Added)
- ✨ **CapabilityFactory** - 能力工厂模式，支持灵活组合和扩展
  - 8 种单一能力构建方法
  - 4 种预设场景能力包（工作、生活、对话、知识）
  - 自定义能力组合方法
  - 能力实例缓存机制
- 📖 **FACTORY_USAGE.md** - 完整的 Factory 使用指南 (351 行)
- 📖 **FACTORY_QUICKSTART.md** - Factory 快速参考卡片 (109 行)
- 📖 **FACTORY_REFACTORING_COMPLETE.md** - 详细的重构报告 (471 行)

### 改进 (Changed)
- 🔄 **CapabilityType** - 新增能力类型枚举，用于自定义组合
- 📦 **ame/__init__.py** - 导出 CapabilityFactory 和 CapabilityType
- 📦 **capabilities/__init__.py** - 导出 Factory 相关类
- 📦 **data_processor/__init__.py** - 改为兼容层，导出 TextProcessor 和 DocumentProcessor

### 删除 (Removed)
- 🗑️ **data_processor/processor.py** (222 行) - 功能已迁移到 foundation.utils.TextProcessor
- 🗑️ **data_processor/base.py** (~50 行) - 已不再使用

### 修复 (Fixed)
- 🐛 修复 data_processor 与 foundation.utils 的代码重复问题
- 🐛 统一文本处理逻辑到 foundation.utils.TextProcessor

### 架构改进
```
Before:
  - 依赖分散在各个 Service
  - 能力直接实例化
  - 272 行重复代码

After:
  - 依赖集中在 CapabilityFactory
  - 通过 Factory 构建能力
  - 0 行重复代码
  - 支持预设场景包和自定义组合
```

### 迁移指南
参考文档：
- `ame/capabilities/FACTORY_USAGE.md` - 完整使用指南
- `ame/capabilities/FACTORY_QUICKSTART.md` - 快速参考

---

## [0.3.0] - 2025-11-09 (之前的重构)

### 新增
- ✨ 三层架构：Foundation → Capabilities → Services
- ✨ 所有 Services 层实现 (10 个服务)
- ✨ StyleGenerator - 风格化文本生成器
- ✨ TextProcessor - 统一文本处理工具

### 删除
- 🗑️ 7 个冗余目录（已备份）
  - engines/, mem/, rag/, rag_generator/
  - storage/, retrieval/, search/

### 架构
- 📁 Foundation Layer: 完整
- 📁 Capabilities Layer: 完整
- 📁 Services Layer: 完整 (10/10)
- 📉 代码减少: 37.5% (~3000 行)

---

## 统计

### 代码量变化
```
v0.3.0 -> v0.4.0:
  新增: +943 行
    - factory.py: 363 行
    - FACTORY_USAGE.md: 351 行
    - FACTORY_QUICKSTART.md: 109 行
    - FACTORY_REFACTORING_COMPLETE.md: 471 行
    - __init__.py 更新: ~20 行
  
  删除: -272 行
    - processor.py: 222 行
    - base.py: 50 行
  
  净增加: +671 行（主要是文档）
  净代码增加: +141 行（全是新功能）
```

### 能力覆盖
- Foundation Layer: 6 个模块 ✅
- Capabilities Layer: 5 个模块 + Factory ✅
- Services Layer: 10 个服务 ✅
- Factory 方法: 13 个 ✅

---

## 向后兼容性

✅ **完全向后兼容**
- `data_processor.DataProcessor` 仍然可用（别名到 TextProcessor）
- `data_processor.DocumentProcessor` 保留
- 所有现有能力类仍可直接导入和使用
- Factory 是可选的，推荐但非必需

---

## 下一步计划

### v0.5.0 (计划中)
- [ ] 为 Factory 添加单元测试
- [ ] 优化预设能力包（基于实际使用反馈）
- [ ] 添加性能监控（能力创建耗时）
- [ ] 探索依赖注入框架集成

---

## 贡献者
- Another Me Team

## 许可证
MIT License

