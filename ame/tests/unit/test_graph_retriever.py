"""
GraphRetriever 单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict

from ame.retrieval.graph_retriever import GraphRetriever
from ame.retrieval.base import RetrievalResult
from ame.storage.falkor_store import FalkorStore
from ame.foundation.nlp.ner import Entity, NERBase


class MockNER(NERBase):
    """Mock NER for testing"""
    
    async def extract(self, text: str) -> List[Entity]:
        """返回预定义的实体"""
        if "机器学习" in text:
            return [
                Entity(text="机器学习", type="TOPIC", score=0.9),
                Entity(text="深度学习", type="TOPIC", score=0.85)
            ]
        return []


class MockFalkorStore:
    """Mock FalkorStore for testing"""
    
    async def search_by_entities(
        self, 
        query: str,
        entities: List[str],
        top_k: int
    ) -> List[Dict]:
        """Mock search results"""
        return [
            {
                "doc_id": "doc1",
                "score": 0.95,
                "source": "graph",
                "matched_entities": ["机器学习"],
                "timestamp": "2024-01-01T00:00:00"
            },
            {
                "doc_id": "doc2",
                "score": 0.80,
                "source": "graph",
                "matched_entities": ["深度学习"],
                "timestamp": "2024-01-02T00:00:00"
            }
        ]
    
    async def find_related_docs(
        self, 
        doc_id: str, 
        max_hops: int,
        limit: int
    ) -> List[Dict]:
        """Mock related docs"""
        if doc_id == "doc1":
            return [
                {
                    "doc_id": "doc3",
                    "distance": 1,
                    "score": 0.7,
                    "shared_entities": ["机器学习", "Python"]
                }
            ]
        return []


@pytest.fixture
def mock_falkor():
    """Fixture for MockFalkorStore"""
    return MockFalkorStore()


@pytest.fixture
def mock_ner():
    """Fixture for MockNER"""
    return MockNER()


@pytest.fixture
def graph_retriever(mock_falkor, mock_ner):
    """Fixture for GraphRetriever"""
    return GraphRetriever(
        falkor_store=mock_falkor,
        ner_service=mock_ner,
        enable_multi_hop=True,
        max_hops=2
    )


class TestGraphRetriever:
    """GraphRetriever 测试类"""
    
    @pytest.mark.asyncio
    async def test_retrieve_basic(self, graph_retriever):
        """测试基本检索"""
        results = await graph_retriever.retrieve(
            query="机器学习的应用",
            top_k=5
        )
        
        assert len(results) > 0
        assert all(isinstance(r, RetrievalResult) for r in results)
        assert results[0].score > 0
        assert "doc_id" in results[0].metadata
    
    @pytest.mark.asyncio
    async def test_retrieve_with_multi_hop(self, graph_retriever):
        """测试多跳推理检索"""
        results = await graph_retriever.retrieve(
            query="机器学习",
            top_k=10,
            enable_multi_hop=True,
            max_hops=2
        )
        
        # 应该包含初始结果 + 扩展结果
        assert len(results) > 2
        
        # 检查是否有扩展的文档
        sources = [r.source for r in results]
        assert "graph" in sources or "graph_expanded" in sources
    
    @pytest.mark.asyncio
    async def test_retrieve_without_multi_hop(self, graph_retriever):
        """测试不启用多跳推理"""
        results = await graph_retriever.retrieve(
            query="机器学习",
            top_k=5,
            enable_multi_hop=False
        )
        
        # 所有结果应该是直接检索的
        for result in results:
            assert result.source in ["graph"]
    
    @pytest.mark.asyncio
    async def test_retrieve_empty_query(self, graph_retriever):
        """测试空查询"""
        results = await graph_retriever.retrieve(
            query="",
            top_k=5
        )
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_retrieve_no_entities(self, mock_falkor):
        """测试查询中没有实体"""
        # 使用一个返回空实体的NER
        class EmptyNER(NERBase):
            async def extract(self, text: str) -> List[Entity]:
                return []
        
        retriever = GraphRetriever(
            falkor_store=mock_falkor,
            ner_service=EmptyNER()
        )
        
        results = await retriever.retrieve(
            query="这是一个测试",
            top_k=5
        )
        
        # 没有实体应该返回空结果
        assert results == []
    
    @pytest.mark.asyncio
    async def test_extract_entities(self, graph_retriever):
        """测试实体提取"""
        entities = await graph_retriever._extract_entities("机器学习和深度学习")
        
        assert len(entities) > 0
        assert "机器学习" in entities or "深度学习" in entities
    
    @pytest.mark.asyncio
    async def test_expand_with_multi_hop(self, graph_retriever):
        """测试多跳推理扩展"""
        initial_results = [
            {
                "doc_id": "doc1",
                "score": 0.95,
                "source": "graph"
            }
        ]
        
        expanded = await graph_retriever._expand_with_multi_hop(
            initial_results,
            max_hops=2
        )
        
        # 扩展后应该有更多结果
        assert len(expanded) >= len(initial_results)
        
        # 检查新增的文档
        expanded_ids = [r["doc_id"] for r in expanded]
        assert "doc1" in expanded_ids
    
    def test_convert_to_results(self, graph_retriever):
        """测试结果转换"""
        graph_results = [
            {
                "doc_id": "doc1",
                "score": 0.95,
                "source": "graph",
                "matched_entities": ["机器学习"]
            },
            {
                "doc_id": "doc2",
                "score": 0.80,
                "source": "graph_expanded",
                "hop_distance": 2
            }
        ]
        
        results = graph_retriever._convert_to_results(graph_results)
        
        assert len(results) == 2
        assert all(isinstance(r, RetrievalResult) for r in results)
        assert results[0].metadata["doc_id"] == "doc1"
        assert results[0].metadata["matched_entities"] == ["机器学习"]
        assert results[1].metadata["hop_distance"] == 2
    
    @pytest.mark.asyncio
    async def test_fallback_extract(self, graph_retriever):
        """测试备用实体提取"""
        # 测试jieba分词fallback
        words = graph_retriever._fallback_extract("机器学习是一门技术")
        
        assert len(words) > 0
        assert all(isinstance(w, str) for w in words)
        assert all(len(w) > 1 for w in words)  # 应该过滤掉单字
    
    @pytest.mark.asyncio
    async def test_retrieve_top_k_limit(self, graph_retriever):
        """测试top_k限制"""
        results = await graph_retriever.retrieve(
            query="机器学习",
            top_k=1
        )
        
        # 结果数量不应超过top_k
        assert len(results) <= 1
    
    @pytest.mark.asyncio
    async def test_score_ordering(self, graph_retriever):
        """测试结果按分数排序"""
        results = await graph_retriever.retrieve(
            query="机器学习和深度学习",
            top_k=10
        )
        
        # 检查分数是降序排列
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_distance_decay(self, graph_retriever):
        """测试距离衰减算法"""
        initial_results = [
            {"doc_id": "doc1", "score": 1.0, "source": "graph"}
        ]
        
        expanded = await graph_retriever._expand_with_multi_hop(
            initial_results,
            max_hops=2
        )
        
        # 检查扩展文档的分数是否有衰减
        for result in expanded:
            if result.get("hop_distance"):
                # 扩展文档的分数应该小于初始文档
                assert result["score"] < 1.0


@pytest.mark.asyncio
async def test_integration_with_real_ner():
    """集成测试：使用真实NER（如果可用）"""
    try:
        from ame.ner import SimpleNER
        
        ner = SimpleNER()
        mock_falkor = MockFalkorStore()
        
        retriever = GraphRetriever(
            falkor_store=mock_falkor,
            ner_service=ner
        )
        
        results = await retriever.retrieve(
            query="张三在北京学习机器学习",
            top_k=5
        )
        
        assert isinstance(results, list)
    
    except ImportError:
        pytest.skip("SimpleNER not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
