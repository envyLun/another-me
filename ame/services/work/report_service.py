"""
工作报告生成服务
职责: 周报/日报生成
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from ame.capabilities.analysis import DataAnalyzer
from ame.capabilities.generation import RAGGenerator
from ame.capabilities.memory import MemoryManager
from ame.models.report_models import WeeklyReport, DailyReport, TaskSummary, Achievement


class ReportService:
    """工作报告生成服务"""
    
    def __init__(
        self,
        data_analyzer: DataAnalyzer,
        rag_generator: RAGGenerator,
        memory_manager: MemoryManager
    ):
        """
        初始化报告服务
        
        Args:
            data_analyzer: 数据分析器 (Capabilities Layer)
            rag_generator: RAG 生成器 (Capabilities Layer)
            memory_manager: 记忆管理器 (Capabilities Layer)
        """
        self.analyzer = data_analyzer
        self.generator = rag_generator
        self.memory = memory_manager
    
    async def generate_weekly_report(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        style: str = "professional"
    ) -> WeeklyReport:
        """
        生成工作周报
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            style: 语气风格 (professional/casual/warm)
        
        Returns:
            WeeklyReport: 结构化周报对象
        """
        # Step 1: 收集数据
        work_logs = await self.memory.retrieve_by_timerange(
            start_time=start_date,
            end_time=end_date,
            filters={"doc_type": "work_log"}
        )
        
        # Step 2: 分析数据
        insights = await self.analyzer.analyze(
            documents=work_logs,
            metrics=["key_tasks", "achievements", "challenges", "time_stats"]
        )
        
        # Step 3: 生成报告
        report_content = await self.generator.generate(
            template="weekly_report",
            data={
                "period": f"{start_date.date()} ~ {end_date.date()}",
                "insights": insights
            },
            style=style
        )
        
        # Step 4: 结构化输出
        return WeeklyReport(
            user_id=user_id,
            period=(start_date, end_date),
            content=report_content,
            key_tasks=self._parse_task_summaries(insights.get("key_tasks", [])),
            achievements=self._parse_achievements(insights.get("achievements", [])),
            challenges=insights.get("challenges", []),
            statistics=insights.get("time_stats", {}),
            generated_at=datetime.now()
        )
    
    async def generate_daily_report(
        self,
        user_id: str,
        date: datetime,
        style: str = "professional"
    ) -> DailyReport:
        """
        生成工作日报
        
        Args:
            user_id: 用户ID
            date: 日期
            style: 语气风格
        
        Returns:
            DailyReport: 结构化日报对象
        """
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        work_logs = await self.memory.retrieve_by_timerange(
            start_time=start_date,
            end_time=end_date,
            filters={"doc_type": "work_log"}
        )
        
        insights = await self.analyzer.analyze(
            documents=work_logs,
            metrics=["key_tasks", "achievements", "highlights"]
        )
        
        report_content = await self.generator.generate(
            template="daily_report",
            data={
                "date": date.date(),
                "insights": insights
            },
            style=style
        )
        
        tasks = self._parse_task_summaries(insights.get("key_tasks", []))
        
        return DailyReport(
            user_id=user_id,
            date=date,
            content=report_content,
            tasks_completed=[t for t in tasks if t.status == "completed"],
            tasks_ongoing=[t for t in tasks if t.status == "ongoing"],
            highlights=insights.get("highlights", []),
            tomorrow_plan=[],
            generated_at=datetime.now()
        )
    
    def _parse_task_summaries(self, insights: List[Dict]) -> List[TaskSummary]:
        """解析任务摘要"""
        summaries = []
        for item in insights[:10]:
            if isinstance(item, dict):
                summaries.append(TaskSummary(
                    title=item.get("entity", "未知任务"),
                    description=item.get("content", ""),
                    status="ongoing",
                    importance=0.7,
                    mentioned_times=item.get("count", 1)
                ))
        return summaries
    
    def _parse_achievements(self, insights: List[Dict]) -> List[Achievement]:
        """解析成就"""
        achievements = []
        for item in insights[:5]:
            if isinstance(item, dict):
                timestamp_str = item.get("timestamp", datetime.now().isoformat())
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                else:
                    timestamp = datetime.now()
                
                achievements.append(Achievement(
                    title=item.get("content", "")[:50],
                    description=item.get("content", ""),
                    timestamp=timestamp,
                    importance=item.get("importance", 0.8)
                ))
        return achievements
