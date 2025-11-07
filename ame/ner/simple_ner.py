"""
SimpleNER: 基于 jieba 词性标注的简单实体提取

特点：
- 快速、轻量级
- 适用于中文文本
- 基于词性识别实体
"""

import logging
from typing import List, Optional

from ame.ner.base import NERBase, Entity

logger = logging.getLogger(__name__)


class SimpleNER(NERBase):
    """简单 NER 实现（基于 jieba 词性标注）"""
    
    # 实体类型映射 (jieba 词性 -> 实体类型)
    POS_TO_ENTITY_TYPE = {
        "nr": "PERSON",      # 人名
        "ns": "LOCATION",    # 地名
        "nt": "ORGANIZATION", # 机构名
        "nz": "OTHER",       # 其他专名
        "n": "TOPIC",        # 普通名词（主题词）
        "vn": "TOPIC",       # 名动词（主题词）
        "eng": "TOPIC",      # 英文词
    }
    
    def __init__(
        self,
        enable_paddle: bool = False,
        min_word_length: int = 2,
        extract_nouns: bool = True
    ):
        """
        初始化 SimpleNER
        
        Args:
            enable_paddle: 是否启用 Paddle 模式（更准确但需要安装 paddlepaddle）
            min_word_length: 最小词长度
            extract_nouns: 是否提取普通名词作为主题词
        """
        self.min_word_length = min_word_length
        self.extract_nouns = extract_nouns
        
        try:
            import jieba
            import jieba.posseg as posseg
            
            # 启用 Paddle 模式（可选）
            if enable_paddle:
                try:
                    jieba.enable_paddle()
                    logger.info("SimpleNER: Paddle 模式已启用")
                except Exception as e:
                    logger.warning(f"SimpleNER: Paddle 模式启用失败，使用默认模式: {e}")
            
            self.jieba = jieba
            self.posseg = posseg
            logger.info("SimpleNER 初始化成功")
            
        except ImportError:
            raise ImportError(
                "SimpleNER 需要安装 jieba。请运行: pip install jieba"
            )
    
    async def extract(self, text: str) -> List[Entity]:
        """
        提取实体
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表
        """
        if not text or not text.strip():
            return []
        
        entities = []
        
        try:
            # 词性标注
            words = self.posseg.cut(text)
            
            for word, pos in words:
                # 长度过滤
                if len(word) < self.min_word_length:
                    continue
                
                # 跳过停用词
                if self._is_stopword(word):
                    continue
                
                # 映射实体类型
                entity_type = self._map_entity_type(pos)
                
                if entity_type:
                    # 如果不提取普通名词，跳过 TOPIC 类型
                    if not self.extract_nouns and entity_type == "TOPIC":
                        continue
                    
                    entities.append(Entity(
                        text=word,
                        type=entity_type,
                        score=self._calculate_score(word, pos),
                        metadata={"pos": pos}
                    ))
        
        except Exception as e:
            logger.error(f"SimpleNER 实体提取失败: {e}")
            return []
        
        # 去重
        entities = self.deduplicate_entities(entities)
        
        return entities
    
    def _map_entity_type(self, pos: str) -> Optional[str]:
        """映射词性到实体类型"""
        return self.POS_TO_ENTITY_TYPE.get(pos)
    
    def _calculate_score(self, word: str, pos: str) -> float:
        """
        计算实体置信度分数
        
        规则：
        - 专有名词（nr, ns, nt）得分高
        - 普通名词得分中等
        - 词长度越长得分越高
        """
        base_score = 0.7
        
        # 专有名词加分
        if pos in ["nr", "ns", "nt", "nz"]:
            base_score = 0.9
        
        # 长度加分（上限 1.0）
        length_bonus = min(len(word) * 0.05, 0.3)
        
        return min(base_score + length_bonus, 1.0)
    
    def _is_stopword(self, word: str) -> bool:
        """判断是否为停用词"""
        stopwords = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
            "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
            "你", "会", "着", "没有", "看", "好", "自己", "这", "那"
        }
        return word in stopwords
