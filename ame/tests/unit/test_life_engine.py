"""
生活引擎单元测试
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from ame.engines.life_engine import LifeEngine
from ame.models.domain import Document, DocumentType
from ame.models.report_models import (
    MoodAnalysis,
    MoodTrend,
    InterestReport,
    InterestTopic,
)


class TestLifeEngine:
    """生活引擎测试类"""
    
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
        llm.generate = AsyncMock(return_value=Mock(content="温暖的建议"))
        return llm
    
    @pytest.fixture
    def mock_analyzer(self):
        """Mock AnalyzeEngine"""
        analyzer = Mock()
        analyzer.collect_time_range = AsyncMock(return_value=[])
        analyzer.extract_insights = AsyncMock(return_value={
            "key_tasks": [{"entity": "阅读", "count": 10}],
            "achievements": []
        })
        return analyzer
    
    @pytest.fixture
    def life_engine(self, mock_repository, mock_llm_caller, mock_analyzer):
        """创建 LifeEngine 实例"""
        return LifeEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            analyze_engine=mock_analyzer
        )
    
    @pytest.mark.asyncio
    async def test_analyze_mood_success(self, life_engine):
        """测试心情分析成功"""
        mood_entry = "今天心情很好，完成了很多事情"
        entry_time = datetime.now()
        
        # 执行
        mood_analysis = await life_engine.analyze_mood(
            mood_entry=mood_entry,
            user_id="test_user",
            entry_time=entry_time
        )
        
        # 验证
        assert isinstance(mood_analysis, MoodAnalysis)
        assert isinstance(mood_analysis.emotion_type, str)
        assert 0.0 <= mood_analysis.emotion_intensity <= 1.0
        assert isinstance(mood_analysis.suggestions, str)
    
    @pytest.mark.asyncio
    async def test_analyze_mood_with_trend(self, life_engine, mock_analyzer):
        """测试心情分析包含趋势"""
        # Mock 历史数据
        mock_docs = [
            Document(
                id="mood1",
                content="昨天心情不错",
                doc_type=DocumentType.LIFE_RECORD,
                source="mood",
                timestamp=datetime.now() - timedelta(days=1),
                metadata={"category": "mood", "emotion": {"type": "happy", "intensity": 0.7}}
            )
        ]
        mock_analyzer.collect_time_range = AsyncMock(return_value=mock_docs)
        
        # 执行
        mood_analysis = await life_engine.analyze_mood(
            mood_entry="今天也很开心",
            user_id="test_user",
            entry_time=datetime.now()
        )
        
        # 验证
        assert mood_analysis.trend is not None
        assert isinstance(mood_analysis.trend, MoodTrend)
        assert mood_analysis.trend.trend_direction in ["improving", "declining", "stable"]
    
    @pytest.mark.asyncio
    async def test_track_interests_success(self, life_engine, mock_analyzer):
        """测试兴趣追踪成功"""
        # Mock 生活记录数据
        mock_docs = [
            Document(
                id="life1",
                content="今天读了一本好书",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now(),
                entities=["阅读", "书籍"]
            ),
            Document(
                id="life2",
                content="去健身房锻炼",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now() - timedelta(days=1),
                entities=["健身", "运动"]
            )
        ]
        mock_analyzer.collect_time_range = AsyncMock(return_value=mock_docs)
        
        # 执行
        interest_report = await life_engine.track_interests(
            user_id="test_user",
            period_days=30
        )
        
        # 验证
        assert isinstance(interest_report, InterestReport)
        assert interest_report.period_days == 30
        assert len(interest_report.top_interests) > 0
        assert isinstance(interest_report.report, str)
    
    @pytest.mark.asyncio
    async def test_track_interests_with_evolution(self, life_engine, mock_analyzer):
        """测试兴趣演化分析"""
        # Mock 当前周期数据
        current_docs = [
            Document(
                id="c1",
                content="学习编程",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now(),
                entities=["编程", "技术"]
            )
        ]
        
        # Mock 上一周期数据
        previous_docs = [
            Document(
                id="p1",
                content="玩游戏",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now() - timedelta(days=40),
                entities=["游戏", "娱乐"]
            )
        ]
        
        # 配置 Mock 按时间返回不同数据
        def collect_by_time(*args, **kwargs):
            start = kwargs.get('start_date') or args[1]
            if start > datetime.now() - timedelta(days=35):
                return current_docs
            else:
                return previous_docs
        
        mock_analyzer.collect_time_range = AsyncMock(side_effect=collect_by_time)
        
        # 执行
        interest_report = await life_engine.track_interests(
            user_id="test_user",
            period_days=30
        )
        
        # 验证：应该识别出新兴趣和衰减兴趣
        assert isinstance(interest_report.new_interests, list)
        assert isinstance(interest_report.declining_interests, list)
    
    @pytest.mark.asyncio
    async def test_generate_life_suggestions_success(self, life_engine, mock_analyzer):
        """测试生活建议生成成功"""
        # Mock 生活记录
        mock_docs = [
            Document(
                id="life1",
                content="最近压力很大",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now(),
                entities=["压力", "工作"]
            )
        ]
        mock_analyzer.collect_time_range = AsyncMock(return_value=mock_docs)
        
        # 执行
        suggestions = await life_engine.generate_life_suggestions(
            user_id="test_user",
            context="最近工作压力大，想要改善"
        )
        
        # 验证
        assert isinstance(suggestions, str)
        assert len(suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_recall_memories_success(self, life_engine, mock_repository):
        """测试记忆回忆成功"""
        # Mock 检索结果
        mock_results = [
            Mock(timestamp=datetime.now(), metadata={})
        ]
        mock_repository.hybrid_search = AsyncMock(return_value=mock_results)
        
        # 执行
        memories = await life_engine.recall_memories(
            user_id="test_user",
            query="去年的旅行",
            time_range=timedelta(days=365)
        )
        
        # 验证
        assert isinstance(memories, list)
        mock_repository.hybrid_search.assert_called_once()


class TestMoodAnalysis:
    """心情分析测试类"""
    
    @pytest.fixture
    def life_engine(self):
        """创建简单的 LifeEngine"""
        return LifeEngine(
            repository=Mock(),
            llm_caller=Mock(),
        )
    
    @pytest.mark.asyncio
    async def test_emotion_detection(self, life_engine):
        """测试情绪检测"""
        text = "今天很开心，完成了重要项目"
        
        # 执行
        emotion = await life_engine._detect_emotion(text, {})
        
        # 验证
        assert "type" in emotion
        assert "intensity" in emotion
        assert "confidence" in emotion
        assert 0.0 <= emotion["intensity"] <= 1.0
        assert 0.0 <= emotion["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_trigger_extraction(self, life_engine):
        """测试触发因素提取"""
        mood_entry = "因为项目成功上线，心情特别好"
        
        # 执行
        triggers = await life_engine._extract_triggers(mood_entry)
        
        # 验证
        assert isinstance(triggers, list)
    
    @pytest.mark.asyncio
    async def test_mood_trend_analysis(self, life_engine, mock_analyzer=None):
        """测试情绪趋势分析"""
        # Mock analyzer
        if not mock_analyzer:
            mock_analyzer = Mock()
            mock_docs = [
                Document(
                    id=f"mood{i}",
                    content=f"心情记录{i}",
                    doc_type=DocumentType.LIFE_RECORD,
                    source="mood",
                    timestamp=datetime.now() - timedelta(days=i),
                    metadata={"category": "mood", "emotion": {"type": "happy", "intensity": 0.7 - i*0.05}}
                )
                for i in range(5)
            ]
            mock_analyzer.collect_time_range = AsyncMock(return_value=mock_docs)
            life_engine.analyzer = mock_analyzer
        
        current_emotion = {"type": "neutral", "intensity": 0.5}
        
        # 执行
        trend = await life_engine._analyze_mood_trend(
            user_id="test_user",
            current_emotion=current_emotion,
            days=7
        )
        
        # 验证
        assert isinstance(trend, MoodTrend)
        assert trend.trend_direction in ["improving", "declining", "stable"]
        assert isinstance(trend.alert, bool)


class TestInterestTracking:
    """兴趣追踪测试类"""
    
    @pytest.mark.asyncio
    async def test_interest_evolution(self):
        """测试兴趣演化分析"""
        # 创建引擎
        repo = Mock()
        llm = Mock()
        analyzer = Mock()
        
        # Mock 当前周期：喜欢编程和阅读
        current_docs = [
            Document(
                id="c1",
                content="学习Python",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now(),
                entities=["编程", "Python"]
            ),
            Document(
                id="c2",
                content="读技术书",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now(),
                entities=["阅读", "技术"]
            )
        ]
        
        # Mock 上一周期：喜欢游戏和阅读
        previous_docs = [
            Document(
                id="p1",
                content="玩游戏",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now() - timedelta(days=40),
                entities=["游戏"]
            ),
            Document(
                id="p2",
                content="读小说",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now() - timedelta(days=40),
                entities=["阅读", "小说"]
            )
        ]
        
        def mock_collect(*args, **kwargs):
            start = kwargs.get('start_date') or args[1]
            if start > datetime.now() - timedelta(days=35):
                return current_docs
            else:
                return previous_docs
        
        analyzer.collect_time_range = AsyncMock(side_effect=mock_collect)
        
        engine = LifeEngine(repo, llm, analyze_engine=analyzer)
        
        # 执行
        new_interests, declining_interests = await engine._analyze_interest_evolution(
            user_id="test_user",
            current_period_days=30
        )
        
        # 验证
        assert "编程" in new_interests or "Python" in new_interests  # 新兴趣
        assert "游戏" in declining_interests  # 衰减兴趣


@pytest.mark.asyncio
async def test_life_engine_integration():
    """集成测试：完整生活分析流程"""
    # 创建 Mock 对象
    repo = Mock()
    llm = Mock()
    analyzer = Mock()
    
    # 配置 Mock 行为
    analyzer.collect_time_range = AsyncMock(return_value=[
        Document(
            id="life1",
            content="今天心情不错，去跑步了",
            doc_type=DocumentType.LIFE_RECORD,
            source="life",
            timestamp=datetime.now(),
            entities=["运动", "跑步"],
            metadata={"category": "mood", "emotion": {"type": "happy", "intensity": 0.8}}
        )
    ])
    
    llm.generate = AsyncMock(return_value=Mock(content="建议：继续保持运动习惯"))
    
    # 创建引擎
    engine = LifeEngine(repo, llm, analyze_engine=analyzer)
    
    # 执行完整流程：心情分析
    mood_analysis = await engine.analyze_mood(
        mood_entry="今天去跑步了，感觉很好",
        user_id="test_user",
        entry_time=datetime.now()
    )
    
    # 验证结果
    assert mood_analysis is not None
    assert isinstance(mood_analysis, MoodAnalysis)
    assert len(mood_analysis.suggestions) > 0
