"""
LLM 调用器抽象基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str                                    # 生成的内容
    model: str                                      # 使用的模型
    usage: Dict[str, int]                           # Token 使用情况
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外的元数据
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "metadata": self.metadata
        }


class LLMCallerBase(ABC):
    """LLM 调用器抽象基类"""
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成回复
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数 (0-2, 越高越随机)
            max_tokens: 最大 token 数
            **kwargs: 其他模型特定参数
            
        Returns:
            LLM 响应
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式生成回复
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他模型特定参数
            
        Yields:
            生成的文本片段
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称"""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """检查是否已配置（API Key等）"""
        pass
    
    async def generate_with_system(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        使用系统提示词生成回复（便捷方法）
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            **kwargs: 其他参数
            
        Returns:
            LLM 响应
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        return await self.generate(messages, temperature=temperature, **kwargs)
