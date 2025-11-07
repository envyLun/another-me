# Another Me - 前端应用

基于 React + TypeScript + Vite 构建的现代化前端应用，实现"双模式双能力"架构。

---

## 🚀 快速开始

### 安装依赖
```bash
cd frontend
npm install
```

### 启动开发服务器
```bash
npm run dev
```

访问: http://localhost:5173

### 构建生产版本
```bash
npm run build
```

---

## 📁 项目结构

```
frontend/src/
├── types/              # TypeScript类型定义
│   ├── mode.ts         # 模式与能力类型
│   ├── work.ts         # 工作场景类型
│   ├── life.ts         # 生活场景类型
│   └── api.ts          # API响应类型
│
├── api/                # API客户端
│   ├── workAPI.ts      # 工作场景API
│   ├── lifeAPI.ts      # 生活场景API
│   ├── ragAPI.ts       # 知识库API
│   └── memAPI.ts       # 记忆API
│
├── store/              # 状态管理 (Zustand)
│   ├── modeStore.ts    # 模式状态
│   ├── knowledgeStore.ts # 知识库状态
│   ├── memoryStore.ts  # 记忆状态
│   └── uiStore.ts      # UI状态
│
├── hooks/              # 自定义Hooks
│   ├── useMode.ts      # 模式管理
│   ├── useKnowledge.ts # 知识库管理
│   ├── useMemory.ts    # 记忆管理
│   └── useChat.ts      # 对话管理
│
├── components/         # 组件库
│   ├── common/         # 通用组件
│   │   ├── StatCard.tsx
│   │   ├── ActionCard.tsx
│   │   ├── EmptyState.tsx
│   │   └── DataChart.tsx
│   └── mode/           # 模式组件
│       ├── ModeSelector.tsx
│       ├── MimicPanel.tsx
│       └── AnalyzePanel.tsx
│
├── pages/              # 页面组件
│   ├── HomePage.tsx    # 首页
│   ├── WorkPage.tsx    # 工作模式
│   ├── LifePage.tsx    # 生活模式
│   ├── KnowledgePage.tsx # 知识库管理
│   ├── MemoryPage.tsx  # 记忆管理
│   ├── ChatPage.tsx    # 对话页面
│   └── ConfigPage.tsx  # 配置页面
│
├── utils/              # 工具函数
│   ├── format.ts       # 格式化工具
│   ├── time.ts         # 时间处理
│   └── validation.ts   # 验证工具
│
└── App.tsx             # 根组件
```

---

## 🎯 核心功能

### 双模式双能力架构

```
           工作模式              生活模式
          ┌─────────┐          ┌─────────┐
模仿我 →  │周报生成 │          │闲聊    │
          │待办整理 │          │记录事件│
          │会议总结 │          │        │
          └─────────┘          └─────────┘
          ┌─────────┐          ┌─────────┐
分析我 →  │项目进度 │          │心情分析│
          │时间分析 │          │兴趣追踪│
          │        │          │生活总结│
          └─────────┘          └─────────┘
```

### 页面路由

| 路径 | 页面 | 功能 |
|------|------|------|
| `/` | 首页 | 场景模式入口、数据统计 |
| `/work` | 工作模式 | 工作场景快速操作 |
| `/life` | 生活模式 | 生活场景快速操作 |
| `/knowledge` | 知识库 | 文档上传、搜索、管理 |
| `/memory` | 记忆管理 | 记忆时间线、搜索、导出 |
| `/chat` | 对话 | 与AI分身对话 |
| `/config` | 配置 | 系统参数配置 |

---

## 💻 开发指南

### 使用模式管理

```typescript
import { useMode } from '@/hooks';

function MyComponent() {
  const { 
    mode,              // 当前模式: 'work' | 'life'
    capability,        // 当前能力: 'mimic' | 'analyze'
    availableActions,  // 可用操作列表
    switchMode,        // 切换模式
  } = useMode();
  
  return (
    <div>
      <p>当前: {mode} - {capability}</p>
      <button onClick={() => switchMode('life')}>
        切换到生活模式
      </button>
    </div>
  );
}
```

### 使用知识库

```typescript
import { useKnowledge } from '@/hooks';

function MyComponent() {
  const { 
    documents,       // 文档列表
    loading,         // 加载状态
    uploadDocument,  // 上传文档
    searchKnowledge, // 搜索知识
  } = useKnowledge();
  
  const handleUpload = async (file: File) => {
    await uploadDocument(file);
  };
  
  return <DocumentList documents={documents} />;
}
```

### 使用记忆管理

```typescript
import { useMemory } from '@/hooks';

function MyComponent() {
  const { 
    memories,        // 记忆列表
    timeline,        // 时间线数据
    searchMemories,  // 搜索记忆
    exportMemories,  // 导出记忆
  } = useMemory();
  
  return <MemoryTimeline timeline={timeline} />;
}
```

---

## 🎨 组件库

### StatCard - 统计卡片

```typescript
<StatCard
  title="知识库文档"
  value={123}
  icon="📚"
  color="#1890ff"
  suffix="个"
  trend="up"
  trendValue="+10%"
  onClick={() => navigate('/knowledge')}
/>
```

### ActionCard - 操作卡片

```typescript
<ActionCard
  title="周报生成"
  description="自动生成本周工作总结"
  icon="📊"
  onClick={handleGenerateReport}
  loading={loading}
/>
```

### EmptyState - 空状态

```typescript
<EmptyState
  title="暂无文档"
  description="点击上传开始构建知识库"
  action={{
    text: "上传文档",
    onClick: handleUpload
  }}
/>
```

---

## 🛠️ 技术栈

- **框架**: React 18 + TypeScript
- **构建**: Vite
- **路由**: React Router v6
- **状态**: Zustand
- **UI库**: Ant Design
- **HTTP**: Axios
- **样式**: CSS-in-JS

---

## 📊 代码统计

- **文件数**: 38个模块
- **代码量**: ~3427行
- **类型定义**: 完整TypeScript支持
- **组件复用**: 高度模块化

---

## 🔧 开发工具

### 推荐VSCode扩展

- ESLint
- Prettier
- TypeScript Vue Plugin (Volar)
- Auto Import

### 代码格式化

```bash
npm run lint
npm run format
```

---

## 📝 开发规范

### 命名规范

- **组件**: PascalCase (HomePage, StatCard)
- **文件**: camelCase (useMode.ts, workAPI.ts)
- **变量**: camelCase (currentMode, handleClick)
- **常量**: UPPER_SNAKE_CASE (API_BASE_URL)

### 导入顺序

```typescript
// 1. React相关
import { useState } from 'react';

// 2. 第三方库
import { Card } from 'antd';

// 3. 类型定义
import type { ModeConfig } from '@/types';

// 4. API和Store
import { useMode } from '@/hooks';

// 5. 工具函数
import { formatTime } from '@/utils';

// 6. 本地组件
import { StatCard } from './StatCard';
```

---

## 🐛 调试技巧

### 查看Store状态

```typescript
import { useModeStore } from '@/store';

// 在组件中
const store = useModeStore.getState();
console.log('Current mode:', store.currentMode);
```

### API调试

所有API调用都有完整的错误处理和日志：

```typescript
try {
  const result = await workAPI.generateWeeklyReport();
  console.log('Report generated:', result);
} catch (error) {
  console.error('Failed to generate:', error);
}
```

---

## 📚 相关文档

- [实施计划](../FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN.md)
- [开发指南](../FRONTEND_DEV_GUIDE.md)
- [完成报告](../FRONTEND_OPTIMIZATION_COMPLETE.md)
- [最终总结](../FRONTEND_OPTIMIZATION_FINAL_SUMMARY.md)

---

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证

---

**维护者**: Another Me Team  
**最后更新**: 2025-11-07
