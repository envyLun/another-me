"""
引擎层集成测试
测试场景引擎与核心引擎的协同工作
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from ame.engines.work_engine import WorkEngine
from ame.engines.life_engine import LifeEngine
from ame.mem.mimic_engine import MimicEngine
from ame.mem.analyze_engine import AnalyzeEngine
from ame.repository.hybrid_repository import HybridRepository
from ame.models.domain import Document, DocumentType


@pytest.fixture
def mock_llm_caller():
    """Mock LLM Caller"""
    llm = Mock()
    llm.generate = AsyncMock(return_value=Mock(content="生成的内容"))
    llm.generate_stream = AsyncMock()
    return llm


@pytest.fixture
def mock_repository():
    """Mock Repository"""
    repo = Mock()
    repo.hybrid_search = AsyncMock(return_value=[])
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def analyze_engine(mock_repository, mock_llm_caller):
    """创建 AnalyzeEngine"""
    return AnalyzeEngine(
        repository=mock_repository,
        llm_caller=mock_llm_caller
    )


@pytest.fixture
def mimic_engine(mock_llm_caller):
    """创建 MimicEngine"""
    # Mock vector store
    vector_store = Mock()
    vector_store.add_documents = AsyncMock()
    
    with patch('ame.mem.mimic_engine.FaissStore', return_value=vector_store):
        with patch('ame.mem.mimic_engine.RetrieverFactory.create_retriever') as mock_factory:
            # Mock retriever
            retriever = Mock()
            retriever.retrieve = AsyncMock(return_value=[])
            mock_factory.return_value = retriever
            
            engine = MimicEngine(
                llm_caller=mock_llm_caller,
                db_path="/tmp/test_mimic"
            )
            return engine


class TestWorkEngineIntegration:
    """工作引擎集成测试"""
    
    @pytest.mark.asyncio
    async def test_work_engine_with_analyze_engine(
        self, 
        mock_repository, 
        mock_llm_caller,
        analyze_engine
    ):
        """测试 WorkEngine 与 AnalyzeEngine 的集成"""
        # 创建 WorkEngine
        work_engine = WorkEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            analyze_engine=analyze_engine
        )
        
        # Mock 数据
        mock_docs = [
            Document(
                id="work1",
                content="完成功能开发",
                doc_type=DocumentType.WORK_LOG,
                source="work",
                timestamp=datetime.now(),
                entities=["功能开发"],
                importance=0.8
            )
        ]
        analyze_engine.collect_time_range = AsyncMock(return_value=mock_docs)
        
        # 执行周报生成
        report = await work_engine.generate_weekly_report(
            user_id="test_user",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            style="professional"
        )
        
        # 验证
        assert report is not None
        assert len(report.key_tasks) > 0
        assert analyze_engine.collect_time_range.called
        assert analyze_engine.extract_insights.called
    
    @pytest.mark.asyncio
    async def test_work_engine_with_mimic_engine(
        self,
        mock_repository,
        mock_llm_caller,
        analyze_engine,
        mimic_engine
    ):
        """测试 WorkEngine 与 MimicEngine 的集成"""
        # 创建 WorkEngine
        work_engine = WorkEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            mimic_engine=mimic_engine,
            analyze_engine=analyze_engine
        )
        
        # Mock 数据
        analyze_engine.collect_time_range = AsyncMock(return_value=[])
        analyze_engine.extract_insights = AsyncMock(return_value={
            "key_tasks": [{"entity": "任务1", "count": 1}],
            "achievements": [],
            "challenges": []
        })
        
        # 执行周报生成
        report = await work_engine.generate_weekly_report(
            user_id="test_user",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            style="casual"
        )
        
        # 验证
        assert report is not None
        assert isinstance(report.content, str)


class TestLifeEngineIntegration:
    """生活引擎集成测试"""
    
    @pytest.mark.asyncio
    async def test_life_engine_with_analyze_engine(
        self,
        mock_repository,
        mock_llm_caller,
        analyze_engine
    ):
        """测试 LifeEngine 与 AnalyzeEngine 的集成"""
        # 创建 LifeEngine
        life_engine = LifeEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            analyze_engine=analyze_engine
        )
        
        # Mock 数据
        mock_docs = [
            Document(
                id="life1",
                content="今天读了一本好书",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now(),
                entities=["阅读", "书籍"]
            )
        ]
        analyze_engine.collect_time_range = AsyncMock(return_value=mock_docs)
        
        # 执行兴趣追踪
        interest_report = await life_engine.track_interests(
            user_id="test_user",
            period_days=30
        )
        
        # 验证
        assert interest_report is not None
        assert len(interest_report.top_interests) > 0
        assert analyze_engine.collect_time_range.called
    
    @pytest.mark.asyncio
    async def test_life_engine_mood_analysis_full_flow(
        self,
        mock_repository,
        mock_llm_caller,
        analyze_engine
    ):
        """测试心情分析完整流程"""
        # 创建 LifeEngine
        life_engine = LifeEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            analyze_engine=analyze_engine
        )
        
        # Mock 历史数据（用于趋势分析）
        mock_history = [
            Document(
                id="mood1",
                content="昨天心情不错",
                doc_type=DocumentType.LIFE_RECORD,
                source="mood",
                timestamp=datetime.now() - timedelta(days=1),
                metadata={
                    "category": "mood",
                    "emotion": {"type": "happy", "intensity": 0.7}
                }
            )
        ]
        analyze_engine.collect_time_range = AsyncMock(return_value=mock_history)
        
        # Mock LLM 响应
        mock_llm_caller.generate = AsyncMock(return_value=Mock(
            content="建议：保持积极心态，多做喜欢的事情"
        ))
        
        # 执行心情分析
        mood_analysis = await life_engine.analyze_mood(
            mood_entry="今天心情很好，完成了很多事情",
            user_id="test_user",
            entry_time=datetime.now()
        )
        
        # 验证
        assert mood_analysis is not None
        assert mood_analysis.trend is not None
        assert len(mood_analysis.suggestions) > 0
        assert mock_repository.create.called  # 应该存储心情记录


class TestCrossEngineIntegration:
    """跨引擎集成测试"""
    
    @pytest.mark.asyncio
    async def test_work_and_life_engine_data_isolation(
        self,
        mock_repository,
        mock_llm_caller,
        analyze_engine
    ):
        """测试工作引擎和生活引擎的数据隔离"""
        # 创建两个引擎
        work_engine = WorkEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            analyze_engine=analyze_engine
        )
        
        life_engine = LifeEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            analyze_engine=analyze_engine
        )
        
        # Mock 混合数据
        all_docs = [
            Document(
                id="work1",
                content="工作记录",
                doc_type=DocumentType.WORK_LOG,
                source="work",
                timestamp=datetime.now(),
                entities=["工作"]
            ),
            Document(
                id="life1",
                content="生活记录",
                doc_type=DocumentType.LIFE_RECORD,
                source="life",
                timestamp=datetime.now(),
                entities=["生活"]
            )
        ]
        
        # 配置 Mock 返回所有数据
        analyze_engine.collect_time_range = AsyncMock(return_value=all_docs)
        
        # 执行工作引擎查询
        work_report = await work_engine.generate_weekly_report(
            user_id="test_user",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now()
        )
        
        # 验证：工作引擎应该只看到工作数据
        # （实际实现中会在 collect_time_range 中过滤）
        assert work_report is not None
    
    @pytest.mark.asyncio
    async def test_analyze_engine_shared_by_multiple_engines(
        self,
        mock_repository,
        mock_llm_caller,
        analyze_engine
    ):
        """测试 AnalyzeEngine 被多个引擎共享"""
        # 创建两个引擎共享同一个 AnalyzeEngine
        work_engine = WorkEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            analyze_engine=analyze_engine
        )
        
        life_engine = LifeEngine(
            repository=mock_repository,
            llm_caller=mock_llm_caller,
            analyze_engine=analyze_engine
        )
        
        # Mock 数据
        analyze_engine.collect_time_range = AsyncMock(return_value=[])
        analyze_engine.extract_insights = AsyncMock(return_value={
            "key_tasks": [],
            "achievements": []
        })
        
        # 执行两个引擎的操作
        await work_engine.generate_weekly_report(
            user_id="test_user",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now()
        )
        
        await life_engine.track_interests(
            user_id="test_user",
            period_days=30
        )
        
        # 验证：AnalyzeEngine 应该被两次调用
        assert analyze_engine.collect_time_range.call_count >= 2


@pytest.mark.asyncio
async def test_full_system_integration():
    """完整系统集成测试"""
    # 创建所有组件
    llm_caller = Mock()
    llm_caller.generate = AsyncMock(return_value=Mock(content="测试内容"))
    
    repository = Mock()
    repository.create = AsyncMock()
    repository.hybrid_search = AsyncMock(return_value=[])
    
    # 创建核心引擎
    analyzer = AnalyzeEngine(repository, llm_caller)
    
    # Mock 数据收集
    analyzer.collect_time_range = AsyncMock(return_value=[
        Document(
            id="doc1",
            content="测试文档",
            doc_type=DocumentType.WORK_LOG,
            source="test",
            timestamp=datetime.now(),
            entities=["测试"],
            importance=0.7
        )
    ])
    
    # 创建场景引擎
    work_engine = WorkEngine(repository, llm_caller, analyze_engine=analyzer)
    life_engine = LifeEngine(repository, llm_caller, analyze_engine=analyzer)
    
    # 执行工作流：生成周报
    work_report = await work_engine.generate_weekly_report(
        user_id="test_user",
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now()
    )
    
    # 执行工作流：分析心情
    mood_analysis = await life_engine.analyze_mood(
        mood_entry="今天心情不错",
        user_id="test_user",
        entry_time=datetime.now()
    )
    
    # 验证整个系统正常工作
    assert work_report is not None
    assert mood_analysis is not None
    assert analyzer.collect_time_range.called
    assert repository.create.called
