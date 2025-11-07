"""
LLMBasedNER: 基于大语言模型的实体提取

特点：
- 准确度高
- 支持复杂实体识别
- 上下文理解能力强
- 需要调用 LLM API（成本较高）
"""

import logging
import json
from typing import List, Optional

from ame.ner.base import NERBase, Entity
from ame.llm_caller.base import LLMCallerBase

logger = logging.getLogger(__name__)


class LLMBasedNER(NERBase):
    """基于 LLM 的实体提取"""
    
    EXTRACTION_PROMPT = """你是一个专业的实体提取助手。请从以下文本中提取关键实体。

提取规则：
1. 识别人名、地名、机构名、主题词等实体
2. 返回 JSON 格式，每个实体包含 text（实体文本）、type（实体类型）、score（置信度0-1）
3. 实体类型包括：PERSON（人名）、LOCATION（地名）、ORGANIZATION（机构）、TOPIC（主题词）、OTHER（其他）
4. 只提取重要实体，过滤无意义词汇

文本：
{text}

返回格式示例：
[
  {{"text": "张三", "type": "PERSON", "score": 0.95}},
  {{"text": "北京", "type": "LOCATION", "score": 0.9}},
  {{"text": "数据分析", "type": "TOPIC", "score": 0.85}}
]

请直接返回 JSON 数组，不要添加其他说明文字。"""
    
    def __init__(
        self,
        llm_caller: LLMCallerBase,
        temperature: float = 0.1,
        max_retries: int = 2
    ):
        """
        初始化 LLMBasedNER
        
        Args:
            llm_caller: LLM 调用器实例
            temperature: LLM 温度参数（低温度更稳定）
            max_retries: 最大重试次数
        """
        self.llm = llm_caller
        self.temperature = temperature
        self.max_retries = max_retries
        logger.info("LLMBasedNER 初始化成功")
    
    async def extract(self, text: str) -> List[Entity]:
        """
        使用 LLM 提取实体
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表
        """
        if not text or not text.strip():
            return []
        
        # 文本过长时截断（避免超过 LLM token 限制）
        if len(text) > 2000:
            text = text[:2000] + "..."
            logger.warning("LLMBasedNER: 文本过长，已截断至 2000 字符")
        
        # 构造 prompt
        prompt = self.EXTRACTION_PROMPT.format(text=text)
        
        # 调用 LLM（带重试）
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.llm.generate(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature
                )
                
                content = response.get("content", "").strip()
                
                # 解析 JSON
                entities = self._parse_response(content)
                
                if entities:
                    logger.info(f"LLMBasedNER 提取到 {len(entities)} 个实体")
                    return entities
                
            except Exception as e:
                logger.warning(f"LLMBasedNER 第 {attempt + 1} 次尝试失败: {e}")
                
                if attempt == self.max_retries:
                    logger.error(f"LLMBasedNER 实体提取失败（已重试 {self.max_retries} 次）")
                    return []
        
        return []
    
    def _parse_response(self, content: str) -> List[Entity]:
        """
        解析 LLM 响应
        
        Args:
            content: LLM 返回的文本
            
        Returns:
            实体列表
        """
        try:
            # 尝试提取 JSON 部分
            content = content.strip()
            
            # 移除可能的 Markdown 代码块标记
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
                content = content.replace("```json", "").replace("```", "").strip()
            
            # 解析 JSON
            data = json.loads(content)
            
            if not isinstance(data, list):
                logger.warning("LLMBasedNER: 响应不是 JSON 数组")
                return []
            
            # 转换为 Entity 对象
            entities = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                text = item.get("text", "").strip()
                entity_type = item.get("type", "OTHER").upper()
                score = float(item.get("score", 0.8))
                
                if text and len(text) > 1:
                    entities.append(Entity(
                        text=text,
                        type=entity_type,
                        score=score,
                        metadata={"source": "llm"}
                    ))
            
            return entities
        
        except json.JSONDecodeError as e:
            logger.error(f"LLMBasedNER JSON 解析失败: {e}\n内容: {content}")
            
            # Fallback: 简单文本解析
            return self._fallback_parse(content)
        
        except Exception as e:
            logger.error(f"LLMBasedNER 响应解析失败: {e}")
            return []
    
    def _fallback_parse(self, content: str) -> List[Entity]:
        """
        备用解析（当 JSON 解析失败时）
        
        简单按逗号分割提取实体
        """
        entities = []
        
        # 移除特殊字符
        content = content.replace("[", "").replace("]", "").replace("{", "").replace("}", "")
        
        # 按逗号分割
        parts = [p.strip() for p in content.split(",") if p.strip()]
        
        for part in parts:
            # 简单过滤
            if len(part) > 1 and len(part) < 20:
                entities.append(Entity(
                    text=part,
                    type="TOPIC",
                    score=0.6,
                    metadata={"source": "llm_fallback"}
                ))
        
        if entities:
            logger.warning(f"LLMBasedNER 使用 fallback 解析，提取到 {len(entities)} 个实体")
        
        return entities
