"""
LLM 工具类和数据类型

包含对话管理相关的数据类型和枚举
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


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


@dataclass
class ConversationMessage:
    """对话消息"""
    role: str                                       # 角色: user/assistant/system
    content: str                                    # 消息内容
    timestamp: Optional[datetime] = None            # 时间戳
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    compressed: bool = False                        # 是否为压缩后的消息
    
    def to_dict(self) -> dict:
        """转换为 OpenAI 格式"""
        return {
            "role": self.role,
            "content": self.content
        }
    
    def to_export_dict(self) -> dict:
        """转换为导出格式（包含完整信息）"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata,
            "compressed": self.compressed
        }


class ContextMode(Enum):
    """
    上下文管理模式
    
    不同模式对应不同的压缩策略和导出策略：
    - SESSION: 会话模式，保留完整历史，导出重要对话和最近上下文
    - DOCUMENT: 文档模式，静默压缩，导出 LLM 分析结果
    """
    SESSION = "session"      # 会话模式：保留完整历史，用于多轮对话
    DOCUMENT = "document"    # 文档模式：静默压缩，用于长文本处理
