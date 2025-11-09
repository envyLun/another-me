"""
NER 服务单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ame.foundation.nlp.ner import Entity, NERBase, SimpleNER, LLMNER, HybridNER


class TestEntity:
    """Entity 数据结构测试"""
    
    def test_entity_creation(self):
        """测试Entity创建"""
        entity = Entity(
            text="张三",
            type="PERSON",
            score=0.95
        )
        
        assert entity.text == "张三"
        assert entity.type == "PERSON"
        assert entity.score == 0.95
        assert entity.metadata is None
    
    def test_entity_with_metadata(self):
        """测试带元数据的Entity"""
        entity = Entity(
            text="北京",
            type="LOCATION",
            score=0.90,
            metadata={"source": "ner", "confidence": "high"}
        )
        
        assert entity.metadata["source"] == "ner"
        assert entity.metadata["confidence"] == "high"
    
    def test_entity_equality(self):
        """测试Entity相等性判断"""
        entity1 = Entity(text="张三", type="PERSON", score=0.9)
        entity2 = Entity(text="张三", type="PERSON", score=0.8)
        entity3 = Entity(text="李四", type="PERSON", score=0.9)
        
        assert entity1 == entity2  # 相同text视为相等
        assert entity1 != entity3
    
    def test_entity_hash(self):
        """测试Entity哈希"""
        entity1 = Entity(text="张三", type="PERSON", score=0.9)
        entity2 = Entity(text="张三", type="PERSON", score=0.8)
        
        # 相同text应该有相同哈希
        assert hash(entity1) == hash(entity2)


class TestNERBase:
    """NERBase 基类测试"""
    
    def test_filter_entities_by_score(self):
        """测试按分数过滤"""
        class DummyNER(NERBase):
            async def extract(self, text):
                return []
        
        ner = DummyNER()
        entities = [
            Entity(text="高分实体", type="TOPIC", score=0.9),
            Entity(text="低分实体", type="TOPIC", score=0.4)
        ]
        
        filtered = ner.filter_entities(entities, min_score=0.5)
        
        assert len(filtered) == 1
        assert filtered[0].text == "高分实体"
    
    def test_filter_entities_by_length(self):
        """测试按长度过滤"""
        class DummyNER(NERBase):
            async def extract(self, text):
                return []
        
        ner = DummyNER()
        entities = [
            Entity(text="长实体名", type="TOPIC", score=0.9),
            Entity(text="短", type="TOPIC", score=0.9)
        ]
        
        filtered = ner.filter_entities(entities, min_length=2)
        
        assert len(filtered) == 1
        assert filtered[0].text == "长实体名"
    
    def test_filter_entities_by_type(self):
        """测试按类型过滤"""
        class DummyNER(NERBase):
            async def extract(self, text):
                return []
        
        ner = DummyNER()
        entities = [
            Entity(text="张三", type="PERSON", score=0.9),
            Entity(text="北京", type="LOCATION", score=0.9),
            Entity(text="主题", type="TOPIC", score=0.9)
        ]
        
        filtered = ner.filter_entities(entities, entity_types=["PERSON", "LOCATION"])
        
        assert len(filtered) == 2
        assert all(e.type in ["PERSON", "LOCATION"] for e in filtered)
    
    def test_deduplicate_entities(self):
        """测试去重"""
        class DummyNER(NERBase):
            async def extract(self, text):
                return []
        
        ner = DummyNER()
        entities = [
            Entity(text="张三", type="PERSON", score=0.9),
            Entity(text="张三", type="PERSON", score=0.95),  # 高分
            Entity(text="李四", type="PERSON", score=0.8)
        ]
        
        deduped = ner.deduplicate_entities(entities)
        
        assert len(deduped) == 2
        # 应该保留高分的"张三"
        zhang_san = [e for e in deduped if e.text == "张三"][0]
        assert zhang_san.score == 0.95


class TestSimpleNER:
    """SimpleNER 测试"""
    
    @pytest.mark.asyncio
    async def test_simple_ner_extract(self):
        """测试SimpleNER提取"""
        try:
            ner = SimpleNER(enable_paddle=False)
            
            entities = await ner.extract("张三在北京的清华大学学习")
            
            assert len(entities) > 0
            assert all(isinstance(e, Entity) for e in entities)
            
            # 检查是否提取到关键实体
            texts = [e.text for e in entities]
            assert any("张三" in t or "北京" in t or "清华" in t for t in texts)
        
        except ImportError:
            pytest.skip("jieba not installed")
    
    @pytest.mark.asyncio
    async def test_simple_ner_empty_text(self):
        """测试空文本"""
        try:
            ner = SimpleNER()
            
            entities = await ner.extract("")
            assert entities == []
            
            entities = await ner.extract("   ")
            assert entities == []
        
        except ImportError:
            pytest.skip("jieba not installed")
    
    @pytest.mark.asyncio
    async def test_simple_ner_stopwords(self):
        """测试停用词过滤"""
        try:
            ner = SimpleNER()
            
            entities = await ner.extract("的了在是我")
            
            # 停用词应该被过滤
            texts = [e.text for e in entities]
            assert not any(w in texts for w in ["的", "了", "在", "是", "我"])
        
        except ImportError:
            pytest.skip("jieba not installed")
    
    def test_map_entity_type(self):
        """测试词性到实体类型映射"""
        try:
            ner = SimpleNER()
            
            assert ner._map_entity_type("nr") == "PERSON"
            assert ner._map_entity_type("ns") == "LOCATION"
            assert ner._map_entity_type("nt") == "ORGANIZATION"
            assert ner._map_entity_type("n") == "TOPIC"
        
        except ImportError:
            pytest.skip("jieba not installed")


class TestLLMBasedNER:
    """LLMBasedNER 测试"""
    
    @pytest.mark.asyncio
    async def test_llm_ner_extract(self):
        """测试LLM NER提取"""
        # Mock LLM caller
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value={
            "content": '[{"text": "张三", "type": "PERSON", "score": 0.95}]'
        })
        
        ner = LLMBasedNER(llm_caller=mock_llm)
        
        entities = await ner.extract("张三在北京学习")
        
        assert len(entities) == 1
        assert entities[0].text == "张三"
        assert entities[0].type == "PERSON"
        assert entities[0].score == 0.95
    
    @pytest.mark.asyncio
    async def test_llm_ner_empty_text(self):
        """测试空文本"""
        mock_llm = AsyncMock()
        ner = LLMBasedNER(llm_caller=mock_llm)
        
        entities = await ner.extract("")
        assert entities == []
    
    @pytest.mark.asyncio
    async def test_llm_ner_long_text_truncation(self):
        """测试长文本截断"""
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value={"content": "[]"})
        
        ner = LLMBasedNER(llm_caller=mock_llm)
        
        long_text = "测试" * 2000  # 4000字符
        await ner.extract(long_text)
        
        # 应该被截断到2000字符
        called_prompt = mock_llm.generate.call_args[1]["messages"][0]["content"]
        assert len(called_prompt) < len(long_text)
    
    def test_parse_response_valid_json(self):
        """测试解析有效JSON"""
        mock_llm = AsyncMock()
        ner = LLMBasedNER(llm_caller=mock_llm)
        
        content = '[{"text": "北京", "type": "LOCATION", "score": 0.9}]'
        entities = ner._parse_response(content)
        
        assert len(entities) == 1
        assert entities[0].text == "北京"
    
    def test_parse_response_with_markdown(self):
        """测试解析带Markdown的JSON"""
        mock_llm = AsyncMock()
        ner = LLMBasedNER(llm_caller=mock_llm)
        
        content = '```json\n[{"text": "北京", "type": "LOCATION", "score": 0.9}]\n```'
        entities = ner._parse_response(content)
        
        assert len(entities) == 1
        assert entities[0].text == "北京"
    
    def test_parse_response_fallback(self):
        """测试解析失败时的fallback"""
        mock_llm = AsyncMock()
        ner = LLMBasedNER(llm_caller=mock_llm)
        
        # 无效JSON
        content = "这不是JSON"
        entities = ner._parse_response(content)
        
        # 应该返回空或使用fallback
        assert isinstance(entities, list)


class TestHybridNER:
    """HybridNER 测试"""
    
    @pytest.mark.asyncio
    async def test_hybrid_ner_simple_only(self):
        """测试仅使用SimpleNER"""
        try:
            ner = HybridNER(
                fusion_strategy="simple_only",
                enable_llm_enhancement=False
            )
            
            entities = await ner.extract("张三在北京")
            
            assert isinstance(entities, list)
            # 所有实体应该来自SimpleNER
            for e in entities:
                assert e.metadata is None or e.metadata.get("source") != "llm"
        
        except ImportError:
            pytest.skip("jieba not installed")
    
    @pytest.mark.asyncio
    async def test_hybrid_ner_short_text(self):
        """测试短文本（不触发LLM）"""
        try:
            mock_llm = AsyncMock()
            from ame.ner import SimpleNER, LLMBasedNER
            
            ner = HybridNER(
                simple_ner=SimpleNER(),
                llm_ner=LLMBasedNER(llm_caller=mock_llm),
                use_llm_threshold=500,
                enable_llm_enhancement=True
            )
            
            short_text = "张三"  # 短文本
            entities = await ner.extract(short_text)
            
            # LLM不应该被调用
            assert not mock_llm.generate.called
        
        except ImportError:
            pytest.skip("Dependencies not installed")
    
    @pytest.mark.asyncio
    async def test_hybrid_ner_merge_strategy(self):
        """测试merge融合策略"""
        # Mock SimpleNER
        class MockSimpleNER(NERBase):
            async def extract(self, text):
                return [
                    Entity(text="张三", type="TOPIC", score=0.7),
                    Entity(text="北京", type="TOPIC", score=0.7)
                ]
        
        # Mock LLM NER
        class MockLLMNER(NERBase):
            async def extract(self, text):
                return [
                    Entity(text="张三", type="PERSON", score=0.95),
                    Entity(text="机器学习", type="TOPIC", score=0.9)
                ]
        
        ner = HybridNER(
            simple_ner=MockSimpleNER(),
            llm_ner=MockLLMNER(),
            use_llm_threshold=0,  # 总是使用LLM
            fusion_strategy="merge"
        )
        
        entities = await ner.extract("测试文本长度超过阈值才会调用LLM")
        
        # 应该包含merged结果
        texts = [e.text for e in entities]
        assert "张三" in texts  # 来自两者
        assert "北京" in texts  # 仅SimpleNER
        assert "机器学习" in texts  # 仅LLM
        
        # 张三应该使用LLM的类型（PERSON更精确）
        zhang_san = [e for e in entities if e.text == "张三"][0]
        assert zhang_san.type == "PERSON"
    
    def test_is_llm_better(self):
        """测试LLM实体优先级判断"""
        try:
            ner = HybridNER()
            
            simple_entity = Entity(text="张三", type="TOPIC", score=0.7)
            llm_entity = Entity(text="张三", type="PERSON", score=0.9)
            
            # LLM类型更精确（PERSON > TOPIC）
            assert ner._is_llm_better(simple_entity, llm_entity) is True
        
        except ImportError:
            pytest.skip("Dependencies not installed")
    
    @pytest.mark.asyncio
    async def test_hybrid_ner_empty_text(self):
        """测试空文本"""
        try:
            ner = HybridNER()
            
            entities = await ner.extract("")
            assert entities == []
        
        except ImportError:
            pytest.skip("Dependencies not installed")


@pytest.mark.asyncio
async def test_ner_integration():
    """NER集成测试"""
    try:
        from ame.ner import HybridNER
        
        ner = HybridNER()
        
        text = "张三在北京的清华大学研究人工智能和机器学习技术"
        entities = await ner.extract(text)
        
        assert len(entities) > 0
        
        # 检查实体类型分布
        types = [e.type for e in entities]
        assert any(t in ["PERSON", "LOCATION", "ORGANIZATION", "TOPIC"] for t in types)
        
        # 检查分数范围
        scores = [e.score for e in entities]
        assert all(0 <= s <= 1 for s in scores)
    
    except ImportError:
        pytest.skip("NER dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
