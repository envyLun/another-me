# Another Me - 双存储架构设计 (Faiss + Falkor)

**版本**: 2.1.0  
**日期**: 2025-11-07  
**核心**: 短期记忆(Faiss) + 长期知识图谱(Falkor)

---

## 🎯 设计理念

### 为什么选择双存储？

**Faiss 向量数据库** - 快速响应层
- ✅ 毫秒级语义检索
- ✅ 近期内容理解（7-30天）
- ✅ 风格模仿上下文
- 🎯 场景："刚才我们聊了什么？" "最近我在关注什么？"

**Falkor 图谱数据库** - 深度分析层
- ✅ 实体关系建模
- ✅ 时间序列演化分析
- ✅ 多跳知识推理
- 🎯 场景："我和张三的关系变化？" "我的技术栈演进路径？"

**协同工作**:
```
查询 → Faiss快速召回(Top20近期相关) 
     ↓ 
     + Falkor图谱推理(关系链路/历史背景)
     ↓
     融合结果(相似度 + 关联性) → 生成答案
```

---

## 📊 架构设计

### 三层存储策略

```
热数据(0-7天)   → Faiss + Falkor  [实时检索]
温数据(7-30天)  → Faiss + Falkor  [补充上下文]
冷数据(30天+)   → 仅 Falkor       [深度分析]
```

### 数据模型

```python
class Document(BaseModel):
    id: str
    content: str
    doc_type: DocumentType
    timestamp: datetime
    
    # Faiss 字段
    faiss_id: Optional[int] = None
    embedding: Optional[List[float]] = None
    layer: str = "hot"  # hot/warm/cold
    
    # Falkor 字段
    graph_node_id: Optional[str] = None
    entities: List[str] = []      # 提取的实体
    relations: List[Dict] = []    # 关系三元组
    
    stored_in_faiss: bool = False
    stored_in_graph: bool = False
```

---

## 🔄 核心流程

### 1. 数据写入（双路并行）

```python
async def create_document_dual_storage(content: str) -> Document:
    doc = Document(id=uuid4(), content=content, timestamp=now())
    
    # 并行写入
    await asyncio.gather(
        write_to_faiss(doc),    # 生成向量、添加索引
        write_to_falkor(doc)    # 提取实体、构建图谱
    )
    
    await metadata_db.insert(doc)
    return doc

async def write_to_faiss(doc):
    embedding = await openai.get_embedding(doc.content)
    faiss_id = faiss_index.add(embedding)
    doc.faiss_id = faiss_id
    doc.stored_in_faiss = True

async def write_to_falkor(doc):
    entities = await ner_extract(doc.content)
    node_id = await falkor.create_node("Document", doc.dict())
    
    for entity in entities:
        entity_id = await falkor.get_or_create_entity(entity)
        await falkor.create_relation(node_id, entity_id, "MENTIONS")
    
    doc.graph_node_id = node_id
    doc.entities = entities
    doc.stored_in_graph = True
```

### 2. 混合检索

```python
async def hybrid_search(query: str, top_k: int = 10):
    # 并行检索
    faiss_task = faiss_search(query, top_k * 2)
    graph_task = graph_search(query, top_k)
    
    faiss_results, graph_results = await asyncio.gather(faiss_task, graph_task)
    
    # 融合排序
    all_results = merge_and_rerank(faiss_results, graph_results)
    return all_results[:top_k]

async def faiss_search(query, k):
    """向量检索"""
    embedding = await openai.get_embedding(query)
    indices, distances = faiss_index.search(embedding, k)
    return [{"doc_id": id_map[i], "score": 1/(1+d)} for i, d in zip(indices, distances)]

async def graph_search(query, k):
    """图谱检索"""
    entities = await ner_extract(query)
    
    cypher = """
    MATCH (d:Document)-[:MENTIONS]->(e:Entity)
    WHERE e.name IN $entities
    RETURN d.doc_id, COUNT(e) as relevance
    ORDER BY relevance DESC, d.timestamp DESC
    LIMIT $k
    """
    
    results = await falkor.query(cypher, entities=entities, k=k)
    return [{"doc_id": r["doc_id"], "score": r["relevance"]/len(entities), "source": "graph"} for r in results]
```

### 3. 数据生命周期

```python
async def lifecycle_management():
    """定时任务：热→温→冷"""
    now = datetime.now()
    
    # 7天前：热→温/冷
    hot_docs = await metadata_db.list(layer="hot", before=now - timedelta(days=7))
    for doc in hot_docs:
        if doc.importance > 0.7:
            doc.layer = "warm"  # 降级
        else:
            faiss_index.remove(doc.faiss_id)  # 删除向量
            doc.layer = "cold"
            doc.stored_in_faiss = False
        await metadata_db.update(doc)
    
    # 30天前：温→冷
    warm_docs = await metadata_db.list(layer="warm", before=now - timedelta(days=30))
    for doc in warm_docs:
        faiss_index.remove(doc.faiss_id)
        doc.layer = "cold"
        doc.stored_in_faiss = False
        await metadata_db.update(doc)
```

---

## 🛠️ 技术实现

### Faiss 集成

```python
import faiss
import numpy as np

class FaissVectorStore:
    def __init__(self, dimension=1536):
        # IVF索引：速度和精度平衡
        quantizer = faiss.IndexFlatL2(dimension)
        self.index = faiss.IndexIVFFlat(quantizer, dimension, 100)
        self.id_map = {}  # faiss_id -> doc_id
    
    async def add(self, embedding: List[float], doc_id: str) -> int:
        vector = np.array([embedding], dtype=np.float32)
        faiss_id = self.index.ntotal
        self.index.add(vector)
        self.id_map[faiss_id] = doc_id
        return faiss_id
    
    async def search(self, query_embedding, top_k=10):
        query = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query, top_k)
        return [(int(idx), float(dist)) for idx, dist in zip(indices[0], distances[0]) if idx != -1]
```

### Falkor 集成

```python
class FalkorGraphStore:
    def __init__(self, connection_string):
        self.client = FalkorClient(connection_string)
    
    async def create_node(self, node_type: str, properties: Dict) -> str:
        cypher = f"CREATE (n:{node_type} $props) RETURN n.id"
        result = await self.client.execute(cypher, props=properties)
        return result[0]["n.id"]
    
    async def create_relation(self, source, target, rel_type, props=None):
        cypher = f"""
        MATCH (s {{id: $source}}), (t {{id: $target}})
        CREATE (s)-[r:{rel_type} $props]->(t)
        """
        await self.client.execute(cypher, source=source, target=target, props=props or {})
    
    async def find_related_docs(self, entity_name: str, max_hops=2):
        cypher = f"""
        MATCH path = (d:Document)-[*1..{max_hops}]-(e:Entity {{name: $entity}})
        RETURN DISTINCT d.doc_id, length(path) as distance
        ORDER BY distance
        LIMIT 20
        """
        return await self.client.execute(cypher, entity=entity_name)
```

### 混合 Repository

```python
class HybridRepository:
    def __init__(self, faiss, falkor, metadata_db):
        self.faiss = faiss
        self.graph = falkor
        self.metadata = metadata_db
    
    async def create(self, doc: Document) -> Document:
        # 双写
        if doc.embedding:
            doc.faiss_id = await self.faiss.add(doc.embedding, doc.id)
            doc.stored_in_faiss = True
        
        node_id = await self.graph.create_node("Document", {
            "doc_id": doc.id,
            "content": doc.content,
            "timestamp": doc.timestamp.isoformat()
        })
        doc.graph_node_id = node_id
        doc.stored_in_graph = True
        
        # 创建实体关系
        for entity in doc.entities:
            entity_id = await self._get_or_create_entity(entity)
            await self.graph.create_relation(node_id, entity_id, "MENTIONS")
        
        self.metadata.insert(doc.dict())
        return doc
    
    async def hybrid_search(self, query, query_emb, top_k=10):
        # 并行检索
        faiss_results = await self.faiss.search(query_emb, top_k * 2)
        
        entities = await extract_entities(query)
        graph_doc_ids = []
        if entities:
            graph_doc_ids = await self.graph.find_related_docs(entities[0])
        
        # 融合
        results = []
        for fid, score in faiss_results:
            doc_id = self.faiss.id_map[fid]
            results.append({"doc_id": doc_id, "score": 1/(1+score), "source": "faiss"})
        
        for gid in graph_doc_ids:
            results.append({"doc_id": gid["doc_id"], "score": 0.8, "source": "graph"})
        
        # 去重排序
        seen = set()
        unique = []
        for r in results:
            if r["doc_id"] not in seen:
                seen.add(r["doc_id"])
                unique.append(r)
        
        unique.sort(key=lambda x: x["score"], reverse=True)
        return unique[:top_k]
```

---

## 🎬 使用场景

### 场景1: 近期对话回忆
```
用户: "昨天我们聊了什么？"
系统: Faiss检索(时间过滤) → 返回昨天的对话
```

### 场景2: 关系演化分析
```
用户: "我和张三的关系变化？"
系统: Falkor图谱查询(时间序列) → 返回互动时间线
```

### 场景3: 综合查询
```
用户: "Python 相关的学习记录"
系统: Faiss相似度检索 + Falkor主题关联 → 融合结果
```

---

## 📈 性能优化

1. **Faiss索引选择**
   - 小规模(<10万): IndexFlatL2
   - 中规模(10万-100万): IndexIVFFlat
   - 大规模(>100万): IndexHNSWFlat

2. **批量操作**
   ```python
   # 批量添加向量
   vectors = np.array(embeddings, dtype=np.float32)
   faiss_index.add(vectors)
   ```

3. **缓存策略**
   ```python
   @lru_cache(maxsize=1000)
   async def get_doc_cached(doc_id): ...
   ```

---

## 📁 目录结构

```
backend/app/
├── storage/              # 新增：存储层
│   ├── faiss_store.py    # Faiss 封装
│   ├── falkor_store.py   # Falkor 封装
│   └── __init__.py
├── repositories/
│   ├── hybrid_repository.py  # 混合仓库
│   └── ...
├── services/
│   └── ...
```

---

## 🚀 实施计划

**Phase 1**: Faiss集成（1周）
- 安装faiss-cpu: `pip install faiss-cpu`
- 实现FaissVectorStore
- 修改RAGRepository支持Faiss

**Phase 2**: Falkor集成（1周）
- 安装Falkor客户端
- 实现FalkorGraphStore
- 实体抽取（spaCy/BERT NER）

**Phase 3**: 混合检索（1周）
- 实现HybridRepository
- 融合算法
- 性能测试

**Phase 4**: 生命周期管理（3天）
- 定时任务
- 数据降温策略

---

## 📝 配置示例

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # Faiss配置
    FAISS_INDEX_PATH: Path = Path("./data/faiss.index")
    FAISS_DIMENSION: int = 1536
    
    # Falkor配置
    FALKOR_CONNECTION: str = "bolt://localhost:7687"
    FALKOR_USER: str = "neo4j"
    FALKOR_PASSWORD: str = "password"
    
    # 生命周期配置
    HOT_DATA_DAYS: int = 7
    WARM_DATA_DAYS: int = 30
    IMPORTANCE_THRESHOLD: float = 0.7
```

---

**核心价值**: 短期快速 + 长期深度，兼顾响应速度和分析能力！
