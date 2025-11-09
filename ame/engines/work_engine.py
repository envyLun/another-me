"""
工作场景引擎 - WorkEngine
负责工作相关的AI辅助功能实现
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter

from ame.repository.hybrid_repository import HybridRepository
from ame.mem.mimic_engine import MimicEngine
from ame.mem.analyze_engine import AnalyzeEngine
from ame.models.domain import Document, DocumentType
from ame.models.report_models import (
    WeeklyReport,
    DailyReport,
    TaskSummary,
    Achievement,
    OrganizedTodos,
    TaskInfo,
    ProjectProgress,
)
from ame.llm_caller.caller import LLMCaller


class WorkEngine:
    """
    工作场景引擎
    
    职责：
    - 周报/日报生成
    - 待办事项智能整理
    - 会议内容结构化总结
    - 项目进度追踪分析
    """
    
    def __init__(
        self,
        repository: HybridRepository,
        llm_caller: LLMCaller,
        mimic_engine: Optional[MimicEngine] = None,
        analyze_engine: Optional[AnalyzeEngine] = None
    ):
        """
        初始化工作引擎
        
        Args:
            repository: 混合存储仓库
            llm_caller: LLM 调用器
            mimic_engine: 模仿引擎（可选，用于生成用户风格文本）
            analyze_engine: 分析引擎（可选，用于数据分析）
        """
        self.repo = repository
        self.llm = llm_caller
        self.mimic = mimic_engine
        self.analyzer = analyze_engine or AnalyzeEngine(repository, llm_caller)
    
    async def generate_weekly_report(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        style: str = "professional"
    ) -> WeeklyReport:
        """
        生成工作周报
        
        流程：
        1. 数据收集：从 HybridRepository 检索工作记录
        2. 数据分析：使用 AnalyzeEngine 提取关键任务、成果、挑战
        3. 风格生成：使用 MimicEngine 以用户风格撰写周报
        4. 结构化输出
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            style: 语气风格（professional/casual）
        
        Returns:
            WeeklyReport: 结构化周报对象
        """
        # Step 1: 收集数据
        work_logs = await self._collect_work_logs(start_date, end_date)
        
        # Step 2: 分析数据
        insights = await self.analyzer.extract_insights(
            documents=work_logs,
            metrics=[
                "key_tasks",       # 关键任务
                "achievements",    # 成果
                "challenges",      # 挑战
                "time_stats",      # 时间统计
            ]
        )
        
        # Step 3: 生成周报内容
        report_content = await self._generate_report_text(
            insights=insights,
            period=(start_date, end_date),
            report_type="weekly",
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
        # 计算当日时间范围
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Step 1: 收集数据
        work_logs = await self._collect_work_logs(start_date, end_date)
        
        # Step 2: 分析数据
        insights = await self.analyzer.extract_insights(
            documents=work_logs,
            metrics=["key_tasks", "achievements", "highlights"]
        )
        
        # Step 3: 生成日报内容
        report_content = await self._generate_report_text(
            insights=insights,
            period=(start_date, end_date),
            report_type="daily",
            style=style
        )
        
        # Step 4: 结构化输出
        tasks = self._parse_task_summaries(insights.get("key_tasks", []))
        
        return DailyReport(
            user_id=user_id,
            date=date,
            content=report_content,
            tasks_completed=[t for t in tasks if t.status == "completed"],
            tasks_ongoing=[t for t in tasks if t.status == "ongoing"],
            highlights=insights.get("highlights", []),
            tomorrow_plan=[],  # TODO: 从用户数据中提取明日计划
            generated_at=datetime.now()
        )
    
    async def organize_todos(
        self,
        raw_todos: List[str],
        context: Optional[Dict] = None
    ) -> OrganizedTodos:
        """
        智能整理待办事项
        
        流程：
        1. 任务解析：提取任务实体和关键信息
        2. 优先级评估：基于紧急度、重要性、依赖关系
        3. 智能分组：按类别、项目、时间
        4. 去重合并：识别重复或相似任务
        
        Args:
            raw_todos: 原始待办列表
            context: 上下文信息
        
        Returns:
            OrganizedTodos: 整理后的待办事项
        """
        # Step 1: 任务解析
        parsed_tasks = []
        for todo in raw_todos:
            task_info = await self._parse_task(todo)
            parsed_tasks.append(task_info)
        
        # Step 2: 优先级评估
        prioritized = await self._prioritize_tasks(parsed_tasks, context)
        
        # Step 3: 智能分组
        high_priority = [t for t in prioritized if t.priority_score >= 70]
        medium_priority = [t for t in prioritized if 40 <= t.priority_score < 70]
        low_priority = [t for t in prioritized if t.priority_score < 40]
        
        # Step 4: 生成整理后的文本
        formatted_text = await self._format_todos(
            high_priority, medium_priority, low_priority
        )
        
        return OrganizedTodos(
            high_priority=high_priority,
            medium_priority=medium_priority,
            low_priority=low_priority,
            formatted_text=formatted_text,
            original_count=len(raw_todos),
            organized_count=len(prioritized)
        )
    
    async def summarize_meeting(
        self,
        meeting_content: str,
        meeting_date: datetime,
        participants: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        会议内容结构化总结
        
        流程：
        1. 使用 LLM 结构化提取会议要点
        2. 识别关键决策、行动项、责任人
        3. 生成 Markdown 格式的会议纪要
        
        Args:
            meeting_content: 会议记录原文
            meeting_date: 会议日期
            participants: 参与者列表
        
        Returns:
            structured_summary: {
                'summary': str,  # 会议摘要
                'key_points': List[str],  # 关键要点
                'decisions': List[str],  # 决策事项
                'action_items': List[Dict],  # 行动项 [{'task': str, 'owner': str, 'deadline': str}]
                'formatted_minutes': str  # Markdown 格式会议纪要
            }
        """
        # 构建 LLM Prompt
        prompt = f"""请从以下会议记录中提取关键信息，以JSON格式返回：

**会议时间**: {meeting_date.strftime('%Y-%m-%d %H:%M')}
**参与者**: {', '.join(participants) if participants else '未记录'}

**会议内容**:
{meeting_content}

请提取以下信息并以JSON格式返回：
{{
  "summary": "会议核心摘要（2-3句话）",
  "key_points": ["要点1", "要点2", "要点3"],
  "decisions": ["决策1", "决策2"],
  "action_items": [
    {{"task": "任务描述", "owner": "负责人", "deadline": "截止日期或空字符串"}}
  ]
}}

只返回JSON，不要其他内容。
"""
        
        try:
            response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # 简化处理：返回基本结构
            import json
            try:
                data = json.loads(response.content)
            except:
                # JSON 解析失败，返回默认结构
                data = {
                    "summary": meeting_content[:100] + "...",
                    "key_points": [],
                    "decisions": [],
                    "action_items": []
                }
            
            # 生成 Markdown 格式会议纪要
            formatted_minutes = self._format_meeting_minutes(
                meeting_date, participants, data
            )
            
            return {
                **data,
                'formatted_minutes': formatted_minutes
            }
        
        except Exception as e:
            # 异常处理：返回基本摘要
            return {
                'summary': meeting_content[:100] + "...",
                'key_points': [],
                'decisions': [],
                'action_items': [],
                'formatted_minutes': f"# 会议纪要\n\n{meeting_content}"
            }
    
    async def track_project_progress(
        self,
        project_name: str,
        user_id: str
    ) -> ProjectProgress:
        """
        追踪项目进度
        
        流程：
        1. 图谱查询：查找项目相关的任务节点
        2. 状态分析：统计已完成/进行中/未开始
        3. 时间线分析：生成项目时间线
        4. 风险识别：识别延期风险和阻塞点
        
        Args:
            project_name: 项目名称
            user_id: 用户ID
        
        Returns:
            ProjectProgress: 项目进度对象
        """
        # Step 1: 检索项目相关记录
        project_docs = await self.repo.hybrid_search(
            query=f"项目:{project_name}",
            top_k=50
        )
        
        # Step 2: 状态分析
        status_stats = await self._analyze_project_status(project_docs)
        
        # Step 3: 时间线生成
        timeline = await self._generate_project_timeline(project_docs)
        
        # Step 4: 风险识别
        risks = await self._identify_project_risks(project_docs, timeline)
        
        # Step 5: 生成进度报告
        report = await self._generate_project_report(
            project_name, status_stats, timeline, risks
        )
        
        return ProjectProgress(
            project_name=project_name,
            completion_rate=status_stats.get("completion_rate", 0.0),
            status=status_stats,
            timeline=timeline,
            risks=risks,
            report=report
        )
    
    # ==================== 辅助方法 ====================
    
    async def _collect_work_logs(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Document]:
        """收集工作记录"""
        return await self.analyzer.collect_time_range(
            user_id="default",  # TODO: 传入实际用户ID
            start=start_date,
            end=end_date,
            category="work"
        )
    
    async def _generate_report_text(
        self,
        insights: Dict[str, Any],
        period: tuple,
        report_type: str,
        style: str
    ) -> str:
        """生成报告文本（使用 LLM）"""
        start_date, end_date = period
        
        # 构建 Prompt
        prompt = f"""请根据以下数据生成{report_type}报告：

**时间范围**: {start_date.date()} 至 {end_date.date()}

**关键任务**:
{self._format_insights_section(insights.get('key_tasks', []))}

**成就**:
{self._format_insights_section(insights.get('achievements', []))}

**挑战**:
{', '.join(insights.get('challenges', ['无']))}

请以{style}的风格生成Markdown格式的报告。
"""
        
        # 调用 LLM 生成
        response = await self.llm.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.content
    
    async def _parse_task(self, todo: str) -> TaskInfo:
        """解析单个任务"""
        # 使用 LLM 解析任务
        prompt = f"""解析以下待办事项，提取关键信息：

任务：{todo}

请以JSON格式返回：
{{
  "content": "任务描述",
  "entities": ["实体1", "实体2"],
  "due_date": "YYYY-MM-DD或null",
  "category": "分类"
}}
"""
        
        try:
            response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # 简化处理：直接返回 TaskInfo
            return TaskInfo(
                content=todo,
                entities=[],
                category="general"
            )
        except Exception:
            return TaskInfo(content=todo)
    
    async def _prioritize_tasks(
        self,
        tasks: List[TaskInfo],
        context: Optional[Dict]
    ) -> List[TaskInfo]:
        """
        任务优先级算法
        
        评分规则：
        1. 紧急度（0-40分）
        2. 重要性（0-40分）
        3. 依赖关系（0-20分）
        """
        for task in tasks:
            score = 0
            
            # 1. 紧急度评分
            urgency_keywords = {
                "紧急": 40, "今天": 40, "ASAP": 40, "asap": 40,
                "明天": 30, "本周": 25, "近期": 15
            }
            for keyword, points in urgency_keywords.items():
                if keyword in task.content:
                    score += points
                    break
            
            # 2. 重要性评分（基于关键词）
            importance_keywords = {
                "重要": 30, "关键": 30, "核心": 25,
                "优先": 20, "必须": 20
            }
            for keyword, points in importance_keywords.items():
                if keyword in task.content:
                    score += points
                    break
            
            # 3. 依赖关系评分
            if task.is_blocking_others:
                score += 20
            elif task.has_dependencies:
                score -= 10
            
            task.priority_score = min(score, 100)
        
        # 排序
        return sorted(tasks, key=lambda t: t.priority_score, reverse=True)
    
    async def _format_todos(
        self,
        high: List[TaskInfo],
        medium: List[TaskInfo],
        low: List[TaskInfo]
    ) -> str:
        """格式化待办事项为 Markdown"""
        result = "# 整理后的待办事项\n\n"
        
        if high:
            result += "## 高优先级\n\n"
            for task in high:
                result += f"- [ ] {task.content}\n"
            result += "\n"
        
        if medium:
            result += "## 中优先级\n\n"
            for task in medium:
                result += f"- [ ] {task.content}\n"
            result += "\n"
        
        if low:
            result += "## 低优先级\n\n"
            for task in low:
                result += f"- [ ] {task.content}\n"
            result += "\n"
        
        return result
    
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
    
    async def _analyze_project_status(self, docs: List[Any]) -> Dict[str, Any]:
        """分析项目状态"""
        # 简化实现
        total = len(docs)
        return {
            "total_tasks": total,
            "completed": 0,
            "in_progress": total,
            "completion_rate": 0.0
        }
    
    async def _generate_project_timeline(self, docs: List[Any]) -> List[Dict[str, Any]]:
        """生成项目时间线"""
        timeline = []
        for doc in docs[:10]:
            timeline.append({
                "date": doc.timestamp.isoformat() if hasattr(doc, 'timestamp') else datetime.now().isoformat(),
                "event": "项目活动",
                "description": ""
            })
        return timeline
    
    async def _identify_project_risks(
        self,
        docs: List[Any],
        timeline: List[Dict]
    ) -> List[str]:
        """识别项目风险"""
        risks = []
        if len(docs) < 5:
            risks.append("项目记录较少，可能存在进度跟踪不足的风险")
        return risks
    
    async def _generate_project_report(
        self,
        project_name: str,
        status: Dict,
        timeline: List[Dict],
        risks: List[str]
    ) -> str:
        """生成项目进度报告"""
        report = f"# {project_name} 项目进度报告\n\n"
        report += f"**完成率**: {status.get('completion_rate', 0) * 100:.1f}%\n\n"
        report += f"**总任务数**: {status.get('total_tasks', 0)}\n\n"
        
        if risks:
            report += "## 风险提示\n\n"
            for risk in risks:
                report += f"- {risk}\n"
        
        return report
    
    def _format_insights_section(self, items: List[Any]) -> str:
        """格式化洞察部分"""
        if not items:
            return "无"
        
        result = ""
        for item in items[:5]:
            if isinstance(item, dict):
                result += f"- {item.get('entity', item.get('content', '未知'))}\n"
            else:
                result += f"- {str(item)}\n"
        return result
    
    def _format_meeting_minutes(
        self,
        meeting_date: datetime,
        participants: Optional[List[str]],
        data: Dict[str, Any]
    ) -> str:
        """生成 Markdown 格式会议纪要"""
        minutes = f"# 会议纪要\n\n"
        minutes += f"**时间**: {meeting_date.strftime('%Y年%m月%d日 %H:%M')}\n\n"
        
        if participants:
            minutes += f"**参与者**: {', '.join(participants)}\n\n"
        
        # 会议摘要
        minutes += f"## 会议摘要\n\n{data.get('summary', '无')}\n\n"
        
        # 关键要点
        if data.get('key_points'):
            minutes += "## 关键要点\n\n"
            for point in data['key_points']:
                minutes += f"- {point}\n"
            minutes += "\n"
        
        # 决策事项
        if data.get('decisions'):
            minutes += "## 决策事项\n\n"
            for decision in data['decisions']:
                minutes += f"- {decision}\n"
            minutes += "\n"
        
        # 行动项
        if data.get('action_items'):
            minutes += "## 行动项\n\n"
            for item in data['action_items']:
                task = item.get('task', '')
                owner = item.get('owner', '未指定')
                deadline = item.get('deadline', '待定')
                minutes += f"- **{task}** (负责人: {owner}, 截止: {deadline})\n"
            minutes += "\n"
        
        return minutes
