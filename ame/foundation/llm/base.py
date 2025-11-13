"""
LLM 调用器抽象基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime

from .utils import LLMResponse, ConversationMessage, ContextMode


class ConversationHistory:
    """多轮对话历史管理器"""
    
    def __init__(
        self,
        max_context_tokens: Optional[int] = None,
        mode: ContextMode = ContextMode.SESSION
    ):
        """
        初始化对话历史
        
        Args:
            max_context_tokens: 最大上下文 token 数（默认 None 表示不限制）
            mode: 上下文管理模式
                - SESSION: 会话模式，保留完整历史，仅在用户主动清空时导出
                - DOCUMENT: 文档模式，自动静默压缩，保留压缩记录用于导出
        """
        self.messages: List[ConversationMessage] = []
        self.max_context_tokens = max_context_tokens
        self.mode = mode
        
        # 存储被压缩的历史消息（用于后续导出）
        self._archived_messages: List[ConversationMessage] = []
        
        # 压缩统计
        self._compression_count = 0
        self._total_messages_removed = 0
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        important: bool = False
    ) -> None:
        """
        添加消息到历史
        
        Args:
            role: 角色 (user/assistant/system)
            content: 消息内容
            metadata: 元数据
            important: 是否为重要消息（重要消息在压缩时会被优先保留）
        """
        metadata = metadata or {}
        metadata["important"] = important
        
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self.messages.append(message)
    
    def get_messages(self) -> List[Dict[str, str]]:
        """获取所有消息（OpenAI 格式）"""
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self) -> None:
        """清空历史"""
        self.messages.clear()
    
    def get_message_count(self) -> int:
        """获取消息数量"""
        return len(self.messages)
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """获取最后 N 条消息"""
        return [msg.to_dict() for msg in self.messages[-n:]]
    
    def remove_oldest_messages(self, count: int) -> None:
        """移除最旧的 N 条消息"""
        if count > 0:
            self.messages = self.messages[count:]
    
    def archive_removed_messages(self, removed_messages: List[ConversationMessage]) -> None:
        """
        归档被移除的消息（用于后续导出）
        
        Args:
            removed_messages: 被移除的消息列表
        """
        # 标记为已压缩
        for msg in removed_messages:
            msg.compressed = True
        
        self._archived_messages.extend(removed_messages)
        self._compression_count += 1
        self._total_messages_removed += len(removed_messages)
    
    def export_all(self) -> Dict[str, Any]:
        """
        导出所有消息（包括已归档的）
        
        适用场景：
        - 需要完整对话历史时
        - 进行数据备份时
        - 需要重建完整上下文时
        
        Returns:
            完整的消息历史字典
        """
        all_messages = self._archived_messages + self.messages
        
        return {
            "mode": self.mode.value,
            "total_messages": len(all_messages),
            "active_messages": len(self.messages),
            "archived_messages": len(self._archived_messages),
            "statistics": {
                "total_compressions": self._compression_count,
                "total_messages_removed": self._total_messages_removed
            },
            "messages": [msg.to_export_dict() for msg in all_messages]
        }
    
    def export_important(self) -> Dict[str, Any]:
        """
        导出关键信息
        
        根据初始化时指定的 mode 决定导出策略：
        - SESSION 模式：导出标记为 important 的消息 + 最近5条对话
        - DOCUMENT 模式：导出 LLM 分析结果（assistant 回复）
        
        适用场景：
        - SESSION: 用户对话结束时，导出重要信息到图谱
        - DOCUMENT: 文档处理完成后，导出 LLM 分析结果
        
        Returns:
            关键信息字典
        """
        all_messages = self._archived_messages + self.messages
        
        if self.mode == ContextMode.SESSION:
            # 会话模式：导出重要消息 + 最近对话
            important_messages = [
                msg for msg in all_messages 
                if msg.metadata.get("important", False)
            ]
            
            # 添加最近的 5 条对话（保持上下文）
            recent_messages = self.messages[-5:] if len(self.messages) > 5 else self.messages
            
            # 去重
            seen = set()
            unique_messages = []
            for msg in important_messages + recent_messages:
                msg_key = (msg.role, msg.content)
                if msg_key not in seen:
                    seen.add(msg_key)
                    unique_messages.append(msg)
            
            return {
                "mode": "session",
                "total_conversations": len(all_messages),
                "important_count": len(important_messages),
                "export_content": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                        "important": msg.metadata.get("important", False)
                    }
                    for msg in unique_messages
                ]
            }
        
        else:  # DOCUMENT 模式
            # 文档模式：导出 LLM 分析结果
            analysis_results = [
                msg for msg in all_messages 
                if msg.role == "assistant"
            ]
            
            # 提取标记为重要的用户输入（原始文档关键部分）
            important_inputs = [
                msg for msg in all_messages
                if msg.role == "user" and msg.metadata.get("important", False)
            ]
            
            return {
                "mode": "document",
                "total_messages": len(all_messages),
                "analysis_count": len(analysis_results),
                "export_content": {
                    "llm_analysis": [
                        {
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                        }
                        for msg in analysis_results
                    ],
                    "important_inputs": [
                        {
                            "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                        }
                        for msg in important_inputs
                    ]
                }
            }
    
    def clear_and_export(self) -> Dict[str, Any]:
        """
        清空对话并导出关键信息
        
        适用场景：
        - SESSION 模式：用户对话结束时调用
        - DOCUMENT 模式：文档处理完成后调用
        
        Returns:
            导出的关键信息（根据 mode 自动选择导出策略）
        """
        export_data = self.export_important()
        
        # 清空当前历史
        self.messages.clear()
        self._archived_messages.clear()
        self._compression_count = 0
        self._total_messages_removed = 0
        
        return export_data
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """
        获取压缩统计信息
        
        Returns:
            压缩统计数据
        """
        return {
            "mode": self.mode.value,
            "total_compressions": self._compression_count,
            "total_messages_removed": self._total_messages_removed,
            "active_messages": len(self.messages),
            "archived_messages": len(self._archived_messages),
            "total_messages": len(self.messages) + len(self._archived_messages)
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
    
    def estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量
        
        使用简单规则估算（1 token ≈ 4 个字符）
        子类可以重写此方法以提供更精确的估算
        
        Args:
            text: 输入文本
            
        Returns:
            估算的 token 数
        """
        return len(text) // 4
    
    def compress_messages(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        压缩消息列表以适应 token 限制
        
        策略：
        1. 保留系统消息
        2. 保留标记为重要的消息
        3. 保留最新的用户消息
        4. 从旧到新逐步移除消息，直到满足 token 限制
        
        Args:
            messages: 消息列表
            max_tokens: 最大 token 数
            
        Returns:
            压缩后的消息列表
        """
        if not messages:
            return []
        
        # 分离不同类型的消息
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        important_messages = [
            msg for msg in messages 
            if msg.get("role") != "system" and msg.get("metadata", {}).get("important", False)
        ]
        normal_messages = [
            msg for msg in messages 
            if msg.get("role") != "system" and not msg.get("metadata", {}).get("important", False)
        ]
        
        # 计算当前 token 总数
        total_tokens = sum(self.estimate_tokens(msg.get("content", "")) for msg in messages)
        
        if total_tokens <= max_tokens:
            return messages
        
        # 需要压缩
        compressed = system_messages.copy()
        system_tokens = sum(self.estimate_tokens(msg.get("content", "")) for msg in system_messages)
        
        # 添加重要消息
        important_tokens = sum(self.estimate_tokens(msg.get("content", "")) for msg in important_messages)
        compressed.extend(important_messages)
        
        remaining_tokens = max_tokens - system_tokens - important_tokens
        
        # 从最新的普通消息开始添加，直到达到 token 限制
        current_tokens = 0
        added_normal = []
        for msg in reversed(normal_messages):
            msg_tokens = self.estimate_tokens(msg.get("content", ""))
            
            if current_tokens + msg_tokens <= remaining_tokens:
                added_normal.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        compressed.extend(added_normal)
        
        # 按原始顺序排序
        compressed.sort(key=lambda x: messages.index(x) if x in messages else 0)
        
        return compressed
