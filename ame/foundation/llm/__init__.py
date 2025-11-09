"""
LLM - LLM 调用能力

提供统一的 LLM 调用接口，支持多种 LLM 提供商。

核心组件：
- LLMCallerBase: LLM 调用器抽象基类
- LLMResponse: LLM 响应封装
- OpenAICaller: OpenAI LLM 调用器
"""

from .base import LLMCallerBase, LLMResponse
from .openai_caller import OpenAICaller

__all__ = [
    "LLMCallerBase",
    "LLMResponse",
    "OpenAICaller",
]
