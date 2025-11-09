"""
检索管道单元测试
"""

import pytest
from unittest.mock import Mock, AsyncMock

from ame.retrieval.pipeline import RetrievalPipeline
from ame.retrieval.stages.base import StageBase
from ame.retrieval.base import RetrievalResult


class MockStage(StageBase):
    """模拟检索阶段"""
    
    def __init__(self, name: str, output_count: int = 5):
        self.stage_name = name
        self.output_count = output_count
    
    async def process(self, query, previous_results, context):
        """返回模拟结果"""
        results = []
        for i in range(self.output_count):
            results.append(RetrievalResult(
                content=f"{self.stage_name} result {i}",
                metadata={"stage": self.stage_name, "doc_id": f"doc_{i}"},
                score=1.0 - i * 0.1,
                source=self.stage_name
            ))
        return results
    
    def get_name(self):
        return self.stage_name


@pytest.mark.asyncio
class TestRetrievalPipeline:
    """Pipeline 测试套件"""
    
    async def test_empty_pipeline(self):
        """测试空管道"""
        pipeline = RetrievalPipeline("test")
        results = await pipeline.execute("test query")
        
        assert results == []
    
    async def test_single_stage(self):
        """测试单阶段管道"""
        pipeline = RetrievalPipeline("test")
        pipeline.add_stage(MockStage("Stage1", output_count=3))
        
        results = await pipeline.execute("test query", top_k=5)
        
        assert len(results) == 3
        assert all(r.metadata["stage"] == "Stage1" for r in results)
    
    async def test_multiple_stages(self):
        """测试多阶段管道"""
        pipeline = RetrievalPipeline("test")
        pipeline\
            .add_stage(MockStage("Stage1", output_count=5))\
            .add_stage(MockStage("Stage2", output_count=3))
        
        results = await pipeline.execute("test query", top_k=3)
        
        # 最终应该返回 Stage2 的结果
        assert len(results) == 3
        assert all(r.metadata["stage"] == "Stage2" for r in results)
    
    async def test_empty_query(self):
        """测试空查询"""
        pipeline = RetrievalPipeline("test")
        pipeline.add_stage(MockStage("Stage1"))
        
        results = await pipeline.execute("")
        
        assert results == []
    
    async def test_context_passing(self):
        """测试上下文传递"""
        class ContextCheckStage(StageBase):
            async def process(self, query, previous_results, context):
                assert "query" in context
                assert "top_k" in context
                assert context["custom_key"] == "custom_value"
                return []
            
            def get_name(self):
                return "ContextCheck"
        
        pipeline = RetrievalPipeline("test")
        pipeline.add_stage(ContextCheckStage())
        
        await pipeline.execute(
            "test",
            context={"custom_key": "custom_value"}
        )
    
    async def test_stage_chain(self):
        """测试阶段链式调用"""
        pipeline = RetrievalPipeline("test")
        
        result = pipeline\
            .add_stage(MockStage("S1"))\
            .add_stage(MockStage("S2"))\
            .add_stage(MockStage("S3"))
        
        assert result == pipeline
        assert len(pipeline.stages) == 3
    
    async def test_get_stage_names(self):
        """测试获取阶段名称"""
        pipeline = RetrievalPipeline("test")
        pipeline\
            .add_stage(MockStage("Vector"))\
            .add_stage(MockStage("Graph"))\
            .add_stage(MockStage("Fusion"))
        
        names = pipeline.get_stage_names()
        
        assert names == ["Vector", "Graph", "Fusion"]
    
    async def test_top_k_limit(self):
        """测试 top_k 限制"""
        pipeline = RetrievalPipeline("test")
        pipeline.add_stage(MockStage("Stage1", output_count=10))
        
        results = await pipeline.execute("test", top_k=3)
        
        assert len(results) == 3


@pytest.mark.asyncio
class TestStageIntegration:
    """阶段集成测试"""
    
    async def test_score_modification(self):
        """测试分数修改"""
        class ScoreBoostStage(StageBase):
            async def process(self, query, previous_results, context):
                if previous_results:
                    for r in previous_results:
                        r.score *= 2
                    return previous_results
                return []
            
            def get_name(self):
                return "ScoreBoost"
        
        pipeline = RetrievalPipeline("test")
        pipeline\
            .add_stage(MockStage("Initial", output_count=3))\
            .add_stage(ScoreBoostStage())
        
        results = await pipeline.execute("test")
        
        # 初始最高分 1.0，boost 后应该是 2.0
        assert results[0].score == 2.0
    
    async def test_result_filtering(self):
        """测试结果过滤"""
        class FilterStage(StageBase):
            async def process(self, query, previous_results, context):
                if previous_results:
                    # 只保留分数 > 0.5 的结果
                    return [r for r in previous_results if r.score > 0.5]
                return []
            
            def get_name(self):
                return "Filter"
        
        pipeline = RetrievalPipeline("test")
        pipeline\
            .add_stage(MockStage("Initial", output_count=10))\
            .add_stage(FilterStage())
        
        results = await pipeline.execute("test")
        
        # 验证所有结果分数 > 0.5
        assert all(r.score > 0.5 for r in results)
        assert len(results) < 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
