"""
HybridNER: 混合实体提取策略

组合 SimpleNER 和 LLMBasedNER 的优势：
- 快速：优先使用 SimpleNER（轻量级）
- 准确：LLM 增强（可选，按需启用）
- 智能融合：去重、合并结果
"""

import logging
from typing import List, Optional

from ame.ner.base import NERBase, Entity
from ame.ner.simple_ner import SimpleNER
from ame.ner.llm_ner import LLMBasedNER

logger = logging.getLogger(__name__)


class HybridNER(NERBase):
    """混合实体提取器"""
    
    def __init__(
        self,
        simple_ner: Optional[SimpleNER] = None,
        llm_ner: Optional[LLMBasedNER] = None,
        use_llm_threshold: int = 500,  # 文本长度超过此阈值才使用 LLM
        enable_llm_enhancement: bool = True,  # 是否启用 LLM 增强
        fusion_strategy: str = "merge"  # 融合策略: merge | llm_only | simple_only
    ):
        """
        初始化 HybridNER
        
        Args:
            simple_ner: SimpleNER 实例（如果为 None 则自动创建）
            llm_ner: LLMBasedNER 实例（可选）
            use_llm_threshold: 文本长度超过此值时才使用 LLM
            enable_llm_enhancement: 是否启用 LLM 增强
            fusion_strategy: 融合策略
                - merge: 合并两种结果（去重）
                - llm_only: 仅使用 LLM 结果
                - simple_only: 仅使用 SimpleNER 结果
        """
        self.simple_ner = simple_ner or SimpleNER()
        self.llm_ner = llm_ner
        self.use_llm_threshold = use_llm_threshold
        self.enable_llm_enhancement = enable_llm_enhancement
        self.fusion_strategy = fusion_strategy
        
        logger.info(
            f"HybridNER 初始化完成 (策略: {fusion_strategy}, "
            f"LLM增强: {enable_llm_enhancement}, "
            f"LLM阈值: {use_llm_threshold}字符)"
        )
    
    async def extract(self, text: str) -> List[Entity]:
        """
        混合实体提取
        
        流程:
        1. 始终执行 SimpleNER（快速）
        2. 根据文本长度和配置决定是否使用 LLM
        3. 融合结果
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表
        """
        if not text or not text.strip():
            return []
        
        text_length = len(text)
        
        # 策略1: 仅 SimpleNER
        if self.fusion_strategy == "simple_only" or not self.enable_llm_enhancement:
            return await self.simple_ner.extract(text)
        
        # 策略2: 仅 LLM
        if self.fusion_strategy == "llm_only" and self.llm_ner:
            return await self.llm_ner.extract(text)
        
        # 策略3: 混合（merge）
        simple_entities = await self.simple_ner.extract(text)
        
        # 判断是否需要 LLM 增强
        use_llm = (
            self.llm_ner is not None and
            self.enable_llm_enhancement and
            text_length >= self.use_llm_threshold
        )
        
        if not use_llm:
            logger.debug(f"HybridNER: 文本长度 {text_length} < {self.use_llm_threshold}，跳过 LLM")
            return simple_entities
        
        # 调用 LLM 增强
        try:
            llm_entities = await self.llm_ner.extract(text)
            
            # 融合结果
            merged_entities = self._merge_entities(simple_entities, llm_entities)
            
            logger.info(
                f"HybridNER: SimpleNER提取{len(simple_entities)}个, "
                f"LLM提取{len(llm_entities)}个, "
                f"融合后{len(merged_entities)}个实体"
            )
            
            return merged_entities
        
        except Exception as e:
            logger.error(f"HybridNER LLM增强失败，回退到 SimpleNER: {e}")
            return simple_entities
    
    def _merge_entities(
        self,
        simple_entities: List[Entity],
        llm_entities: List[Entity]
    ) -> List[Entity]:
        """
        融合两个实体列表
        
        规则:
        1. 同文本的实体保留高分者
        2. LLM 实体优先级更高（如果类型更准确）
        3. 去重并排序
        
        Args:
            simple_entities: SimpleNER 提取的实体
            llm_entities: LLM 提取的实体
            
        Returns:
            融合后的实体列表
        """
        entity_map = {}
        
        # 1. 加入 SimpleNER 实体
        for entity in simple_entities:
            entity_map[entity.text] = entity
        
        # 2. 加入 LLM 实体（可能覆盖）
        for entity in llm_entities:
            if entity.text in entity_map:
                existing = entity_map[entity.text]
                
                # LLM 实体类型更精确，或分数更高时覆盖
                if self._is_llm_better(existing, entity):
                    entity_map[entity.text] = entity
            else:
                entity_map[entity.text] = entity
        
        # 3. 转换为列表并按分数排序
        merged = list(entity_map.values())
        merged.sort(key=lambda e: e.score, reverse=True)
        
        return merged
    
    def _is_llm_better(self, simple_entity: Entity, llm_entity: Entity) -> bool:
        """
        判断 LLM 实体是否更优
        
        规则:
        - LLM 类型更具体（PERSON/LOCATION/ORGANIZATION > TOPIC）
        - LLM 分数更高
        """
        # 类型优先级
        type_priority = {
            "PERSON": 4,
            "LOCATION": 3,
            "ORGANIZATION": 3,
            "TOPIC": 2,
            "OTHER": 1
        }
        
        simple_priority = type_priority.get(simple_entity.type, 0)
        llm_priority = type_priority.get(llm_entity.type, 0)
        
        # LLM 类型更具体
        if llm_priority > simple_priority:
            return True
        
        # 类型相同时比分数
        if llm_priority == simple_priority:
            return llm_entity.score > simple_entity.score
        
        return False
