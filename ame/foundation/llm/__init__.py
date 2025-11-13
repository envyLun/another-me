"""
LLM - LLM 调用能力

提供统一的 LLM 调用接口，支持多种 LLM 提供商。

核心组件：
- LLMCallerBase: LLM 调用器抽象基类
- LLMResponse: LLM 响应封装
- OpenAICaller: OpenAI LLM 调用器
- ConversationMessage: 对话消息数据类
- ConversationHistory: 多轮对话历史管理器
- ContextMode: 上下文管理模式枚举
"""

from .base import LLMCallerBase, ConversationHistory
from .openai_caller import OpenAICaller
from .utils import LLMResponse, ConversationMessage, ContextMode

__all__ = [
    "LLMCallerBase",
    "LLMResponse",
    "OpenAICaller",
    "ConversationMessage",
    "ConversationHistory",
    "ContextMode",
]
