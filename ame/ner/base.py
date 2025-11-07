"""
NER 基础接口定义
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Entity:
    """实体数据结构"""
    
    text: str  # 实体文本
    type: str  # 实体类型 (PERSON, ORG, LOCATION, TOPIC, etc.)
    score: float = 1.0  # 置信度分数 (0-1)
    metadata: Optional[Dict] = None  # 扩展元数据
    
    def __hash__(self):
        return hash(self.text)
    
    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.text == other.text
        return False


class NERBase(ABC):
    """NER 基础抽象类"""
    
    @abstractmethod
    async def extract(self, text: str) -> List[Entity]:
        """
        从文本中提取实体
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表
        """
        pass
    
    def filter_entities(
        self,
        entities: List[Entity],
        min_score: float = 0.5,
        min_length: int = 2,
        entity_types: Optional[List[str]] = None
    ) -> List[Entity]:
        """
        过滤实体
        
        Args:
            entities: 原始实体列表
            min_score: 最小置信度
            min_length: 最小文本长度
            entity_types: 允许的实体类型（None表示所有类型）
            
        Returns:
            过滤后的实体列表
        """
        filtered = []
        
        for entity in entities:
            # 分数过滤
            if entity.score < min_score:
                continue
            
            # 长度过滤
            if len(entity.text) < min_length:
                continue
            
            # 类型过滤
            if entity_types and entity.type not in entity_types:
                continue
            
            filtered.append(entity)
        
        return filtered
    
    def deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        去重实体（保留高分）
        
        Args:
            entities: 实体列表
            
        Returns:
            去重后的实体列表
        """
        entity_map: Dict[str, Entity] = {}
        
        for entity in entities:
            if entity.text not in entity_map:
                entity_map[entity.text] = entity
            else:
                # 保留高分实体
                if entity.score > entity_map[entity.text].score:
                    entity_map[entity.text] = entity
        
        return list(entity_map.values())
