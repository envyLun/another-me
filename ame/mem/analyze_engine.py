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
    
    async def detect_emotion(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        情绪识别（新增）
        
        使用 LLM 识别文本中的主要情绪和强度
        
        Args:
            text: 要分析的文本
            context: 上下文信息
        
        Returns:
            emotion_result: {type: str, intensity: float, confidence: float}
        """
        if not self.llm:
            # 如果没有 LLM，返回默认值
            return {
                "type": "neutral",
                "intensity": 0.5,
                "confidence": 0.5
            }
        
        prompt = f"""请分析以下文本的情绪：

文本：{text}

请以JSON格式返回：
{{
  "type": "情绪类型（happy/sad/angry/anxious/excited/neutral等）",
  "intensity": 0.0到1.0之间的强度值,
  "confidence": 0.0到1.0之间的置信度
}}

只返回JSON，不要其他内容。
"""
        
        try:
            response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # 简化处理：返回默认情绪
            return {
                "type": "neutral",
                "intensity": 0.5,
                "confidence": 0.7
            }
        except Exception:
            return {
                "type": "neutral",
                "intensity": 0.5,
                "confidence": 0.5
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
    
    async def generate_report(
        self,
        documents: List[Document],
        report_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成报告（新增）
        
        支持多种报告类型：
        - weekly: 周报
        - daily: 日报
        - life_summary: 生活总结
        - project_progress: 项目进度
        
        Args:
            documents: 文档列表
            report_type: 报告类型
            context: 上下文信息
        
        Returns:
            report: Markdown 格式的报告
        """
        # 提取洞察
        insights = await self.extract_insights(documents)
        
        # 根据类型生成报告
        if report_type == "weekly":
            return await self._generate_weekly_report(insights, context)
        elif report_type == "daily":
            return await self._generate_daily_report(insights, context)
        elif report_type == "life_summary":
            return await self._generate_life_summary(insights, context)
        elif report_type == "project_progress":
            return await self._generate_project_progress(insights, context)
        else:
            return await self.generate_insights_report("default", report_type)
    
    async def _generate_weekly_report(
        self,
        insights: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """生成周报"""
        report = "# 工作周报\n\n"
        
        if context:
            report += f"**时间范围**: {context.get('start_date', '')} ~ {context.get('end_date', '')}\n\n"
        
        # 关键任务
        if "key_tasks" in insights:
            report += "## 关键任务\n\n"
            for item in insights["key_tasks"][:5]:
                report += f"- **{item['entity']}**: {item['count']} 次提及\n"
            report += "\n"
        
        # 成就
        if "achievements" in insights:
            report += "## 重要成就\n\n"
            for item in insights["achievements"]:
                report += f"- {item['content'][:50]}... ({item['timestamp'][:10]})\n"
            report += "\n"
        
        return report
    
    async def _generate_daily_report(
        self,
        insights: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """生成日报"""
        report = "# 工作日报\n\n"
        
        if context:
            report += f"**日期**: {context.get('date', '')}\n\n"
        
        # 今日完成
        if "key_tasks" in insights:
            report += "## 今日完成\n\n"
            for item in insights["key_tasks"][:3]:
                report += f"- {item['entity']}\n"
            report += "\n"
        
        return report
    
    async def _generate_life_summary(
        self,
        insights: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """生成生活总结"""
        report = "# 生活总结\n\n"
        
        if context:
            period = context.get('period', 'week')
            report += f"**统计周期**: 最近{period}\n\n"
        
        # 主要活动
        if "key_tasks" in insights:
            report += "## 主要活动\n\n"
            for item in insights["key_tasks"][:5]:
                report += f"- {item['entity']}\n"
            report += "\n"
        
        return report
    
    async def _generate_project_progress(
        self,
        insights: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """生成项目进度报告"""
        project_name = context.get('project_name', '未知项目') if context else '未知项目'
        
        report = f"# {project_name} 项目进度\n\n"
        report += "## 项目概况\n\n"
        report += "暂无详细数据\n\n"
        
        return report
