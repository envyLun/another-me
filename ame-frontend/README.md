# Another Me Frontend 🎨

> 基于 React 18 + TypeScript + Vite 的 AI 数字分身前端系统

[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF)](https://vitejs.dev/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-5.12-1890FF)](https://ant.design/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 📖 项目简介

Another Me 前端是一个现代化的 Web 应用，提供直观的用户界面用于管理知识库（RAG）、记忆模仿（MEM）、工作和生活场景等功能。采用最新的前端技术栈，注重用户体验和开发效率。

### ✨ 核心特性

- ✅ **TypeScript 全栈类型安全** - 从 API 到 UI 的完整类型覆盖
- ✅ **Ant Design 5 UI 组件库** - 企业级 UI 设计语言
- ✅ **Zustand 状态管理** - 轻量级、高性能的状态管理
- ✅ **React Router v6** - 声明式路由导航
- ✅ **SSE 流式对话** - 实时流式 AI 对话体验
- ✅ **响应式设计** - 完美适配桌面和移动设备
- ✅ **模块化架构** - 清晰的代码组织和职责分离
- ✅ **Vite 极速构建** - 毫秒级热更新
- ✅ **Tailwind CSS** - 原子化 CSS 框架

---

## 🏗️ 项目架构

### 📁 目录结构

```
ame-frontend/
├── public/                     # 静态资源
│   ├── logo.png               # 项目 Logo
│   └── LOGO_INSTRUCTION.md    # Logo 使用说明
├── src/
│   ├── api/                   # API 客户端层 (27 个接口)
│   │   ├── client.ts          # 核心 HTTP 客户端 + SSE 流式处理
│   │   ├── workAPI.ts         # 工作场景 API (4 个接口)
│   │   ├── lifeAPI.ts         # 生活场景 API (5 个接口)
│   │   ├── memAPI.ts          # 记忆模仿 API
│   │   ├── ragAPI.ts          # 知识库 API
│   │   ├── graphAPI.ts        # 知识图谱 API (6 个接口)
│   │   └── index.ts           # 统一导出
│   ├── components/            # React 组件 (20+ 个)
│   │   ├── common/            # 通用组件 (7 个)
│   │   │   ├── ActionCard.tsx         # 操作卡片
│   │   │   ├── AnalysisResult.tsx     # 分析结果展示
│   │   │   ├── DataChart.tsx          # 数据图表
│   │   │   ├── EmptyState.tsx         # 空状态占位
│   │   │   ├── ErrorBoundary.tsx      # 错误边界
│   │   │   ├── GraphVisualization.tsx # 图谱可视化
│   │   │   ├── StatCard.tsx           # 统计卡片
│   │   │   └── index.ts
│   │   └── mode/              # 场景模式组件 (11 个)
│   │       ├── AnalyzePanel.tsx           # 分析面板
│   │       ├── FileUploader.tsx           # 文件上传
│   │       ├── LifeEventRecorder.tsx      # 生活事件记录
│   │       ├── MeetingSummaryGenerator.tsx # 会议总结生成器
│   │       ├── MessageInput.tsx           # 消息输入框
│   │       ├── MessageList.tsx            # 消息列表
│   │       ├── MimicPanel.tsx             # 模仿面板
│   │       ├── ModeSelector.tsx           # 场景选择器
│   │       ├── SearchPanel.tsx            # 搜索面板
│   │       ├── TodoOrganizer.tsx          # 待办整理器
│   │       ├── WeeklyReportGenerator.tsx  # 周报生成器
│   │       └── index.ts
│   ├── hooks/                 # 自定义 Hooks (6 个)
│   │   ├── useChat.ts         # 对话逻辑管理
│   │   ├── useKnowledge.ts    # 知识库操作
│   │   ├── useMediaQuery.ts   # 响应式断点检测
│   │   ├── useMemory.ts       # 记忆管理
│   │   ├── useMode.ts         # 场景模式切换
│   │   ├── useStreamChat.ts   # SSE 流式对话
│   │   └── index.ts
│   ├── pages/                 # 页面组件 (8 个)
│   │   ├── HomePage.tsx       # 首页 - 系统概览
│   │   ├── ChatPage.tsx       # MEM 对话页
│   │   ├── KnowledgePage.tsx  # RAG 知识库页
│   │   ├── GraphPage.tsx      # 知识图谱页
│   │   ├── MemoryPage.tsx     # 记忆管理页
│   │   ├── WorkPage.tsx       # 工作场景页
│   │   ├── LifePage.tsx       # 生活场景页
│   │   └── ConfigPage.tsx     # 配置页
│   ├── store/                 # Zustand 状态管理 (6 个 Store)
│   │   ├── chatStore.ts       # 对话状态
│   │   ├── configStore.ts     # 配置状态 (持久化)
│   │   ├── knowledgeStore.ts  # 知识库状态
│   │   ├── memoryStore.ts     # 记忆状态
│   │   ├── modeStore.ts       # 场景模式状态 (持久化)
│   │   ├── uiStore.ts         # UI 状态 (持久化)
│   │   └── index.ts
│   ├── types/                 # TypeScript 类型定义
│   │   ├── api.ts             # API 接口类型 (20+ 个接口)
│   │   ├── app.ts             # 应用通用类型
│   │   ├── mode.ts            # 场景模式类型
│   │   ├── work.ts            # 工作场景类型 (6 个接口)
│   │   ├── life.ts            # 生活场景类型 (12 个接口)
│   │   └── index.ts
│   ├── utils/                 # 工具函数
│   │   ├── errorHandler.ts    # 统一错误处理
│   │   ├── format.ts          # 格式化工具
│   │   ├── helpers.ts         # 辅助函数
│   │   ├── time.ts            # 时间处理
│   │   ├── validation.ts      # 数据验证
│   │   └── index.ts
│   ├── styles/                # 样式文件
│   │   ├── globals.css        # 全局样式
│   │   └── theme.ts           # 主题配置
│   ├── App.tsx                # 根组件 + 路由配置
│   └── main.tsx               # 应用入口
├── index.html                 # HTML 模板
├── package.json               # 依赖配置
├── vite.config.ts             # Vite 构建配置
├── tsconfig.json              # TypeScript 配置
├── tailwind.config.js         # Tailwind CSS 配置
├── Dockerfile                 # Docker 镜像配置
├── run.sh                     # 快速启动脚本
└── README.md                  # 项目文档
```

### 🔀 架构分层

```
┌─────────────────────────────────────┐
│        Pages Layer (路由页面)        │
│   HomePage, ChatPage, WorkPage...  │
└─────────────────────────────────────┘
              ↓ 使用
┌─────────────────────────────────────┐
│     Components Layer (UI 组件)      │
│   Common Components + Mode Comps   │
└─────────────────────────────────────┘
              ↓ 调用
┌─────────────────────────────────────┐
│  Business Logic Layer (业务逻辑)    │
│   Custom Hooks + Zustand Stores    │
└─────────────────────────────────────┘
              ↓ 请求
┌─────────────────────────────────────┐
│      API Client Layer (API 层)      │
│   Axios + SSE Stream Handler       │
└─────────────────────────────────────┘
              ↓ HTTP/SSE
┌─────────────────────────────────────┐
│      Backend API (后端服务)          │
│   FastAPI + AME Engine             │
└─────────────────────────────────────┘
```

### 🎯 设计模式

- **单一职责原则**: 每个组件/Hook 只负责一个功能
- **组合优于继承**: 使用 Hooks 和组件组合
- **依赖注入**: 通过 Props 和 Context 传递依赖
- **观察者模式**: Zustand 状态订阅
- **工厂模式**: API Client 创建

---

## 🔌 API 接口规范

### 配置管理
- `POST /config/save` - 保存配置
- `GET /config/load` - 加载配置
- `POST /config/test` - 测试配置

### RAG 知识库
- `POST /rag/upload` - 上传文档
- `POST /rag/search` - 检索知识
- `GET /rag/documents` - 文档列表
- `DELETE /rag/documents/{id}` - 删除文档
- `GET /rag/stats` - 统计信息

### MEM 记忆模仿
- `POST /mem/chat` - 流式对话 (SSE)
- `POST /mem/chat-sync` - 同步对话
- `POST /mem/learn` - 学习对话
- `GET /mem/memories` - 记忆列表
- `DELETE /mem/memories/{id}` - 删除记忆

### 工作场景
- `POST /work/weekly-report` - 生成周报
- `POST /work/organize-todos` - 整理待办
- `POST /work/summarize-meeting` - 会议总结
- `POST /work/track-project` - 项目进度

### 生活场景
- `POST /life/analyze-mood` - 心情分析
- `GET /life/track-interests` - 兴趣追踪
- `POST /life/life-summary` - 生活总结
- `POST /life/suggestions` - 生活建议
- `POST /life/record-event` - 记录事件

### 知识图谱
- `GET /graph/entity/{name}` - 实体图谱
- `GET /graph/document/{id}` - 文档图谱
- `GET /graph/stats` - 图谱统计
- `POST /graph/query` - Cypher 查询
- `POST /graph/search` - 搜索实体

---

## 🎨 用户交互流程

### 首次使用

1. 访问首页 → 检查配置状态
2. 未配置 → 跳转配置页
3. 输入 API Key → 测试配置
4. 保存配置 → 开始使用

### 知识库管理

1. 上传文档 → 文件验证
2. 后端处理 → 向量化存储
3. 更新统计 → 显示成功

### MEM 对话

1. 输入消息 → 发送请求
2. 检索记忆 → LLM 生成
3. 流式返回 → 实时显示

### 工作场景

**周报生成**: 选择时间 → 分析记录 → 生成报告  
**待办整理**: 输入列表 → AI 分类 → 展示结果  
**会议总结**: 输入笔记 → 提取要点 → 生成总结

### 生活场景

**心情分析**: 写日记 → 情感识别 → 提供建议  
**兴趣追踪**: 选择时间 → 分析记录 → 生成图表

---

## 💾 状态管理

### Zustand Stores

| Store | 用途 | 持久化 |
|-------|------|--------|
| ConfigStore | API 配置 | ✅ |
| ChatStore | 对话历史 | ❌ |
| KnowledgeStore | 知识库 | ❌ |
| MemoryStore | 记忆数据 | ❌ |
| ModeStore | 场景模式 | ✅ |
| UIStore | UI 设置 | ✅ |

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2 | UI 框架 |
| TypeScript | 5.2 | 类型系统 |
| Vite | 5.0 | 构建工具 |
| Ant Design | 5.12 | UI 组件 |
| Zustand | 4.4 | 状态管理 |
| Axios | 1.6 | HTTP 客户端 |

---

## 🚀 快速开始

### 环境要求

- **Node.js**: >= 18.0.0
- **npm**: >= 9.0.0
- **操作系统**: macOS / Linux / Windows
- **浏览器**: Chrome >= 90, Firefox >= 88, Safari >= 14

### 安装步骤

```bash
# 1. 克隆项目（如果从 Git 克隆）
git clone https://github.com/kailiangshang/another-me.git
cd another-me/ame-frontend

# 2. 安装依赖
npm install
# 或使用 yarn
yarn install
# 或使用 pnpm (推荐，更快)
pnpm install

# 3. 启动开发服务器
npm run dev
# 访问 http://localhost:5173
```

### 开发模式

```bash
# 启动开发服务器（热更新）
npm run dev

# 启动并指定端口
vite --port 3000

# 启动并暴露到局域网
vite --host
```

访问地址:
- 本地: http://localhost:5173
- 局域网: http://192.168.x.x:5173

### 生产构建

```bash
# 类型检查 + 构建
npm run build

# 输出目录: dist/
# 包含:
# - index.html
# - assets/ (JS, CSS, 图片等)
```

### 预览生产构建

```bash
# 预览构建结果
npm run preview
# 访问 http://localhost:4173
```

### 代码检查

```bash
# ESLint 检查
npm run lint

# 自动修复
npm run lint -- --fix
```

### 快速启动脚本

```bash
# 使用项目提供的启动脚本
./run.sh
```

---

## 🔧 核心功能实现

### SSE 流式对话

```typescript
await apiClient.chatStream(
  message,
  (chunk) => setResponse(prev => prev + chunk),
  (error) => console.error(error),
  () => setStreaming(false)
);
```

### 文件上传

```typescript
const result = await apiClient.uploadDocument(file);
```

### 状态持久化

```typescript
persist(
  (set) => ({ /* state */ }),
  { name: 'store-key' }
)
```

---

## 📊 数据流设计

### 请求流程
```
Component → Hook → API Client → Backend → Response → Store → Re-render
```

### SSE 流式数据
```
Component → API Client → SSE Stream → Callback → Update UI
```

---

## 🎯 后端接口需求清单

### 必需实现的端点

#### 配置 (Config)
- ✅ `GET /health`
- ✅ `POST /config/save`
- ✅ `GET /config/load`
- ✅ `POST /config/test` (需支持 Embedding 测试)

#### RAG
- ✅ `POST /rag/upload` (支持 multipart/form-data)
- ✅ `POST /rag/search`
- ✅ `GET /rag/documents`
- ✅ `DELETE /rag/documents/{id}`
- ✅ `GET /rag/stats`

#### MEM
- ✅ `POST /mem/chat` (SSE 流式响应)
- ✅ `POST /mem/chat-sync`
- ✅ `POST /mem/learn`
- ✅ `GET /mem/memories`
- ✅ `DELETE /mem/memories/{id}`

#### 工作场景 (Work)
- ⚠️ `POST /work/weekly-report`
- ⚠️ `POST /work/organize-todos`
- ⚠️ `POST /work/summarize-meeting`
- ⚠️ `POST /work/track-project`

#### 生活场景 (Life)
- ⚠️ `POST /life/analyze-mood`
- ⚠️ `GET /life/track-interests`
- ⚠️ `POST /life/life-summary`
- ⚠️ `POST /life/suggestions`
- ⚠️ `POST /life/record-event`

#### 知识图谱 (Graph)
- ⚠️ `GET /graph/entity/{name}`
- ⚠️ `GET /graph/document/{id}`
- ⚠️ `GET /graph/stats`
- ⚠️ `POST /graph/query`
- ⚠️ `POST /graph/search`

**图例**: ✅ 已实现 | ⚠️ 待实现

---

## 📝 类型定义规范

### API 配置 (src/types/api.ts)

```typescript
/** API 配置接口 */
interface APIConfig {
  api_key: string;              // OpenAI API Key
  base_url: string;             // API 基础 URL
  model: string;                // LLM 模型名称
  embedding_model?: string;     // Embedding 模型名称
  embedding_dimension?: number; // Embedding 向量维度
}

/** 配置测试结果 */
interface ConfigTestResult {
  success: boolean;
  message: string;
  model_available?: boolean;        // LLM 模型是否可用
  embedding_available?: boolean;    // Embedding 模型是否可用
  embedding_dimension?: number;     // 实际的向量维度
}
```

### 基础响应 (src/types/api.ts)

```typescript
/** 基础响应接口 */
interface BaseResponse {
  success: boolean;
  message: string;
  data?: any;
}

/** 分页响应接口 */
interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;          // 当前页码
    page_size: number;     // 每页数量
    total: number;         // 总记录数
    total_pages: number;   // 总页数
  };
  timestamp: string;
}
```

### 知识库类型 (src/types/api.ts)

```typescript
/** 文档信息 */
interface DocumentInfo {
  id: string;
  filename: string;
  size: number;
  upload_time: string;
  chunk_count?: number;
}

/** 搜索结果 */
interface SearchResult {
  content: string;
  score: number;
  metadata: Record<string, any>;
}

/** RAG 统计信息 */
interface RAGStats {
  document_count: number;   // 文档总数
  total_chunks: number;     // 分块总数
  total_size: number;       // 总大小（字节）
}
```

### 对话类型 (src/types/api.ts)

```typescript
/** 聊天消息 */
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

/** 记忆项 */
interface Memory {
  id: string;
  content: string;
  timestamp: string;
  metadata: Record<string, any>;
}
```

### 工作场景类型 (src/types/work.ts)

```typescript
/** 待办事项 */
interface TodoItem {
  id: string;
  title: string;
  description?: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed';
  deadline?: string;
  dependencies?: string[];
  created_at: string;
}

/** 周报响应 */
interface WeeklyReportResponse {
  success: boolean;
  report: string;
  insights?: {
    key_tasks?: string[];
    achievements?: string[];
    challenges?: string[];
    time_stats?: TimeStats;
  };
  timestamp: string;
}
```

### 生活场景类型 (src/types/life.ts)

```typescript
/** 心情分析响应 */
interface MoodAnalysisResponse {
  success: boolean;
  analysis: string;
  emotion?: string;
  suggestions?: string[];
  timestamp: string;
}

/** 兴趣追踪响应 */
interface InterestTrackingResponse {
  success: boolean;
  interests: Array<{
    name: string;
    frequency: number;
    trend: 'rising' | 'stable' | 'declining';
  }>;
  summary: string;
  timestamp: string;
}
```

---

## 🔒 安全考虑

- API Key 存储在 localStorage（仅前端展示用）
- 实际配置保存在后端
- 配置加载时隐藏敏感信息（显示前 8 位）
- HTTPS 传输加密

---

## 📈 性能优化

- GET 请求缓存 5 分钟
- 组件懒加载 (React.lazy)
- 使用 React.memo 减少重渲染
- 虚拟滚动（长列表）
- 图片懒加载

---

## 🐛 错误处理

### 统一错误拦截

```typescript
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // 统一处理错误
    console.error('API Error:', error.response?.data?.detail);
    return Promise.reject(error);
  }
);
```

### ErrorBoundary

所有页面组件都被 `ErrorBoundary` 包裹，捕获运行时错误。

---

## 🐳 Docker 部署

### 快速部署

使用提供的一键部署脚本：

```bash
# 默认使用 80 端口
./deploy.sh

# 指定端口
./deploy.sh 3000

# 访问应用
open http://localhost:80
```

### 手动部署

#### 1. 构建镜像

```bash
# 在 ame-frontend 目录下
cd ame-frontend

# 构建镜像
docker build -t another-me-frontend:latest .

# 查看镜像
docker images | grep another-me-frontend
```

#### 2. 运行容器

```bash
# 基础运行（端口 80）
docker run -d \
  --name another-me-frontend \
  -p 80:80 \
  --restart unless-stopped \
  another-me-frontend:latest

# 使用其他端口
docker run -d \
  --name another-me-frontend \
  -p 3000:80 \
  --restart unless-stopped \
  another-me-frontend:latest

# 访问: http://localhost:80 或 http://localhost:3000
```

#### 3. 管理容器

```bash
# 查看运行状态
docker ps | grep another-me-frontend

# 查看日志
docker logs another-me-frontend
docker logs -f another-me-frontend  # 实时日志

# 停止/启动/重启
docker stop another-me-frontend
docker start another-me-frontend
docker restart another-me-frontend

# 删除容器
docker rm -f another-me-frontend
```

### Docker 镜像说明

- **基础镜像**: node:18-alpine + nginx:alpine
- **构建方式**: 多阶段构建，最终镜像小于 50MB
- **端口**: 80 (容器内)
- **自动重启**: 支持 `--restart unless-stopped`
- **健康检查**: 自动检测服务状态
- **API 代理**: 自动代理 `/api/` 到 `host.docker.internal:8000`

### 故障排查

```bash
# 端口占用
lsof -i :80
# 使用其他端口: ./deploy.sh 8080

# 构建失败
docker build --no-cache -t another-me-frontend .

# 容器启动失败
docker logs another-me-frontend

# 清理旧镜像
docker image prune -a
```

---

## 🔧 环境变量配置

### 开发环境 (.env.development)

```bash
# API 地址
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用配置
VITE_APP_NAME=Another Me
VITE_APP_VERSION=1.0.0

# 调试模式
VITE_DEBUG=true
```

### 生产环境 (.env.production)

```bash
# API 地址
VITE_API_BASE_URL=/api/v1

# 应用配置
VITE_APP_NAME=Another Me
VITE_APP_VERSION=1.0.0

# 调试模式
VITE_DEBUG=false
```

---

## 🧪 测试

### 单元测试（计划）

```bash
# 运行测试
npm run test

# 测试覆盖率
npm run test:coverage
```

### E2E 测试（计划）

```bash
# Playwright E2E 测试
npm run test:e2e
```

---

## 📊 性能监控

### 构建分析

```bash
# 分析构建包大小
npm run build -- --report

# 使用 vite-bundle-visualizer
npm install --save-dev vite-bundle-visualizer
```

### 性能指标

- **首屏加载**: < 2s
- **热更新**: < 100ms
- **构建时间**: < 30s
- **包大小**: < 500KB (gzip)

---

## 🐛 常见问题

### 1. 端口被占用

```bash
# 查看 5173 端口占用
lsof -i :5173

# 杀死占用进程
kill -9 <PID>

# 或使用其他端口
vite --port 3000
```

### 2. 依赖安装失败

```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 3. TypeScript 类型错误

```bash
# 重新生成类型
npm run build

# 检查 tsconfig.json 配置
```

### 4. API 请求失败

检查 Vite 代理配置 (`vite.config.ts`):
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // 后端地址
      changeOrigin: true,
    },
  },
}
```

### 5. 热更新不生效

```bash
# 重启开发服务器
npm run dev

# 清除浏览器缓存
# Chrome: Ctrl/Cmd + Shift + R
```

---

## 📚 学习资源

### 官方文档

- [React 官方文档](https://react.dev/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Vite 官方文档](https://vitejs.dev/)
- [Ant Design 官方文档](https://ant.design/)
- [Zustand 官方文档](https://zustand-demo.pmnd.rs/)

### 推荐阅读

- [React Hooks 最佳实践](https://react.dev/reference/react)
- [TypeScript 类型体操](https://github.com/type-challenges/type-challenges)
- [Vite 性能优化](https://vitejs.dev/guide/performance.html)

---

## 🤝 贡献指南

### 提交流程

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

### 代码规范

- 遵循 ESLint 规则
- 使用 TypeScript 严格模式
- 组件命名使用 PascalCase
- 函数命名使用 camelCase
- 常量命名使用 UPPER_SNAKE_CASE
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)

### Commit 消息格式

```
type(scope): subject

[optional body]

[optional footer]
```

类型 (type):
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

示例:
```
feat(chat): add SSE stream support

Implement Server-Sent Events for real-time chat

Closes #123
```

---

## 🌐 国际化支持

### 当前支持
- ✅ 中文 (zh-CN)

### 计划支持
- ⏳ 英文 (en-US)
- ⏳ 日文 (ja-JP)

---

## 📞 联系方式

- **项目地址**: https://github.com/kailiangshang/another-me
- **文档地址**: https://docs.another-me.ai
- **问题反馈**: https://github.com/kailiangshang/another-me/issues
- **讨论区**: https://github.com/kailiangshang/another-me/discussions

---

## 📜 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢以下开源项目:
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Ant Design](https://ant.design/)
- [Zustand](https://github.com/pmndrs/zustand)
- [Axios](https://axios-http.com/)

---

## 📈 项目统计

- **代码行数**: ~8,000 行
- **组件数量**: 20+ 个
- **API 接口**: 27 个
- **类型定义**: 50+ 个
- **自定义 Hooks**: 6 个
- **状态 Store**: 6 个

---

**最后更新**: 2025-01-07  
**维护者**: Another Me Team  
**版本**: 1.0.0
