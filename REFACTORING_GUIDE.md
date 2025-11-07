# Another Me - 重构实施指南

本文档提供重构的具体实施步骤和代码示例。

---

## 📋 Phase 1: 基础架构重构

### Step 1.1: 创建统一数据模型

**文件**: `backend/app/models/domain.py`

```python
"""
领域模型 - 统一的数据结构定义
"""
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid


class DocumentType(str, Enum):
    """文档类型枚举"""
    RAG_KNOWLEDGE = "rag_knowledge"
    MEM_CONVERSATION = "mem_conversation"
    MEM_DIARY = "mem_diary"
    MEM_SOCIAL = "mem_social"


class DocumentStatus(str, Enum):
    """文档状态"""
    PROCESSING = "processing"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Document(BaseModel):
    """基础文档模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    doc_type: DocumentType
    source: str
    status: DocumentStatus = DocumentStatus.PROCESSING
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Knowledge(Document):
    """知识文档（RAG 专用）"""
    doc_type: DocumentType = DocumentType.RAG_KNOWLEDGE
    tags: List[str] = Field(default_factory=list)
    file_path: Optional[str] = None
    chunk_index: int = 0
    total_chunks: int = 1


class Memory(Document):
    """记忆文档（MEM 专用）"""
    doc_type: DocumentType = DocumentType.MEM_CONVERSATION
    emotion: Optional[str] = None
    importance: float = 0.5
```

### Step 1.2: 创建元数据数据库

**文件**: `backend/app/core/database.py`

```python
"""
元数据数据库管理（SQLite）
"""
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from app.core.logger import get_logger

logger = get_logger(__name__)


class MetadataDB:
    """元数据数据库"""
    
    def __init__(self, db_path: str = "./data/metadata.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    doc_type TEXT NOT NULL,
                    source TEXT,
                    status TEXT,
                    timestamp DATETIME,
                    created_at DATETIME,
                    updated_at DATETIME,
                    metadata TEXT
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_type ON documents(doc_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON documents(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON documents(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON documents(timestamp)")
            
            conn.commit()
            logger.info("Metadata database initialized")
    
    def insert(self, doc: Dict[str, Any]) -> bool:
        """插入文档元数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO documents 
                (id, doc_type, source, status, timestamp, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc["id"],
                doc["doc_type"],
                doc["source"],
                doc.get("status", "processing"),
                doc.get("timestamp"),
                doc.get("created_at"),
                doc.get("updated_at"),
                json.dumps(doc.get("metadata", {}))
            ))
            conn.commit()
        return True
    
    def get(self, doc_id: str) -> Optional[Dict]:
        """获取文档元数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def list(
        self, 
        doc_type: Optional[str] = None,
        source: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """列表查询"""
        query = "SELECT * FROM documents WHERE 1=1"
        params = []
        
        if doc_type:
            query += " AND doc_type = ?"
            params.append(doc_type)
        if source:
            query += " AND source LIKE ?"
            params.append(f"%{source}%")
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update(self, doc_id: str, updates: Dict) -> bool:
        """更新文档元数据"""
        updates["updated_at"] = datetime.now().isoformat()
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE documents SET {set_clause} WHERE id = ?"
        params = list(updates.values()) + [doc_id]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
            conn.commit()
        return True
    
    def delete(self, doc_id: str) -> bool:
        """删除文档元数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
        return True
    
    def count(self, doc_type: Optional[str] = None) -> int:
        """统计文档数量"""
        query = "SELECT COUNT(*) FROM documents"
        params = []
        
        if doc_type:
            query += " WHERE doc_type = ?"
            params.append(doc_type)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]
```

### Step 1.3: 实现 Repository 层

**文件**: `backend/app/repositories/base.py`

```python
"""
Repository 基类 - 数据访问层抽象
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.domain import Document
from app.models.responses import PaginatedResponse


class BaseRepository(ABC):
    """仓库基类"""
    
    @abstractmethod
    async def create(self, doc: Document) -> Document:
        """创建文档"""
        pass
    
    @abstractmethod
    async def get(self, doc_id: str) -> Optional[Document]:
        """获取单个文档"""
        pass
    
    @abstractmethod
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResponse[Document]:
        """分页列表"""
        pass
    
    @abstractmethod
    async def update(self, doc_id: str, updates: Dict[str, Any]) -> Document:
        """更新文档"""
        pass
    
    @abstractmethod
    async def delete(self, doc_id: str) -> bool:
        """删除文档"""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """向量检索"""
        pass
```

**文件**: `backend/app/repositories/rag_repository.py`

```python
"""
RAG Repository - 知识库数据访问
"""
from typing import List, Optional, Dict, Any
from app.repositories.base import BaseRepository
from app.models.domain import Knowledge, DocumentType, DocumentStatus
from app.models.responses import PaginatedResponse
from app.core.database import MetadataDB
from ame.vector_store.base import VectorStoreBase
from app.core.logger import get_logger

logger = get_logger(__name__)


class RAGRepository(BaseRepository):
    """RAG 数据仓库"""
    
    def __init__(self, vector_store: VectorStoreBase, metadata_db: MetadataDB):
        self.vector_store = vector_store
        self.metadata_db = metadata_db
    
    async def create(self, doc: Knowledge) -> Knowledge:
        """创建知识文档"""
        # 1. 保存到向量库（自动生成 embedding）
        await self.vector_store.add_documents([{
            "id": doc.id,
            "content": doc.content,
            "metadata": {
                "doc_type": doc.doc_type,
                "source": doc.source,
                "timestamp": doc.timestamp.isoformat(),
                "tags": doc.tags,
                **doc.metadata
            }
        }])
        
        # 2. 保存元数据到数据库
        self.metadata_db.insert({
            "id": doc.id,
            "doc_type": doc.doc_type,
            "source": doc.source,
            "status": doc.status,
            "timestamp": doc.timestamp.isoformat(),
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat(),
            "metadata": {
                "tags": doc.tags,
                "file_path": doc.file_path,
                "chunk_index": doc.chunk_index,
                "total_chunks": doc.total_chunks,
                **doc.metadata
            }
        })
        
        logger.info(f"Created knowledge document: {doc.id}")
        return doc
    
    async def get(self, doc_id: str) -> Optional[Knowledge]:
        """获取知识文档"""
        # 从元数据库获取
        metadata = self.metadata_db.get(doc_id)
        if not metadata:
            return None
        
        # 从向量库获取内容
        vector_result = await self.vector_store.get_by_id(doc_id)
        
        # 组合返回
        return Knowledge(
            id=metadata["id"],
            content=vector_result.get("content", ""),
            source=metadata["source"],
            status=metadata["status"],
            timestamp=metadata["timestamp"],
            tags=metadata.get("metadata", {}).get("tags", []),
            file_path=metadata.get("metadata", {}).get("file_path"),
            chunk_index=metadata.get("metadata", {}).get("chunk_index", 0),
            total_chunks=metadata.get("metadata", {}).get("total_chunks", 1),
            created_at=metadata["created_at"],
            updated_at=metadata["updated_at"]
        )
    
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResponse[Knowledge]:
        """分页列表"""
        filters = filters or {}
        offset = (page - 1) * page_size
        
        # 从元数据库查询
        results = self.metadata_db.list(
            doc_type=DocumentType.RAG_KNOWLEDGE,
            source=filters.get("source"),
            status=filters.get("status"),
            limit=page_size,
            offset=offset
        )
        
        # 转换为 Knowledge 对象
        knowledge_list = []
        for metadata in results:
            knowledge = await self.get(metadata["id"])
            if knowledge:
                knowledge_list.append(knowledge)
        
        # 计算总数
        total = self.metadata_db.count(doc_type=DocumentType.RAG_KNOWLEDGE)
        
        return PaginatedResponse(
            data=knowledge_list,
            pagination={
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    
    async def update(self, doc_id: str, updates: Dict[str, Any]) -> Knowledge:
        """更新知识文档"""
        # 更新元数据
        self.metadata_db.update(doc_id, updates)
        
        # 如果更新了内容，更新向量库
        if "content" in updates:
            await self.vector_store.update_document(doc_id, updates["content"])
        
        # 返回更新后的文档
        return await self.get(doc_id)
    
    async def delete(self, doc_id: str) -> bool:
        """删除知识文档"""
        # 从向量库删除
        await self.vector_store.delete_documents([doc_id])
        
        # 从元数据库删除
        self.metadata_db.delete(doc_id)
        
        logger.info(f"Deleted knowledge document: {doc_id}")
        return True
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """向量检索"""
        results = await self.vector_store.search(
            query=query,
            top_k=top_k,
            filters=filters
        )
        return results
```

---

## 📋 Phase 2: Service 层重构

### Step 2.1: 重写 RAGService

**文件**: `backend/app/services/rag_service.py`

```python
"""
RAG Service - 知识库业务逻辑
"""
from typing import List, Optional, Dict, Any
from fastapi import UploadFile
from pathlib import Path
import shutil
from datetime import datetime

from app.models.domain import Knowledge, DocumentStatus
from app.models.responses import PaginatedResponse, SearchResult, QAResponse
from app.repositories.rag_repository import RAGRepository
from ame.data_processor.processor import DataProcessor
from ame.rag.qa_generator import QAGenerator  # 需要新建
from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.exceptions import DocumentNotFoundError, ValidationError

logger = get_logger(__name__)


class RAGService:
    """RAG 业务服务"""
    
    def __init__(
        self,
        repository: RAGRepository,
        data_processor: DataProcessor,
        qa_generator: QAGenerator
    ):
        self.repo = repository
        self.processor = data_processor
        self.qa = qa_generator
        self.settings = get_settings()
    
    async def create_knowledge(
        self,
        file: UploadFile,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Knowledge:
        """
        创建知识文档（从文件上传）
        
        业务流程:
        1. 验证文件格式和大小
        2. 保存文件到本地
        3. 解析文件内容
        4. 分块处理
        5. 保存到数据库（向量化）
        """
        logger.info(f"Creating knowledge from file: {file.filename}")
        
        # 1. 验证
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.settings.ALLOWED_EXTENSIONS:
            raise ValidationError(f"File type {file_ext} not allowed")
        
        # 2. 保存文件
        file_path = await self._save_upload_file(file)
        
        try:
            # 3. 解析文件
            documents = await self.processor.process_file(str(file_path))
            
            if not documents:
                raise ValidationError("No content extracted from file")
            
            # 4. 创建知识文档（分块）
            knowledge_list = []
            total_chunks = len(documents)
            
            for idx, doc_data in enumerate(documents):
                knowledge = Knowledge(
                    content=doc_data["content"],
                    source=file.filename,
                    timestamp=doc_data.get("timestamp", datetime.now()),
                    tags=tags or [],
                    file_path=str(file_path),
                    chunk_index=idx,
                    total_chunks=total_chunks,
                    metadata=metadata or {},
                    status=DocumentStatus.PROCESSING
                )
                
                # 5. 保存到仓库
                saved = await self.repo.create(knowledge)
                knowledge_list.append(saved)
            
            # 6. 更新状态为 ACTIVE
            for k in knowledge_list:
                await self.repo.update(k.id, {"status": DocumentStatus.ACTIVE})
            
            logger.info(f"Created {len(knowledge_list)} knowledge chunks")
            
            # 返回第一个分块
            return knowledge_list[0]
            
        except Exception as e:
            # 清理文件
            if file_path.exists():
                file_path.unlink()
            raise
    
    async def get_knowledge(self, knowledge_id: str) -> Knowledge:
        """获取知识文档"""
        knowledge = await self.repo.get(knowledge_id)
        if not knowledge:
            raise DocumentNotFoundError(knowledge_id)
        return knowledge
    
    async def list_knowledge(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResponse[Knowledge]:
        """列表查询（分页）"""
        return await self.repo.list(filters, page, page_size)
    
    async def update_knowledge(
        self,
        knowledge_id: str,
        updates: Dict[str, Any]
    ) -> Knowledge:
        """更新知识文档"""
        # 验证文档存在
        await self.get_knowledge(knowledge_id)
        
        # 更新
        return await self.repo.update(knowledge_id, updates)
    
    async def delete_knowledge(self, knowledge_id: str) -> bool:
        """删除知识文档"""
        await self.get_knowledge(knowledge_id)
        return await self.repo.delete(knowledge_id)
    
    async def search_knowledge(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[SearchResult]:
        """检索知识"""
        results = await self.repo.search(query, filters, top_k)
        
        return [
            SearchResult(
                content=r.get("content"),
                score=r.get("score", 0.0),
                metadata=r.get("metadata", {})
            )
            for r in results
        ]
    
    async def ask_question(
        self,
        question: str,
        context: Optional[str] = None
    ) -> QAResponse:
        """智能问答（非流式）"""
        # 1. 检索相关知识
        knowledge = await self.search_knowledge(question, top_k=5)
        
        # 2. 生成答案
        answer = await self.qa.generate_answer(
            question=question,
            context=context,
            knowledge=knowledge
        )
        
        return QAResponse(
            question=question,
            answer=answer,
            sources=[k.metadata for k in knowledge]
        )
    
    async def ask_question_stream(
        self,
        question: str,
        context: Optional[str] = None
    ):
        """智能问答（流式）"""
        # 1. 检索
        knowledge = await self.search_knowledge(question, top_k=5)
        
        # 2. 流式生成
        async for chunk in self.qa.generate_answer_stream(
            question=question,
            context=context,
            knowledge=knowledge
        ):
            yield chunk
    
    async def _save_upload_file(self, file: UploadFile) -> Path:
        """保存上传的文件"""
        upload_dir = self.settings.UPLOADS_DIR / "rag"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return file_path


# 依赖注入
_rag_service: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        from app.repositories.rag_repository import RAGRepository
        from app.core.database import MetadataDB
        from ame.vector_store.factory import VectorStoreFactory
        from ame.data_processor.processor import DataProcessor
        from ame.rag.qa_generator import QAGenerator
        
        settings = get_settings()
        
        # 创建依赖
        vector_store = VectorStoreFactory.create(
            store_type=settings.VECTOR_STORE_TYPE,
            db_path=str(settings.RAG_VECTOR_STORE_PATH)
        )
        metadata_db = MetadataDB()
        repository = RAGRepository(vector_store, metadata_db)
        data_processor = DataProcessor()
        qa_generator = QAGenerator()  # 需要实现
        
        _rag_service = RAGService(repository, data_processor, qa_generator)
    
    return _rag_service
```

---

## 📋 Phase 3: API 层更新

### Step 3.1: 更新 RAG API

**文件**: `backend/app/api/v1/rag.py`

```python
"""
RAG API 端点
"""
from fastapi import APIRouter, UploadFile, File, Depends, Query
from typing import List, Optional

from app.services.rag_service import RAGService, get_rag_service
from app.models.requests import SearchRequest, QARequest
from app.models.responses import (
    KnowledgeResponse,
    PaginatedResponse,
    SearchResponse,
    QAResponse
)

router = APIRouter()


@router.post("/knowledge", response_model=KnowledgeResponse)
async def create_knowledge(
    file: UploadFile = File(...),
    tags: Optional[str] = Query(None),  # 逗号分隔
    service: RAGService = Depends(get_rag_service)
):
    """上传知识文档"""
    tag_list = tags.split(",") if tags else []
    knowledge = await service.create_knowledge(file, tags=tag_list)
    return KnowledgeResponse(success=True, data=knowledge)


@router.get("/knowledge", response_model=PaginatedResponse)
async def list_knowledge(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    service: RAGService = Depends(get_rag_service)
):
    """知识列表（分页）"""
    filters = {}
    if source:
        filters["source"] = source
    if status:
        filters["status"] = status
    
    result = await service.list_knowledge(filters, page, page_size)
    return result


@router.get("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge(
    knowledge_id: str,
    service: RAGService = Depends(get_rag_service)
):
    """获取知识详情"""
    knowledge = await service.get_knowledge(knowledge_id)
    return KnowledgeResponse(success=True, data=knowledge)


@router.delete("/knowledge/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: str,
    service: RAGService = Depends(get_rag_service)
):
    """删除知识"""
    success = await service.delete_knowledge(knowledge_id)
    return {"success": success}


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    request: SearchRequest,
    service: RAGService = Depends(get_rag_service)
):
    """检索知识"""
    results = await service.search_knowledge(
        query=request.query,
        top_k=request.top_k
    )
    return SearchResponse(success=True, data=results)


@router.post("/ask", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    service: RAGService = Depends(get_rag_service)
):
    """智能问答"""
    response = await service.ask_question(
        question=request.question,
        context=request.context
    )
    return response
```

---

## 📋 检查清单

### Phase 1 完成标准

- [ ] `domain.py` 创建完成
- [ ] `database.py` 实现并测试
- [ ] `BaseRepository` 定义完成
- [ ] `RAGRepository` 和 `MEMRepository` 实现
- [ ] 数据库迁移脚本编写
- [ ] 单元测试编写

### Phase 2 完成标准

- [ ] `RAGService` 重构完成
- [ ] `MEMService` 重构完成
- [ ] 所有 CRUD 功能实现
- [ ] 错误处理完善
- [ ] 业务逻辑测试通过

### Phase 3 完成标准

- [ ] 所有 API 端点更新
- [ ] API 文档更新
- [ ] 前端 API 客户端更新
- [ ] 集成测试通过

---

## 📝 注意事项

1. **数据备份**: 重构前备份现有向量数据
2. **向后兼容**: 保留旧 API 一段时间
3. **渐进式迁移**: 先完成 RAG，再做 MEM
4. **测试驱动**: 每个模块先写测试
5. **文档同步**: 代码和文档同步更新
