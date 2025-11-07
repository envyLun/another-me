"""
分析引擎 - 数据分析与洞察生成
职责：挖掘行为模式、兴趣演化、知识结构
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter

from ame.repository.hybrid_repository import HybridRepository
from ame.models.domain import Document, DocumentType


class AnalyzeEngine:
    """
    分析引擎 - "分析我" 核心能力
    
    功能：
    - 行为模式识别
    - 兴趣演化分析
    - 知识结构挖掘
    - 时间序列分析
    """
    
    def __init__(self, repository: HybridRepository, llm_caller=None):
        """
        Args:
            repository: 混合存储仓库
            llm_caller: LLM 调用器（用于深度分析）
        """
        self.repo = repository
        self.llm = llm_caller
    
    async def collect_time_range(
        self,
        user_id: str,
        start: datetime,
        end: Optional[datetime] = None,
        category: Optional[str] = None
    ) -> List[Document]:
        """
        收集时间范围内的数据
        
        Args:
            user_id: 用户ID
            start: 起始时间
            end: 结束时间（None=现在）
            category: 分类（work/life）
        
        Returns:
            documents: 文档列表
        """
        end = end or datetime.now()
        
        # 从元数据库查询
        docs = self.repo.metadata.list(
            after=start,
            before=end,
            limit=1000
        )
        
        # 过滤分类
        if category:
            if category == "work":
                docs = [d for d in docs if d.doc_type == DocumentType.WORK_LOG]
            elif category == "life":
                docs = [d for d in docs if d.doc_type == DocumentType.LIFE_RECORD]
        
        return docs
    
    async def extract_insights(
        self,
        documents: List[Document],
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        提取关键洞察
        
        Args:
            documents: 文档列表
            metrics: 指标列表（key_tasks, achievements, challenges）
        
        Returns:
            insights: 洞察结果
        """
        metrics = metrics or ["key_tasks", "achievements", "challenges"]
        
        insights = {}
        
        # 提取实体频率（关键主题）
        if "key_tasks" in metrics:
            all_entities = []
            for doc in documents:
                all_entities.extend(doc.entities)
            
            entity_freq = Counter(all_entities)
            insights["key_tasks"] = [
                {"entity": e, "count": c}
                for e, c in entity_freq.most_common(10)
            ]
        
        # 成就提取（高重要性文档）
        if "achievements" in metrics:
            achievements = [
                {
                    "content": doc.content[:100],
                    "timestamp": doc.timestamp.isoformat(),
                    "importance": doc.importance
                }
                for doc in documents
                if doc.importance > 0.7
            ]
            insights["achievements"] = achievements[:5]
        
        # 挑战识别（TODO: 使用 LLM 分析情感）
        if "challenges" in metrics:
            insights["challenges"] = []
        
        return insights
    
    async def analyze_task_graph(self, user_id: str) -> Dict[str, Any]:
        """
        分析任务图谱（基于 Falkor）
        
        Args:
            user_id: 用户ID
        
        Returns:
            task_graph: 任务关系图
        """
        # TODO: 查询 Falkor 图谱
        # 1. 找到所有任务节点
        # 2. 分析任务间依赖关系
        # 3. 识别关键路径
        
        return {
            "nodes": [],
            "edges": [],
            "critical_path": []
        }
    
    async def prioritize_tasks(
        self,
        tasks: List[Dict]
    ) -> List[Dict]:
        """
        任务优先级排序
        
        Args:
            tasks: 任务列表
        
        Returns:
            sorted_tasks: 排序后的任务
        """
        # 简单的优先级算法
        # TODO: 使用 LLM 进行智能排序
        
        def score_task(task):
            score = 0
            # 紧急程度
            if "紧急" in task.get("content", ""):
                score += 10
            # 重要程度
            if task.get("importance", 0) > 0.7:
                score += 5
            # 时间因素
            if task.get("due_date"):
                # TODO: 计算距离截止日期的时间
                pass
            return score
        
        return sorted(tasks, key=score_task, reverse=True)
    
    async def analyze_interest_evolution(
        self,
        user_id: str,
        time_windows: List[timedelta] = None
    ) -> Dict[str, Any]:
        """
        兴趣演化分析
        
        Args:
            user_id: 用户ID
            time_windows: 时间窗口列表（默认：30天、90天、365天）
        
        Returns:
            evolution: 兴趣演化数据
        """
        time_windows = time_windows or [
            timedelta(days=30),
            timedelta(days=90),
            timedelta(days=365)
        ]
        
        now = datetime.now()
        evolution = {}
        
        for window in time_windows:
            start = now - window
            docs = await self.collect_time_range(user_id, start, now)
            
            # 统计实体频率
            entities = []
            for doc in docs:
                entities.extend(doc.entities)
            
            entity_freq = Counter(entities)
            
            evolution[f"{window.days}days"] = {
                "top_interests": [
                    {"topic": e, "frequency": c}
                    for e, c in entity_freq.most_common(10)
                ],
                "total_docs": len(docs)
            }
        
        return evolution
    
    async def analyze_mood_timeline(
        self,
        user_id: str,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[Dict]:
        """
        心情时间线分析
        
        Args:
            user_id: 用户ID
            start: 起始时间
            end: 结束时间
        
        Returns:
            timeline: 心情时间线
        """
        docs = await self.collect_time_range(user_id, start, end, category="life")
        
        timeline = []
        for doc in docs:
            # 提取情绪（从 metadata 或使用 LLM 分析）
            emotion = doc.metadata.get("emotion", "neutral")
            
            timeline.append({
                "timestamp": doc.timestamp.isoformat(),
                "emotion": emotion,
                "content": doc.content[:100],
                "importance": doc.importance
            })
        
        return timeline
    
    async def generate_insights_report(
        self,
        user_id: str,
        report_type: str = "weekly"
    ) -> str:
        """
        生成洞察报告
        
        Args:
            user_id: 用户ID
            report_type: 报告类型（weekly/monthly/yearly）
        
        Returns:
            report: Markdown 格式的报告
        """
        # 确定时间范围
        now = datetime.now()
        if report_type == "weekly":
            start = now - timedelta(days=7)
        elif report_type == "monthly":
            start = now - timedelta(days=30)
        else:  # yearly
            start = now - timedelta(days=365)
        
        # 收集数据
        docs = await self.collect_time_range(user_id, start, now)
        insights = await self.extract_insights(docs)
        
        # 生成报告
        report = f"# {report_type.capitalize()} 洞察报告\n\n"
        report += f"**时间范围**: {start.date()} ~ {now.date()}\n\n"
        report += f"**数据量**: {len(docs)} 条记录\n\n"
        
        # 关键主题
        if "key_tasks" in insights:
            report += "## 关键主题\n\n"
            for item in insights["key_tasks"][:5]:
                report += f"- **{item['entity']}**: {item['count']} 次提及\n"
            report += "\n"
        
        # 成就
        if "achievements" in insights:
            report += "## 重要成就\n\n"
            for item in insights["achievements"]:
                report += f"- {item['content']}... ({item['timestamp'][:10]})\n"
            report += "\n"
        
        return report
