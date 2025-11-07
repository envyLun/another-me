# 前端优化 - 开发者快速上手指南

> 本指南帮助开发者快速了解已完成的架构，并开始后续开发工作。

---

## 🏗️ 架构概览

```
frontend/src/
├── types/          ✅ TypeScript类型定义（完成）
├── api/            ✅ API客户端层（完成）
├── utils/          ✅ 工具函数库（完成）
├── store/          ✅ Zustand状态管理（完成）
├── hooks/          📝 自定义Hooks（待实施）
├── components/     ⏳ UI组件（待实施）
└── pages/          ⏳ 页面组件（部分待重写）
```

---

## 📦 已完成模块使用示例

### 1. 类型系统

```typescript
// 导入类型
import type { 
  SceneMode, 
  CapabilityType,
  WeeklyReportRequest,
  MoodAnalysisResponse,
  DocumentInfo 
} from '@/types';

// 使用示例
const mode: SceneMode = 'work';
const capability: CapabilityType = 'mimic';
```

### 2. API客户端

```typescript
// 导入API客户端
import { workAPI, lifeAPI, ragAPI, memAPI } from '@/api';

// 工作场景API
const report = await workAPI.generateWeeklyReport({
  start_date: '2024-11-01',
  end_date: '2024-11-07'
});

// 生活场景API
const moodAnalysis = await lifeAPI.analyzeMood({
  mood_entry: '今天心情不错',
  entry_time: new Date().toISOString()
});

// 知识库API
const docs = await ragAPI.getDocuments(1, 20);
await ragAPI.uploadDocument(file);

// 记忆API
const memories = await memAPI.getMemories(50, 0);
await memAPI.exportMemories('json');
```

### 3. 工具函数

```typescript
import { 
  formatFileSize, 
  formatRelativeTime, 
  isValidFileType,
  formatEmotionToEmoji 
} from '@/utils';

// 格式化文件大小
const size = formatFileSize(1024 * 1024); // "1.00 MB"

// 相对时间
const time = formatRelativeTime(new Date('2024-11-06')); // "1天前"

// 验证文件类型
const isValid = isValidFileType(file, ['application/pdf', 'text/*']);

// 情绪转emoji
const emoji = formatEmotionToEmoji('happy'); // "😊"
```

### 4. 状态管理

```typescript
// 导入store
import { 
  useModeStore, 
  useKnowledgeStore, 
  useMemoryStore,
  useUIStore 
} from '@/store';

// 组件中使用
function MyComponent() {
  // 模式状态
  const { currentMode, switchMode, getModeConfig } = useModeStore();
  
  // 知识库状态
  const { 
    documents, 
    loading, 
    uploadDocument,
    loadDocuments 
  } = useKnowledgeStore();
  
  // 记忆状态
  const { 
    memories, 
    timeline, 
    searchMemories 
  } = useMemoryStore();
  
  // UI状态
  const { 
    showNotification, 
    setGlobalLoading 
  } = useUIStore();
  
  // 使用
  const handleUpload = async (file: File) => {
    setGlobalLoading(true, '上传中...');
    try {
      await uploadDocument(file);
      showNotification('success', '上传成功');
    } catch (error) {
      showNotification('error', '上传失败', error.message);
    } finally {
      setGlobalLoading(false);
    }
  };
  
  return <div>...</div>;
}
```

---

## 🎯 开发模式系统

### 模式配置（modeStore）

系统定义了 **2×2 模式矩阵**:

| 场景 ↓ / 能力 → | 模仿我 (mimic) | 分析我 (analyze) |
|----------------|----------------|------------------|
| **工作 (work)** | 周报生成、待办整理、会议总结 | 项目进度、时间分析 |
| **生活 (life)** | 闲聊、记录事件 | 心情分析、兴趣追踪、生活总结 |

### 使用模式系统

```typescript
import { useModeStore } from '@/store';

function ModeExample() {
  const { 
    currentMode,           // 'work' | 'life'
    currentCapability,     // 'mimic' | 'analyze'
    switchMode,
    getModeConfig,
    getAvailableActions    // 获取当前可用操作
  } = useModeStore();
  
  const modeConfig = getModeConfig();
  // { mode: 'work', label: '工作', icon: '💼', color: '#1890ff' }
  
  const actions = getAvailableActions();
  // [{ key: 'weekly_report', label: '周报生成', icon: '📊', ... }]
  
  return (
    <div>
      <h2>{modeConfig.icon} {modeConfig.label}</h2>
      <button onClick={() => switchMode('life')}>切换到生活模式</button>
      
      {actions.map(action => (
        <button key={action.key}>
          {action.icon} {action.label}
        </button>
      ))}
    </div>
  );
}
```

---

## 🛠️ 待实施组件示例

### 通用组件 - StatCard

```typescript
// components/common/StatCard.tsx
import { Card, Statistic } from 'antd';

interface StatCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
  trend?: 'up' | 'down' | 'stable';
}

export function StatCard({ title, value, icon, color, trend }: StatCardProps) {
  return (
    <Card hoverable>
      <Statistic
        title={title}
        value={value}
        prefix={<span style={{ color }}>{icon}</span>}
        valueStyle={{ color }}
      />
      {trend && <TrendIndicator trend={trend} />}
    </Card>
  );
}
```

### 知识库组件 - DocumentList

```typescript
// components/knowledge/DocumentList.tsx
import { Table, Button, Space } from 'antd';
import { useKnowledgeStore } from '@/store';
import { formatFileSize, formatRelativeTime } from '@/utils';

export function DocumentList() {
  const { 
    documents, 
    loading, 
    deleteDocument,
    loadDocuments 
  } = useKnowledgeStore();
  
  const columns = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => formatFileSize(size),
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      render: (time: string) => formatRelativeTime(time),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button type="link" onClick={() => handleView(record.id)}>
            查看
          </Button>
          <Button 
            type="link" 
            danger 
            onClick={() => deleteDocument(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];
  
  return (
    <Table
      dataSource={documents}
      columns={columns}
      loading={loading}
      rowKey="id"
      pagination={{
        onChange: (page) => loadDocuments(page),
      }}
    />
  );
}
```

### 工作模式页面 - WorkPage

```typescript
// pages/WorkPage.tsx
import { Tabs, Space } from 'antd';
import { useModeStore } from '@/store';
import { MimicPanel } from '@/components/mode/MimicPanel';
import { AnalyzePanel } from '@/components/mode/AnalyzePanel';

export default function WorkPage() {
  const { 
    currentCapability, 
    switchCapability,
    getModeConfig 
  } = useModeStore();
  
  const modeConfig = getModeConfig();
  
  return (
    <div>
      <h1>{modeConfig.icon} {modeConfig.label}模式</h1>
      
      <Tabs
        activeKey={currentCapability}
        onChange={(key) => switchCapability(key as CapabilityType)}
        items={[
          {
            key: 'mimic',
            label: '🤖 模仿我',
            children: <MimicPanel />,
          },
          {
            key: 'analyze',
            label: '🔍 分析我',
            children: <AnalyzePanel />,
          },
        ]}
      />
    </div>
  );
}
```

---

## 📝 开发规范

### 1. 组件命名

- **页面组件**: `HomePage.tsx`, `WorkPage.tsx` (PascalCase + Page后缀)
- **业务组件**: `DocumentList.tsx`, `MemoryTimeline.tsx` (PascalCase)
- **通用组件**: `StatCard.tsx`, `EmptyState.tsx` (PascalCase)

### 2. 文件组织

```
components/
├── common/        # 通用组件（可跨项目复用）
├── mode/          # 模式相关组件
├── knowledge/     # 知识库组件
├── memory/        # 记忆组件
└── chat/          # 对话组件
```

### 3. 导入顺序

```typescript
// 1. React相关
import { useState, useEffect } from 'react';

// 2. 第三方库
import { Card, Button } from 'antd';

// 3. 类型定义
import type { DocumentInfo } from '@/types';

// 4. API客户端
import { ragAPI } from '@/api';

// 5. Store和Hooks
import { useKnowledgeStore } from '@/store';

// 6. 工具函数
import { formatFileSize } from '@/utils';

// 7. 本地组件
import { StatCard } from './StatCard';
```

### 4. 类型定义

```typescript
// Props类型定义
interface MyComponentProps {
  title: string;
  value?: number;
  onAction: (id: string) => void;
}

// 组件实现
export function MyComponent({ title, value = 0, onAction }: MyComponentProps) {
  // ...
}
```

### 5. 错误处理

```typescript
const handleAction = async () => {
  const { setError, showNotification } = useUIStore();
  
  try {
    setGlobalLoading(true);
    await someAPI.doSomething();
    showNotification('success', '操作成功');
  } catch (error: any) {
    const message = error.message || '操作失败';
    setError(message);
    showNotification('error', '操作失败', message);
  } finally {
    setGlobalLoading(false);
  }
};
```

---

## 🚀 快速开始步骤

### Step 1: 熟悉已有架构

1. 阅读类型定义: `frontend/src/types/*`
2. 了解API客户端: `frontend/src/api/*`
3. 查看状态管理: `frontend/src/store/*`

### Step 2: 创建自定义Hooks

参考 `FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN.md` 中的Hooks设计

### Step 3: 实现通用组件

优先实现:
- `StatCard` - 统计卡片
- `EmptyState` - 空状态
- `ActionCard` - 操作卡片

### Step 4: 重写核心页面

按优先级:
1. KnowledgePage (知识库管理)
2. MemoryPage (记忆管理)
3. WorkPage (工作模式)
4. LifePage (生活模式)

---

## 📚 参考文档

- **设计文档**: 项目根目录 `设计文档-前端优化.md`
- **实施计划**: `FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN.md`
- **进度报告**: `FRONTEND_OPTIMIZATION_PROGRESS.md`
- **后端API**: `backend/app/api/v1/` 路由定义

---

## 💡 开发建议

### 性能优化

1. 使用 `React.memo` 包裹纯展示组件
2. 使用 `useMemo` 缓存计算结果
3. 列表使用虚拟滚动（react-window）
4. 图片懒加载

### 用户体验

1. 加载状态（Skeleton, Spin）
2. 错误提示（message, notification）
3. 空状态引导（EmptyState）
4. 操作确认（Modal.confirm）

### 代码质量

1. TypeScript严格模式
2. ESLint代码检查
3. Prettier格式化
4. 单元测试（Jest + React Testing Library）

---

## ❓ 常见问题

**Q: 如何添加新的场景模式？**

A: 在 `modeStore.ts` 中扩展 `MODE_CONFIGS` 和操作配置数组。

**Q: 如何扩展API客户端？**

A: 在对应的API文件（如 `workAPI.ts`）中添加新方法，同时更新类型定义。

**Q: Store中的数据如何持久化？**

A: 使用Zustand的 `persist` 中间件，已在 `modeStore` 和 `uiStore` 中配置。

**Q: 如何处理API错误？**

A: 统一使用 `try-catch`，在catch块中调用 `useUIStore().showNotification()`。

---

**最后更新**: 2025-11-07  
**维护者**: 开发团队
