"""
工作引擎单元测试
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from ame.engines.work_engine import WorkEngine
from ame.models.domain import Document, DocumentType
from ame.models.report_models import (
    WeeklyReport,
    DailyReport,
    OrganizedTodos,
    TaskInfo,
    ProjectProgress,
)


class TestWorkEngine:
    """工作引擎测试类"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock HybridRepository"""
        repo = Mock()
        repo.hybrid_search = AsyncMock(return_value=[])
        return repo
    
    @pytest.fixture
    def mock_llm_caller(self):
        """Mock LLMCaller"""
        llm = Mock()
        llm.generate = AsyncMock(return_value=Mock(content="测试响应"))
        return llm
    
    @pytest.fixture
    def mock_analyzer(self):
        """Mock AnalyzeEngine"""
        analyzer = Mock()
        analyzer.collect_time_range = AsyncMock(return_value=[])
        analyzer.extract_insights = AsyncMock(return_value={
            "key_tasks": [{"entity": "任务1", "count": 5}],
            "achievements": [{"content": "成就1", "timestamp": datetime.now().isoformat(), "importance": 0.8}],
            "challenges": ["挑战1"],
            "time_stats": {}
        })
        return analyzer
    
    @pytest.fixture
    def work_engine(self, mock_repository, mock_llm_caller, mock_analyzer):
        """创建 WorkEngine 实例"""
        return WorkEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            analyze_engine=mock_analyzer
        )
    
    @pytest.mark.asyncio
    async def test_generate_weekly_report_success(self, work_engine, mock_analyzer):
        """测试周报生成成功"""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        # 执行
        report = await work_engine.generate_weekly_report(
            user_id="test_user",
            start_date=start_date,
            end_date=end_date,
            style="professional"
        )
        
        # 验证
        assert isinstance(report, WeeklyReport)
        assert report.user_id == "test_user"
        assert report.period == (start_date, end_date)
        assert isinstance(report.content, str)
        assert len(report.key_tasks) > 0
        
        # 验证调用
        mock_analyzer.collect_time_range.assert_called_once()
        mock_analyzer.extract_insights.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_daily_report_success(self, work_engine, mock_analyzer):
        """测试日报生成成功"""
        date = datetime.now()
        
        # 执行
        report = await work_engine.generate_daily_report(
            user_id="test_user",
            date=date,
            style="professional"
        )
        
        # 验证
        assert isinstance(report, DailyReport)
        assert report.user_id == "test_user"
        assert report.date == date
        assert isinstance(report.content, str)
    
    @pytest.mark.asyncio
    async def test_organize_todos_success(self, work_engine):
        """测试待办整理成功"""
        raw_todos = [
            "紧急：完成项目报告",
            "本周完成代码审查",
            "明天开会",
            "学习新技术"
        ]
        
        # 执行
        organized = await work_engine.organize_todos(
            raw_todos=raw_todos,
            context={}
        )
        
        # 验证
        assert isinstance(organized, OrganizedTodos)
        assert organized.original_count == len(raw_todos)
        assert organized.organized_count > 0
        assert len(organized.high_priority) > 0  # "紧急"应该被识别
    
    @pytest.mark.asyncio
    async def test_organize_todos_priority_algorithm(self, work_engine):
        """测试待办优先级算法"""
        raw_todos = [
            "紧急：修复线上bug",  # 应该是高优先级
            "重要：优化性能",      # 应该是高优先级
            "本周完成文档",        # 应该是中优先级
            "有空看看新技术"       # 应该是低优先级
        ]
        
        # 执行
        organized = await work_engine.organize_todos(raw_todos)
        
        # 验证优先级分组
        assert len(organized.high_priority) >= 2  # 至少2个高优先级
        assert organized.high_priority[0].priority_score >= 70
    
    @pytest.mark.asyncio
    async def test_track_project_progress_success(self, work_engine, mock_repository):
        """测试项目进度追踪成功"""
        project_name = "测试项目"
        
        # Mock 检索结果
        mock_docs = [
            Mock(timestamp=datetime.now(), metadata={})
        ]
        mock_repository.hybrid_search = AsyncMock(return_value=mock_docs)
        
        # 执行
        progress = await work_engine.track_project_progress(
            project_name=project_name,
            user_id="test_user"
        )
        
        # 验证
        assert isinstance(progress, ProjectProgress)
        assert progress.project_name == project_name
        assert isinstance(progress.report, str)
    
    @pytest.mark.asyncio
    async def test_weekly_report_with_no_data(self, work_engine, mock_analyzer):
        """测试无数据时的周报生成"""
        # Mock 无数据
        mock_analyzer.collect_time_range = AsyncMock(return_value=[])
        mock_analyzer.extract_insights = AsyncMock(return_value={
            "key_tasks": [],
            "achievements": [],
            "challenges": []
        })
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        # 执行
        report = await work_engine.generate_weekly_report(
            user_id="test_user",
            start_date=start_date,
            end_date=end_date
        )
        
        # 验证：即使无数据也应返回有效报告
        assert isinstance(report, WeeklyReport)
        assert len(report.key_tasks) == 0
        assert len(report.achievements) == 0


class TestTaskPrioritization:
    """任务优先级测试类"""
    
    @pytest.fixture
    def work_engine(self):
        """创建简单的 WorkEngine"""
        return WorkEngine(
            repository=Mock(),
            llm_caller=Mock(),
        )
    
    @pytest.mark.asyncio
    async def test_urgent_keywords_detection(self, work_engine):
        """测试紧急关键词检测"""
        tasks = [
            TaskInfo(content="紧急处理客户投诉"),
            TaskInfo(content="今天必须完成"),
            TaskInfo(content="ASAP修复bug"),
            TaskInfo(content="普通任务"),
        ]
        
        # 执行
        prioritized = await work_engine._prioritize_tasks(tasks, None)
        
        # 验证：紧急任务应该排在前面
        assert prioritized[0].priority_score > prioritized[-1].priority_score
        assert prioritized[0].priority_score >= 40  # 紧急关键词至少40分
    
    @pytest.mark.asyncio
    async def test_importance_keywords_detection(self, work_engine):
        """测试重要性关键词检测"""
        tasks = [
            TaskInfo(content="重要项目评审"),
            TaskInfo(content="关键功能开发"),
            TaskInfo(content="普通任务"),
        ]
        
        # 执行
        prioritized = await work_engine._prioritize_tasks(tasks, None)
        
        # 验证
        assert prioritized[0].priority_score > prioritized[-1].priority_score
    
    @pytest.mark.asyncio
    async def test_combined_priority_scoring(self, work_engine):
        """测试组合优先级评分"""
        tasks = [
            TaskInfo(content="紧急且重要：项目上线"),  # 应该最高分
            TaskInfo(content="紧急：小问题修复"),      # 中高分
            TaskInfo(content="重要：长期规划"),        # 中分
            TaskInfo(content="普通任务"),              # 低分
        ]
        
        # 执行
        prioritized = await work_engine._prioritize_tasks(tasks, None)
        
        # 验证评分递减
        scores = [t.priority_score for t in prioritized]
        assert scores == sorted(scores, reverse=True)  # 降序排列
        assert prioritized[0].priority_score >= 70  # 紧急+重要应该高分


@pytest.mark.asyncio
async def test_work_engine_integration():
    """集成测试：完整工作流"""
    # 创建 Mock 对象
    repo = Mock()
    llm = Mock()
    analyzer = Mock()
    
    # 配置 Mock 行为
    analyzer.collect_time_range = AsyncMock(return_value=[
        Document(
            id="doc1",
            content="完成了重要功能开发",
            doc_type=DocumentType.WORK_LOG,
            source="work",
            timestamp=datetime.now(),
            entities=["功能开发"]
        )
    ])
    
    analyzer.extract_insights = AsyncMock(return_value={
        "key_tasks": [{"entity": "功能开发", "count": 1}],
        "achievements": [],
        "challenges": []
    })
    
    llm.generate = AsyncMock(return_value=Mock(content="# 工作周报\n\n完成了功能开发"))
    
    # 创建引擎
    engine = WorkEngine(repo, llm, analyze_engine=analyzer)
    
    # 执行完整流程
    report = await engine.generate_weekly_report(
        user_id="test_user",
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now()
    )
    
    # 验证结果
    assert report is not None
    assert isinstance(report, WeeklyReport)
    assert "功能开发" in report.content or len(report.key_tasks) > 0
