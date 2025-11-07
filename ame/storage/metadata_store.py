"""
元数据数据库管理（SQLite）
职责：存储文档元数据、索引信息、状态管理
"""
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from ame.models.domain import Document, DocumentType, DataLayer


class MetadataStore:
    """元数据数据库（SQLite）"""
    
    def __init__(self, db_path: str = "./data/metadata.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            # 文档主表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    doc_type TEXT NOT NULL,
                    source TEXT,
                    timestamp DATETIME,
                    
                    -- Faiss 字段
                    faiss_index INTEGER,
                    layer TEXT DEFAULT 'hot',
                    stored_in_faiss BOOLEAN DEFAULT 0,
                    
                    -- Falkor 字段
                    graph_node_id TEXT,
                    entities TEXT,
                    stored_in_graph BOOLEAN DEFAULT 0,
                    
                    -- 状态字段
                    status TEXT DEFAULT 'processing',
                    importance REAL DEFAULT 0.5,
                    retention_type TEXT DEFAULT 'permanent',
                    
                    -- 元数据
                    metadata TEXT,
                    
                    -- 时间戳
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_type ON documents(doc_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON documents(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON documents(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON documents(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_layer ON documents(layer)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_retention_type ON documents(retention_type)")
            
            conn.commit()
    
    def insert(self, doc: Document) -> bool:
        """插入文档元数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO documents 
                (id, content, doc_type, source, timestamp, 
                 faiss_index, layer, stored_in_faiss,
                 graph_node_id, entities, stored_in_graph,
                 status, importance, retention_type, metadata,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.id,
                doc.content,
                doc.doc_type,
                doc.source,
                doc.timestamp.isoformat() if doc.timestamp else None,
                doc.faiss_index,
                doc.layer,
                doc.stored_in_faiss,
                doc.graph_node_id,
                json.dumps(doc.entities),
                doc.stored_in_graph,
                doc.status,
                doc.importance,
                doc.retention_type,
                json.dumps(doc.metadata),
                doc.created_at.isoformat() if doc.created_at else None,
                doc.updated_at.isoformat() if doc.updated_at else None,
            ))
            conn.commit()
        return True
    
    def get(self, doc_id: str) -> Optional[Document]:
        """获取文档元数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_document(row)
    
    def list(
        self, 
        doc_type: Optional[str] = None,
        source: Optional[str] = None,
        status: Optional[str] = None,
        layer: Optional[str] = None,
        retention_type: Optional[str] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Document]:
        """列表查询（支持多种过滤条件）"""
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
        if layer:
            query += " AND layer = ?"
            params.append(layer)
        if retention_type:
            query += " AND retention_type = ?"
            params.append(retention_type)
        if before:
            query += " AND timestamp < ?"
            params.append(before.isoformat())
        if after:
            query += " AND timestamp > ?"
            params.append(after.isoformat())
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [self._row_to_document(row) for row in cursor.fetchall()]
    
    def update(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """更新文档元数据"""
        updates["updated_at"] = datetime.now().isoformat()
        
        # 处理特殊字段（JSON序列化）
        if "entities" in updates:
            updates["entities"] = json.dumps(updates["entities"])
        if "metadata" in updates:
            updates["metadata"] = json.dumps(updates["metadata"])
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE documents SET {set_clause} WHERE id = ?"
        params = list(updates.values()) + [doc_id]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
            conn.commit()
        return True
    
    def delete(self, doc_id: str) -> bool:
        """删除文档元数据（物理删除）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
        return True
    
    def soft_delete(self, doc_id: str) -> bool:
        """软删除（标记为已删除）"""
        return self.update(doc_id, {"status": "deleted"})
    
    def count(
        self,
        doc_type: Optional[str] = None,
        status: Optional[str] = None,
        layer: Optional[str] = None
    ) -> int:
        """统计文档数量"""
        query = "SELECT COUNT(*) FROM documents WHERE 1=1"
        params = []
        
        if doc_type:
            query += " AND doc_type = ?"
            params.append(doc_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        if layer:
            query += " AND layer = ?"
            params.append(layer)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]
    
    def get_by_ids(self, doc_ids: List[str]) -> List[Document]:
        """批量获取文档"""
        if not doc_ids:
            return []
        
        placeholders = ",".join(["?" for _ in doc_ids])
        query = f"SELECT * FROM documents WHERE id IN ({placeholders})"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, doc_ids)
            return [self._row_to_document(row) for row in cursor.fetchall()]
    
    def _row_to_document(self, row: sqlite3.Row) -> Document:
        """转换数据库行为 Document 对象"""
        data = dict(row)
        
        # 解析 JSON 字段
        if data.get("entities"):
            data["entities"] = json.loads(data["entities"])
        if data.get("metadata"):
            data["metadata"] = json.loads(data["metadata"])
        
        # 转换时间字段
        if data.get("timestamp"):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        # 设置默认值
        data.setdefault("relations", [])
        data.setdefault("embedding", None)
        
        return Document(**data)
