# Another Me - 后端系统设计文档

**版本**: 2.0.0  
**日期**: 2025-01-15

---

## 1. 概述

### 1.1 后端职责

Another Me 后端基于 FastAPI 构建，作为前端与 AME 引擎的桥梁：

- **API 网关**: 提供 RESTful API 和 SSE 流式接口
- **业务编排**: 协调 AME 引擎完成复杂业务逻辑
- **场景服务**: 实现工作/生活两大场景的智能辅助功能
- **数据管理**: 管理双存储架构（Faiss + FalkorDB）

### 1.2 技术栈

```yaml
框架: FastAPI 0.104+
语言: Python 3.11+
异步: asyncio
验证: Pydantic 2.0+
部署: Uvicorn + Docker
```

### 1.3 架构层次

```
Frontend (React)
       ↓
API Layer (FastAPI Routes)
       ↓
Service Layer (Business Logic)
       ↓
AME Engine (MimicEngine, AnalyzeEngine)
       ↓
Storage (Faiss + FalkorDB)
```

---

## 2. API Layer 设计

### 2.1 路由模块

```
backend/app/api/v1/
├── work.py     # 工作场景
├── life.py     # 生活场景
├── rag.py      # 知识库
├── mem.py      # 记忆对话
└── config.py   # 配置管理
```

### 2.2 Work API

**端点**:
```python
POST /api/v1/work/weekly-report      # 周报生成
POST /api/v1/work/daily-report       # 日报生成
POST /api/v1/work/organize-todos     # 待办整理
POST /api/v1/work/summarize-meeting  # 会议总结
POST /api/v1/work/track-project      # 项目追踪
```

**示例**:
```python
@router.post("/weekly-report")
async def generate_weekly_report(
    request: WeeklyReportRequest,
    service: WorkService = Depends(get_work_service)
):
    """生成工作周报"""
    return await service.generate_weekly_report(
        start_date=request.start_date,
        end_date=request.end_date
    )
```

### 2.3 Life API

**端点**:
```python
POST /api/v1/life/analyze-mood       # 心情分析
GET  /api/v1/life/track-interests    # 兴趣追踪
POST /api/v1/life/life-summary       # 生活总结
POST /api/v1/life/suggestions        # 生活建议
POST /api/v1/life/record-event       # 记录事件
```

### 2.4 RAG API

**端点**:
```python
POST   /api/v1/rag/upload           # 上传文档
POST   /api/v1/rag/search           # 检索知识
POST   /api/v1/rag/ask              # 智能问答
GET    /api/v1/rag/documents        # 文档列表
DELETE /api/v1/rag/documents/{id}   # 删除文档
```

### 2.5 MEM API

**端点**:
```python
POST /api/v1/mem/chat               # 流式对话（SSE）
POST /api/v1/mem/chat-sync          # 同步对话
POST /api/v1/mem/learn              # 学习对话
GET  /api/v1/mem/memories           # 记忆列表
```

**SSE 流式实现**:
```python
@router.post("/chat")
async def chat_stream(request: ChatRequest):
    async def event_generator():
        async for chunk in service.chat_stream(request.message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

---

## 3. Service Layer 设计

### 3.1 WorkService

**职责**: 工作效率工具

```python
class WorkService:
    def __init__(self):
        self.llm_caller = LLMCaller(...)
        self.repository = HybridRepository(...)
        self.analyzer = AnalyzeEngine(...)
        self.mimic = MimicEngine(...)
    
    async def generate_weekly_report(
        self, start_date, end_date
    ) -> Dict:
        """
        周报生成流程:
        1. 检索工作记录（Faiss + Falkor）
        2. 分析关键任务和成果
        3. 用户风格撰写周报
        """
        # 检索
        logs = await self._get_work_logs(start_date, end_date)
        
        # 分析
        insights = await self.analyzer.extract_insights(
            logs, "weekly_summary"
        )
        
        # 生成
        report = await self.mimic.generate_report(
            template="weekly_report",
            data=insights,
            tone="professional"
        )
        
        return {"report": report, "logs_count": len(logs)}
    
    async def organize_todos(self, todos: List[str]) -> Dict:
        """
        待办整理流程:
        1. 图谱分析任务依赖
        2. 优先级排序
        3. 用户风格分类
        """
        graph = await self.analyzer.analyze_task_dependencies(todos)
        prioritized = await self.analyzer.prioritize_tasks(graph)
        organized = await self.mimic.organize_by_user_style(prioritized)
        
        return {"organized_todos": organized}
```

### 3.2 LifeService

**职责**: 生活陪伴与记录

```python
class LifeService:
    async def analyze_mood(self, mood_entry, entry_time) -> Dict:
        """
        心情分析流程:
        1. LLM 深度情绪分析
        2. 存储到永久记忆
        """
        analysis = await self.llm_caller.call(
            messages=[{"role": "user", "content": mood_entry}]
        )
        
        doc = Document(
            content=mood_entry,
            doc_type=DocumentType.LIFE_RECORD,
            retention_type=MemoryRetentionType.PERMANENT
        )
        await self.repository.create(doc)
        
        return {"analysis": analysis}
    
    async def track_interests(self, period_days) -> Dict:
        """
        兴趣追踪流程:
        1. 时间范围检索
        2. 提取兴趣关键词
        3. 图谱演化分析
        """
        records = await self._get_life_records(period_days)
        interests = await self.analyzer.extract_insights(
            records, "interests"
        )
        trends = await self.analyzer.analyze_interest_trends(interests)
        
        return {"interests": interests, "trends": trends}
```

### 3.3 RAGService

**职责**: 知识库管理

```python
class RAGService:
    async def upload_document(self, file_path, filename) -> Dict:
        """
        文档上传流程:
        1. 解析文档（PDF/TXT/DOCX）
        2. 分块处理
        3. 生成 Embedding
        4. 存储到 Faiss
        """
        content = await self.knowledge_base.parse_document(file_path)
        chunks = await self.knowledge_base.chunk_text(content)
        
        for chunk in chunks:
            doc = Document(content=chunk, doc_type=DocumentType.RAG_KNOWLEDGE)
            await self.repository.create(doc)
        
        return {"chunks_count": len(chunks)}
    
    async def ask_question_stream(self, question) -> AsyncIterator[str]:
        """
        问答流程:
        1. 检索相关知识
        2. 构建 RAG Prompt
        3. 流式生成答案
        """
        results = await self.repository.vector_search(question, top_k=5)
        context_docs = [r.document.content for r in results]
        
        async for chunk in self.rag_generator.generate_stream(
            question, context_docs
        ):
            yield chunk
```

### 3.4 MEMService

**职责**: 记忆对话

```python
class MEMService:
    async def chat_stream(self, message) -> AsyncIterator[str]:
        """
        对话流程:
        1. 检索相似对话
        2. 风格化 Prompt
        3. 流式生成
        """
        similar = await self.repository.vector_search(message, top_k=5)
        
        async for chunk in self.mimic_engine.generate_response_stream(
            message, similar, temperature=0.8
        ):
            yield chunk
```

---

## 4. 双存储协同

### 4.1 Faiss 向量存储

**场景**:
- 短期工作/生活记录（最近 30 天）
- 实时对话检索
- 知识库文档检索

**数据隔离**:
```
data/faiss/
├── work.index    # 工作数据
├── life.index    # 生活数据
├── rag.index     # 知识库
└── mem.index     # 对话记忆
```

### 4.2 FalkorDB 图谱存储

**场景**:
- 长期知识图谱
- 任务依赖分析
- 兴趣演化追踪

**图谱结构**:
```cypher
(Person)-[:COLLABORATE_ON]->(Project)
(Task)-[:DEPENDS_ON]->(Task)
(Person)-[:INTERESTED_IN]->(Interest)
```

### 4.3 混合检索

```python
# 周报生成：Faiss + Falkor
faiss_results = await repository.vector_search("工作日志", top_k=50)
graph_results = await repository.graph_search(
    "MATCH (log)-[:RELATED_TO]->(p:Project) RETURN p"
)
combined = merge_results(faiss_results, graph_results)
```

---

## 5. 数据流示例

### 5.1 周报生成

```
POST /api/v1/work/weekly-report
    ↓
Work API → WorkService
    ↓
1. HybridRepository.hybrid_search()
   - Faiss 检索工作日志
   - Falkor 查询项目关系
    ↓
2. AnalyzeEngine.extract_insights()
   - 提取关键任务
   - 统计时间分配
    ↓
3. MimicEngine.generate_report()
   - 用户风格撰写
    ↓
返回周报
```

### 5.2 聊天陪伴（SSE）

```
POST /api/v1/mem/chat
    ↓
MEM API → StreamingResponse
    ↓
1. AnalyzeEngine.detect_emotion()
    ↓
2. HybridRepository.graph_search()
   - 查询相关记忆
    ↓
3. MimicEngine.generate_response_stream()
   - 流式生成回复
    ↓
SSE 输出：
  data: chunk1\n\n
  data: chunk2\n\n
  data: [DONE]\n\n
```

---

## 6. 错误处理

### 6.1 异常分类

```python
class ConfigurationError(APIException):
    """配置错误（API Key 未配置）"""

class StorageError(APIException):
    """存储错误"""

class LLMError(APIException):
    """LLM 调用错误"""
```

### 6.2 错误响应

```json
{
  "success": false,
  "error": "Configuration error",
  "detail": "API Key not configured",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 6.3 HTTP 状态码

```
400 - 参数错误
404 - 资源未找到
500 - 服务器内部错误
503 - 服务不可用（API 未配置）
```

---

## 7. 中间件

### 7.1 错误处理中间件

```python
class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except ValueError:
            return JSONResponse(status_code=400, ...)
        except Exception as e:
            logger.critical(f"Error: {e}")
            return JSONResponse(status_code=500, ...)
```

### 7.2 日志中间件

```python
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"→ {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"← {response.status_code}")
        return response
```

---

## 8. 配置管理

```python
class Settings(BaseSettings):
    # LLM
    OPENAI_API_KEY: Optional[str]
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 存储
    DATA_DIR: Path = Path("./data")
    
    # RAG
    RAG_CHUNK_SIZE: int = 500
    RAG_TOP_K: int = 5
    
    # MEM
    MEM_TOP_K: int = 10
```

---

## 9. 测试策略

### 9.1 单元测试

```python
@pytest.mark.asyncio
async def test_generate_weekly_report():
    service = WorkService()
    result = await service.generate_weekly_report(...)
    assert result["success"] is True
```

### 9.2 集成测试

```python
async def test_work_api(client):
    response = await client.post("/api/v1/work/weekly-report", ...)
    assert response.status_code == 200
```

---

## 10. 部署

### 10.1 Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### 10.2 Docker Compose

```yaml
services:
  backend:
    build: ../backend
    ports: ["8000:8000"]
    volumes: ["../data:/app/data"]
```

