# AME 核心算法增强设计

## 1. 概述

### 1.1 项目背景

Another Me 是一个 AI 数字分身系统，前端已完成独立部署（React + TypeScript + Vite），提供完整的用户交互界面。当前需要完善 AME（Another Me Engine）核心算法模块，为后端提供完整的算法能力支持。

### 1.2 设计目标

- **完善算法层**：增强 AME 核心算法模块的能力，覆盖前端所需的全部功能
- **清晰的职责边界**：AME 专注算法逻辑，后端负责数据库配置和 API 暴露
- **模块化设计**：AME 作为独立 Python 包，通过明确接口与后端集成
- **支持前端功能**：覆盖前端 README 中提到的 27 个 API 接口功能需求

### 1.3 架构分层

```
┌─────────────────────────────────────────────────────┐
│         Frontend (React + TypeScript)                │
│  27 API Calls: RAG, MEM, Work, Life, Graph          │
└─────────────────────────────────────────────────────┘
                      ↓ HTTP API
┌─────────────────────────────────────────────────────┐
│         Backend (FastAPI)                            │
│  - API 路由层 (app/api/v1/)                          │
│  - Service 编排层 (app/services/)                   │
│  - 数据库配置（提供连接参数给 AME）                    │
└─────────────────────────────────────────────────────┘
                      ↓ Function Call
┌─────────────────────────────────────────────────────┐
│         AME Engine (Python Package)                  │
│  核心算法能力（独立模块）                              │
│  - engines/      场景引擎层                          │
│  - mem/          记忆与分析核心                       │
│  - rag/          知识库核心                          │
│  - repository/   数据访问层                          │
│  - storage/      存储抽象层                          │
│  - retrieval/    检索算法层                          │
│  - ner/          实体识别层                          │
│  - llm_caller/   LLM 调用层                          │
└─────────────────────────────────────────────────────┘
                      ↓ Storage
┌─────────────────────────────────────────────────────┐
│     Storage Layer (后端配置并提供连接参数)             │
│  - Faiss Vector Store                               │
│  - FalkorDB Graph Database                          │
│  - SQLite Metadata Store                            │
└─────────────────────────────────────────────────────┘
```

---

## 2. 核心功能架构

### 2.1 双引擎架构设计

AME 采用场景引擎层 + 核心引擎层的双层架构：

```
场景引擎层 (engines/)
├── WorkEngine          工作场景
│   ├── 周报生成
│   ├── 日报生成
│   ├── 待办整理
│   ├── 会议总结
│   └── 项目追踪
└── LifeEngine          生活场景
    ├── 心情分析
    ├── 兴趣追踪
    ├── 生活建议
    └── 记忆回顾

核心引擎层 (mem/)
├── MimicEngine         风格模仿
│   ├── 学习用户表达
│   ├── 生成用户风格文本
│   └── 流式对话生成
└── AnalyzeEngine       数据分析
    ├── 行为模式识别
    ├── 趋势分析
    └── 洞察提取
```

### 2.2 存储架构设计

**双存储策略**（Faiss + FalkorDB）：

| 存储层 | 职责 | 数据范围 | 算法特点 |
|--------|------|----------|----------|
| **Faiss Vector** | 语义相似度检索 | 0-30天热温数据 | 向量距离计算，毫秒级响应 |
| **FalkorDB Graph** | 实体关系推理 | 全生命周期数据 | 多跳图遍历，关系演化分析 |
| **SQLite Metadata** | 元数据管理 | 全生命周期数据 | 结构化查询，时间范围过滤 |

**混合检索算法**：
- Faiss 向量召回（基于语义相似度）
- FalkorDB 图谱推理（基于实体关系）
- 融合排序（加权求和，默认 Faiss 0.6 + Graph 0.4）

---

## 3. 算法模块详细设计

### 3.1 场景引擎层 (engines/)

#### 3.1.1 WorkEngine 算法增强

**核心算法**：

```python
class WorkEngine:
    """工作场景引擎"""
    
    async def generate_weekly_report(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        style: str = "professional"
    ) -> WeeklyReport:
        """
        周报生成算法
        
        算法流程：
        1. 数据收集：从 Repository 检索工作记录
        2. 实体提取：使用 NER 提取关键任务实体
        3. 频率统计：Counter 统计实体出现频率
        4. 洞察生成：AnalyzeEngine 分析成就、挑战
        5. 风格化输出：MimicEngine 生成用户风格文本
        
        算法优化：
        - 时间加权：越近的记录权重越高
        - 重要性过滤：importance > 0.7 的优先展示
        - 去重合并：相似任务自动合并
        """
```

**新增算法**：
- `generate_daily_report()`: 日报生成（基于单日数据聚合）
- `organize_todos()`: 待办优先级算法（紧急度 + 重要性 + 依赖关系）
- `summarize_meeting()`: 会议要点提取（基于 LLM 结构化提取）
- `track_project_progress()`: 项目进度分析（基于图谱时间线查询）

**待办优先级算法**：

```python
async def prioritize_tasks(tasks: List[TaskInfo]) -> List[TaskInfo]:
    """
    优先级评分算法
    
    评分规则（总分 100）：
    1. 紧急度（0-40分）
       - "紧急"/"今天"/"ASAP": 40分
       - "明天": 30分
       - "本周": 25分
       - "近期": 15分
    
    2. 重要性（0-40分）
       - "重要"/"关键"/"核心": 30分
       - "优先"/"必须": 20分
    
    3. 依赖关系（±20分）
       - 阻塞其他任务: +20分
       - 依赖其他任务: -10分
    
    输出：按 priority_score 降序排序
    """
```

#### 3.1.2 LifeEngine 算法增强

**核心算法**：

```python
class LifeEngine:
    """生活场景引擎"""
    
    async def analyze_mood(
        self,
        mood_entry: str,
        user_id: str,
        entry_time: datetime
    ) -> MoodAnalysis:
        """
        心情分析算法
        
        算法流程：
        1. 情绪识别：LLM 分析情绪类型和强度（0-1）
        2. 触发因素提取：NER + LLM 识别情绪触发事件
        3. 趋势分析：对比最近 7 天情绪变化
        4. 建议生成：基于情绪状态生成个性化建议
        
        情绪趋势算法：
        - 计算近 7 天平均情绪强度
        - 当前强度 > 平均 + 0.2: improving
        - 当前强度 < 平均 - 0.2: declining
        - 其他: stable
        - 预警：declining && 强度 < 0.3
        """
```

**兴趣演化算法**：

```python
async def track_interests(
    self,
    user_id: str,
    period_days: int = 30
) -> InterestReport:
    """
    兴趣追踪算法
    
    算法流程：
    1. 数据收集：检索最近 N 天生活记录
    2. 实体提取：使用 HybridNER 提取主题实体
    3. 频率统计：Counter 统计实体出现频率
    4. 演化分析：对比不同时间窗口（当前期 vs 上一期）
       - 新兴趣 = 当前期实体 - 上一期实体
       - 衰减兴趣 = 上一期实体 - 当前期实体
    5. 趋势判断：基于时间序列分析
       - rising: 最近频率 > 早期频率
       - declining: 最近频率 < 早期频率
       - stable: 频率变化不大
    
    输出：Top 10 兴趣 + 新兴趣 + 衰减兴趣 + 推荐
    """
```

### 3.2 核心引擎层 (mem/)

#### 3.2.1 MimicEngine 算法增强

**核心算法**：

```python
class MimicEngine:
    """模仿引擎 - 学习和模仿用户说话风格"""
    
    async def generate_response_stream(
        self,
        prompt: str,
        temperature: float = 0.8,
        use_history: bool = True
    ) -> AsyncIterator[str]:
        """
        流式对话生成算法
        
        算法流程：
        1. 上下文检索：
           - 使用混合检索器（HybridRetriever）
           - 向量权重 0.4，关键词权重 0.4，时间权重 0.2
           - 检索 Top 5 相关历史对话
        
        2. Prompt 构建：
           - 系统提示词：定义 AI 角色和风格要求
           - 用户历史：注入相关历史对话作为风格参考
           - 用户问题：当前输入
        
        3. 流式生成：
           - 调用 LLMCaller.generate_stream()
           - 逐 token 返回，实时展示
        
        4. 风格保持：
           - Temperature 0.8 保持创造性
           - 第一人称"我"表达
           - 保留用户惯用词汇和句式
        """
```

**风格化文本生成算法**：

```python
async def generate_styled_text(
    self,
    template: str,
    data: Dict[str, Any],
    tone: str = "casual"
) -> str:
    """
    多模板风格化生成算法
    
    支持模板：
    - weekly_report: 周报（professional tone）
    - daily_report: 日报（professional tone）
    - todo_list: 待办整理（casual tone）
    - mood_support: 心情支持（warm tone）
    
    算法步骤：
    1. 检索风格参考：查询用户历史相似内容
    2. 构建模板 Prompt：结合模板指导和用户风格
    3. 数据格式化：将结构化数据转换为自然语言描述
    4. LLM 生成：Temperature 根据 tone 调整
       - professional: 0.5（稳定）
       - warm: 0.7（温暖）
       - casual: 0.8（自然）
    5. Markdown 格式化输出
    """
```

#### 3.2.2 AnalyzeEngine 算法增强

**核心算法**：

```python
class AnalyzeEngine:
    """分析引擎 - 数据分析与洞察生成"""
    
    async def extract_insights(
        self,
        documents: List[Document],
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        洞察提取算法
        
        支持指标：
        1. key_tasks: 关键任务提取
           算法：实体频率统计（Counter）
           输出：Top 10 高频实体 + 提及次数
        
        2. achievements: 成就识别
           算法：importance > 0.7 的文档
           输出：Top 5 高重要性记录
        
        3. challenges: 挑战识别
           算法：情绪分析（LLM）识别负面情绪记录
           输出：挑战列表
        
        4. time_stats: 时间统计
           算法：按时间分组统计文档数量
           输出：每日/每周活动分布
        
        5. trends: 趋势分析
           算法：时间序列对比分析
           输出：上升/稳定/下降趋势
        """
```

**情绪识别算法**：

```python
async def detect_emotion(
    self,
    text: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    情绪识别算法（基于 LLM）
    
    算法流程：
    1. Prompt 构建：
       - 输入文本
       - 上下文信息（时间、场景等）
       - 要求 JSON 格式输出
    
    2. LLM 分析（Temperature 0.3，保证稳定性）：
       - type: 情绪类型（happy/sad/angry/anxious等）
       - intensity: 情绪强度（0.0-1.0）
       - confidence: 置信度（0.0-1.0）
    
    3. 结果解析：
       - 解析 JSON 响应
       - 兜底策略：解析失败返回 neutral
    
    输出格式：
    {
      "type": "happy",
      "intensity": 0.8,
      "confidence": 0.9
    }
    """
```

### 3.3 检索算法层 (retrieval/)

#### 3.3.1 HybridRetriever 混合检索算法

**核心算法**：

```python
class HybridRetriever:
    """混合检索器 - 融合向量、关键词、时间三种检索策略"""
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[SearchResult]:
        """
        混合检索算法
        
        算法流程：
        1. 并行检索（3 路并发）：
           a) 向量检索：Faiss 语义相似度（cosine similarity）
           b) 关键词检索：BM25 算法（基于倒排索引）
           c) 时间检索：时间衰减权重（越新权重越高）
        
        2. 分数归一化（Min-Max Normalization）：
           - 向量分数：1 / (1 + distance)
           - 关键词分数：BM25 归一化到 [0, 1]
           - 时间分数：exp(-λ * days_ago)，λ=0.1
        
        3. 加权融合：
           final_score = 
             vector_weight * vector_score + 
             keyword_weight * keyword_score + 
             time_weight * time_score
           
           默认权重：vector 0.4, keyword 0.4, time 0.2
        
        4. 去重排序：
           - 按 doc_id 去重（保留最高分）
           - 按 final_score 降序排序
           - 返回 Top K
        """
```

**时间衰减算法**：

```python
def calculate_time_score(doc_timestamp: datetime) -> float:
    """
    时间衰减分数计算
    
    算法：指数衰减函数
    score = exp(-λ * days_ago)
    
    参数：
    - λ (lambda): 衰减率，默认 0.1
    - days_ago: 文档距今天数
    
    示例：
    - 今天的文档：exp(-0.1 * 0) = 1.0
    - 7天前：exp(-0.1 * 7) ≈ 0.50
    - 30天前：exp(-0.1 * 30) ≈ 0.05
    
    效果：保证近期文档获得更高权重
    """
    days_ago = (datetime.now() - doc_timestamp).days
    return math.exp(-0.1 * days_ago)
```

#### 3.3.2 GraphRetriever 图谱检索算法

**核心算法**：

```python
class GraphRetriever:
    """图谱检索器 - 基于实体关系的检索"""
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        图谱检索算法
        
        算法流程：
        1. 实体识别：
           - 使用 HybridNER 提取查询中的实体
           - 实体类型：PERSON, ORG, CONCEPT, TOPIC 等
        
        2. 图谱查询（Cypher）：
           MATCH (d:Document)-[r:MENTIONS]->(e:Entity)
           WHERE e.name IN $entities
           RETURN d, SUM(r.weight) as score
           ORDER BY score DESC
           LIMIT $top_k
        
        3. 多跳扩展（可选）：
           - 1-hop: 直接提及的文档
           - 2-hop: 通过共同实体关联的文档
           - 关系权重递减：weight * 0.5^hop_distance
        
        4. 分数计算：
           score = Σ(mention_weight) * entity_importance
           
           其中：
           - mention_weight: MENTIONS 关系权重（NER 置信度）
           - entity_importance: 实体重要性（全局频率）
        """
```

### 3.4 NER 实体识别层 (ner/)

#### 3.4.1 HybridNER 混合实体识别算法

**核心算法**：

```python
class HybridNER:
    """混合 NER - 结合规则和 LLM 的实体识别"""
    
    async def extract(self, text: str) -> List[Entity]:
        """
        混合实体识别算法
        
        算法流程：
        1. 规则识别（SimpleNER）：
           - 关键词匹配：基于领域词典
           - 正则表达式：日期、数字、邮箱等
           - 优势：快速、准确率高（特定领域）
        
        2. LLM 识别（LLMNER）：
           - Prompt 模板：
             "请从以下文本中提取实体，返回 JSON 格式：
              [{name: '实体名', type: '类型', score: 置信度}]"
           - 实体类型：PERSON, ORG, LOCATION, CONCEPT, TOPIC
           - 优势：覆盖面广、理解上下文
        
        3. 结果融合：
           - 去重：相同 name 的实体只保留一个
           - 分数合并：平均两种方法的置信度
           - 排序：按 score 降序排序
        
        4. 输出过滤：
           - score < 0.5 的实体丢弃
           - 停用词过滤（"的"、"了"、"是"等）
        
        输出：List[Entity]
        Entity: {text: str, type: str, score: float}
        """
```

**实体类型定义**：

| 实体类型 | 说明 | 示例 |
|---------|------|------|
| PERSON | 人物 | "张三"、"小明" |
| ORG | 组织机构 | "阿里巴巴"、"清华大学" |
| LOCATION | 地点 | "北京"、"杭州" |
| CONCEPT | 概念术语 | "向量检索"、"深度学习" |
| TOPIC | 话题主题 | "项目管理"、"健康生活" |
| EVENT | 事件 | "会议"、"旅行" |
| DATE | 日期 | "2025-01-07"、"今天" |

### 3.5 存储抽象层 (storage/)

#### 3.5.1 FaissStore 向量存储算法

**核心算法**：

```python
class FaissStore:
    """Faiss 向量存储"""
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10
    ) -> List[Dict]:
        """
        向量检索算法
        
        使用 Faiss 索引类型：
        1. IndexFlatL2（小规模 <10万）：
           - 精确检索（100% recall）
           - L2 距离：d = sqrt(Σ(qi - di)^2)
           - 时间复杂度：O(n)
        
        2. IndexIVFFlat（大规模 >10万）：
           - 倒排索引 + 聚类
           - nlist = sqrt(n) 个聚类中心
           - 搜索时探测 nprobe 个簇
           - 时间复杂度：O(nprobe * n/nlist)
        
        3. IndexHNSWFlat（超大规模 >100万）：
           - 分层导航小世界图
           - M = 32（每个节点连接数）
           - efConstruction = 200（构建时探索范围）
           - efSearch = 50（搜索时探索范围）
           - 时间复杂度：O(log n)
        
        分数转换：
        score = 1 / (1 + distance)
        
        输出：[(doc_id, score), ...]
        """
```

**索引构建算法**：

```python
async def build_index(
    self,
    dimension: int,
    n_docs: int
) -> faiss.Index:
    """
    自适应索引选择算法
    
    策略：
    if n_docs < 10_000:
        # 小规模：精确检索
        return faiss.IndexFlatL2(dimension)
    
    elif n_docs < 100_000:
        # 中规模：倒排索引
        nlist = int(math.sqrt(n_docs))
        quantizer = faiss.IndexFlatL2(dimension)
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
        return index
    
    else:
        # 大规模：HNSW 图索引
        index = faiss.IndexHNSWFlat(dimension, M=32)
        index.hnsw.efConstruction = 200
        return index
    
    优势：根据数据规模自动选择最优索引类型
    """
```

#### 3.5.2 FalkorStore 图谱存储算法

**核心算法**：

```python
class FalkorStore:
    """FalkorDB 图谱存储"""
    
    async def search_by_entities(
        self,
        query: str,
        entities: List[str],
        top_k: int = 10
    ) -> List[Dict]:
        """
        基于实体的图谱检索算法
        
        Cypher 查询策略：
        
        1. 单跳查询（直接关联）：
        MATCH (d:Document)-[r:MENTIONS]->(e:Entity)
        WHERE e.name IN $entities
        RETURN d.id as doc_id, 
               SUM(r.weight) as score,
               COUNT(e) as entity_count
        ORDER BY score DESC, entity_count DESC
        LIMIT $top_k
        
        2. 多跳查询（间接关联）：
        MATCH (d:Document)-[r1:MENTIONS]->(e1:Entity),
              (d2:Document)-[r2:MENTIONS]->(e1)
        WHERE e1.name IN $entities AND d.id <> d2.id
        RETURN d2.id as doc_id,
               SUM(r1.weight * r2.weight * 0.5) as score
        ORDER BY score DESC
        LIMIT $top_k
        
        3. 时间演化查询：
        MATCH (d:Document)-[r:MENTIONS]->(e:Entity)
        WHERE e.name = $entity
        RETURN d.timestamp, COUNT(d) as mention_count
        ORDER BY d.timestamp
        
        分数计算：
        score = Σ(mention_weight) * entity_freq_weight
        
        其中：
        - mention_weight: NER 置信度
        - entity_freq_weight: log(1 + global_freq)
        """
```

### 3.6 数据访问层 (repository/)

#### 3.6.1 HybridRepository 混合检索算法

**核心算法**：

```python
class HybridRepository:
    """混合存储仓库 - 协调 Faiss + FalkorDB + SQLite"""
    
    async def hybrid_search(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        top_k: int = 10,
        faiss_weight: float = 0.6,
        graph_weight: float = 0.4
    ) -> List[SearchResult]:
        """
        混合检索融合算法
        
        算法流程：
        1. 并行检索：
           Task 1: Faiss 向量检索（Top 2K）
           Task 2: FalkorDB 图谱检索（Top 2K）
        
        2. 分数归一化：
           - Faiss 分数：已在 [0, 1] 范围
           - Graph 分数：score / max_score
        
        3. 加权融合：
           merged_score = 
             faiss_weight * faiss_score + 
             graph_weight * graph_score
        
        4. 去重合并：
           scores = {}
           for faiss_result:
             scores[doc_id] += faiss_weight * score
           for graph_result:
             scores[doc_id] += graph_weight * score
        
        5. 排序 & 返回：
           sorted_docs = sorted(scores.items(), key=score, reverse=True)
           return sorted_docs[:top_k]
        
        优势：
        - Faiss 保证语义相关性
        - Graph 保证关系关联性
        - 融合提升召回率和准确率
        """
```

**数据生命周期管理算法**：

```python
async def lifecycle_management(self):
    """
    数据分层生命周期算法
    
    分层策略：
    ┌──────────────────────────────────────┐
    │  HOT (热数据, 0-7天)                 │
    │  - 存储：Faiss + FalkorDB + SQLite   │
    │  - 用途：实时检索、高频访问           │
    └──────────────────────────────────────┘
              ↓ (7天后)
    ┌──────────────────────────────────────┐
    │  WARM (温数据, 7-30天)               │
    │  - 存储：Faiss + FalkorDB + SQLite   │
    │  - 用途：历史回溯、趋势分析           │
    └──────────────────────────────────────┘
              ↓ (30天后)
    ┌──────────────────────────────────────┐
    │  COLD (冷数据, 30天+)                │
    │  - 存储：仅 FalkorDB + SQLite        │
    │  - 用途：长期知识图谱、深度分析       │
    └──────────────────────────────────────┘
    
    降温算法：
    1. HOT → WARM（7天）：
       if doc.age > 7 days:
         if doc.importance > 0.7:
           # 重要文档保留在 Faiss
           doc.layer = WARM
         else:
           # 普通文档移出 Faiss
           faiss.remove(doc.id)
           doc.layer = COLD
           doc.stored_in_faiss = False
    
    2. WARM → COLD（30天）：
       if doc.age > 30 days:
         faiss.remove(doc.id)
         doc.layer = COLD
         doc.stored_in_faiss = False
    
    优势：
    - 节省 Faiss 内存（仅保留热温数据）
    - 长期知识图谱保留在 FalkorDB
    - 重要文档延长热数据周期
    """
```

---

## 4. 算法性能优化

### 4.1 检索性能优化

| 优化策略 | 算法实现 | 性能提升 |
|---------|---------|---------|
| **批量向量化** | 使用 batch embedding，减少 API 调用 | 5x |
| **缓存机制** | 查询结果缓存（5分钟 TTL） | 10x |
| **并行检索** | asyncio.gather 并发 Faiss + Graph | 2x |
| **索引优化** | HNSW 索引（大规模数据） | 100x |
| **分数归一化** | Min-Max 快速归一化 | 无损 |

### 4.2 实体识别优化

| 优化策略 | 算法实现 | 准确率提升 |
|---------|---------|-----------|
| **混合 NER** | 规则 + LLM 双路融合 | +15% |
| **领域词典** | 预定义高频实体词典 | +10% |
| **上下文窗口** | 提取实体时保留前后文 | +8% |
| **置信度过滤** | score < 0.5 的实体丢弃 | 精准度 +12% |

### 4.3 图谱查询优化

| 优化策略 | 算法实现 | 性能提升 |
|---------|---------|---------|
| **索引优化** | Entity.name, Document.timestamp 索引 | 10x |
| **多跳限制** | 限制最多 2 跳，避免过深遍历 | 5x |
| **批量查询** | 使用 UNWIND 批量创建关系 | 20x |
| **缓存热点** | 高频实体查询结果缓存 | 3x |

---

## 5. 算法与后端的集成设计

### 5.1 职责划分

| 模块 | 职责 | 算法示例 |
|------|------|---------|
| **AME 核心算法** | 纯算法逻辑，接收参数返回结果 | `WorkEngine.generate_weekly_report()` |
| **Backend Service** | 业务编排，参数准备，结果转换 | `WorkService.generate_weekly_report()` |
| **Backend API** | HTTP 路由，请求验证，响应序列化 | `POST /api/v1/work/weekly-report` |

### 5.2 数据库配置隔离

**后端职责**：

```python
# backend/app/main.py
from ame.repository.hybrid_repository import HybridRepository
from ame.storage.faiss_store import FaissStore
from ame.storage.falkor_store import FalkorStore
from ame.storage.metadata_store import MetadataStore

# 后端提供配置参数
def initialize_ame():
    """后端负责初始化 AME 存储"""
    
    # 1. 初始化 Faiss（后端配置路径）
    faiss_store = FaissStore(
        dimension=1536,
        index_path=settings.DATA_DIR / "faiss" / "work.index"
    )
    
    # 2. 初始化 FalkorDB（后端配置连接）
    falkor_store = FalkorStore(
        host=settings.FALKORDB_HOST,
        port=settings.FALKORDB_PORT,
        graph_name="another_me_work"
    )
    
    # 3. 初始化 SQLite（后端配置路径）
    metadata_store = MetadataStore(
        db_path=settings.DATA_DIR / "metadata" / "work.db"
    )
    
    # 4. 创建 HybridRepository
    repository = HybridRepository(
        faiss_store=faiss_store,
        falkor_store=falkor_store,
        metadata_store=metadata_store
    )
    
    return repository
```

**AME 职责**：

```python
# ame/engines/work_engine.py
class WorkEngine:
    """AME 专注算法逻辑，接收 Repository 依赖注入"""
    
    def __init__(
        self,
        repository: HybridRepository,  # 后端传入
        llm_caller: LLMCaller,         # 后端传入
        analyze_engine: AnalyzeEngine  # 后端传入
    ):
        self.repo = repository
        self.llm = llm_caller
        self.analyzer = analyze_engine
    
    async def generate_weekly_report(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> WeeklyReport:
        """纯算法逻辑，不关心数据库配置"""
        # 算法实现...
```

### 5.3 API 接口设计

**前端需求 → 后端 API → AME 算法映射**：

| 前端需求 | 后端 API | AME 算法 |
|---------|---------|---------|
| 生成周报 | `POST /work/weekly-report` | `WorkEngine.generate_weekly_report()` |
| 生成日报 | `POST /work/daily-report` | `WorkEngine.generate_daily_report()` |
| 整理待办 | `POST /work/organize-todos` | `WorkEngine.organize_todos()` |
| 会议总结 | `POST /work/summarize-meeting` | `WorkEngine.summarize_meeting()` |
| 项目追踪 | `POST /work/track-project` | `WorkEngine.track_project_progress()` |
| 心情分析 | `POST /life/analyze-mood` | `LifeEngine.analyze_mood()` |
| 兴趣追踪 | `GET /life/track-interests` | `LifeEngine.track_interests()` |
| 生活总结 | `POST /life/life-summary` | `AnalyzeEngine.generate_report()` |
| 生活建议 | `POST /life/suggestions` | `LifeEngine.generate_life_suggestions()` |
| 记录事件 | `POST /life/record-event` | `Repository.create()` |

---

## 6. 算法测试策略

### 6.1 单元测试

**测试覆盖**：

```python
# tests/unit/test_work_engine.py
class TestWorkEngine:
    """WorkEngine 算法单元测试"""
    
    @pytest.mark.asyncio
    async def test_prioritize_tasks_algorithm(self):
        """测试待办优先级算法"""
        tasks = [
            TaskInfo(content="紧急修复 Bug"),      # 预期 high
            TaskInfo(content="学习新技术"),        # 预期 low
            TaskInfo(content="重要项目评审"),      # 预期 high
        ]
        
        result = await engine.prioritize_tasks(tasks)
        
        assert result[0].content == "紧急修复 Bug"
        assert result[0].priority_score >= 70
        assert result[-1].priority_score < 40
```

**测试指标**：
- 算法正确性：断言输出符合预期
- 边界条件：空输入、异常输入
- 性能基准：单次调用 < 100ms

### 6.2 集成测试

```python
# tests/integration/test_hybrid_repository.py
class TestHybridRepository:
    """混合检索算法集成测试"""
    
    @pytest.mark.asyncio
    async def test_hybrid_search_fusion(self):
        """测试 Faiss + Graph 融合检索"""
        # 准备数据
        await repo.create(doc1)  # 向量相关
        await repo.create(doc2)  # 图谱相关
        
        # 执行混合检索
        results = await repo.hybrid_search(
            query="项目进度",
            faiss_weight=0.6,
            graph_weight=0.4
        )
        
        # 验证融合效果
        assert len(results) > 0
        assert any(r.source == "hybrid" for r in results)
```

### 6.3 性能测试

```python
# tests/performance/test_search_performance.py
class TestSearchPerformance:
    """检索性能测试"""
    
    @pytest.mark.benchmark
    async def test_faiss_search_latency(self, benchmark):
        """Faiss 检索延迟测试"""
        result = benchmark(lambda: faiss.search(query_vec, 10))
        
        # 断言延迟 < 10ms
        assert result.stats.mean < 0.01
```

---

## 7. 算法迭代计划

### Phase 1: 核心算法完善（当前）

**目标**：完成基础算法实现

- ✅ WorkEngine 算法（周报、日报、待办、会议、项目）
- ✅ LifeEngine 算法（心情、兴趣、建议、回忆）
- ✅ MimicEngine 流式生成
- ✅ AnalyzeEngine 洞察提取
- ✅ HybridRetriever 混合检索
- ✅ HybridRepository 融合算法

### Phase 2: 算法优化（2周）

**目标**：性能和准确率提升

**检索优化**：
- 实现 Faiss HNSW 索引（大规模数据）
- 实现查询缓存机制（Redis）
- 优化 Cypher 查询（添加索引）

**NER 优化**：
- 扩充领域词典（工作、生活专用词典）
- 实现实体链接（Entity Linking）
- 增加实体消歧义（Disambiguation）

**评分算法优化**：
- 实现 Learning to Rank（LTR）
- 用户反馈学习（点击率、停留时间）
- A/B 测试不同权重组合

### Phase 3: 高级算法（4周）

**目标**：引入先进算法

**个性化推荐**：
- 协同过滤算法（用户-兴趣矩阵）
- 内容推荐算法（基于图谱）
- 冷启动策略

**趋势预测**：
- 时间序列预测（ARIMA/LSTM）
- 兴趣演化预测
- 情绪趋势预警

**知识推理**：
- 图谱推理引擎（基于 Cypher）
- 因果关系分析
- 反事实推理

### Phase 4: 模型微调（6周）

**目标**：领域模型优化

**LLM 微调**：
- 用户风格 LoRA 微调
- 领域知识注入
- 个性化 Prompt 优化

**向量模型优化**：
- Embedding 模型蒸馏
- 多任务学习（检索 + 分类）
- 对比学习优化

---

## 8. 算法监控指标

### 8.1 性能指标

| 指标 | 目标 | 监控方式 |
|------|------|---------|
| 检索延迟 | P95 < 100ms | Prometheus + Grafana |
| 向量化延迟 | P95 < 50ms | 日志统计 |
| LLM 调用延迟 | P95 < 2s | OpenAI API 监控 |
| 内存占用 | < 2GB | 系统监控 |
| 吞吐量 | > 100 QPS | 压力测试 |

### 8.2 准确率指标

| 指标 | 目标 | 评估方式 |
|------|------|---------|
| 检索召回率 | > 85% | 人工标注测试集 |
| NER 准确率 | > 80% | 实体标注数据集 |
| 情绪识别准确率 | > 75% | 情绪标注数据集 |
| 用户满意度 | > 4.0/5.0 | 用户反馈评分 |

### 8.3 算法稳定性

| 指标 | 目标 | 监控方式 |
|------|------|---------|
| 成功率 | > 99% | 错误日志统计 |
| 异常率 | < 1% | 异常捕获监控 |
| 数据一致性 | 100% | 定期数据校验 |

