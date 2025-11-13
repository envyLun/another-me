"""
OpenAI LLM 调用器

支持 OpenAI 和 OpenAI-Compatible API（如 Azure OpenAI, Together AI 等）

特性：
- 自动重试机制（指数退避）
- 请求缓存（基于消息内容）
- 流式输出支持
- 完整的错误处理
"""

import os
import asyncio
import hashlib
import json
import logging
from typing import List, Dict, Optional, AsyncIterator, Any

from openai import AsyncOpenAI
from .base import LLMCallerBase, ConversationHistory
from .utils import LLMResponse, ContextMode, ConversationMessage

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_API_KEY = ""
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_MAX_CONTEXT_TOKENS = 4000  # 默认最大上下文 token 数


class OpenAICaller(LLMCallerBase):
    """
    OpenAI LLM 调用器
    
    支持 OpenAI 和兼容 API，具备重试、缓存、流式输出等特性
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: float = DEFAULT_TIMEOUT,
        cache_enabled: bool = False,  # 默认关闭缓存以保证创造性
        max_context_tokens: Optional[int] = None
    ):
        """
        初始化 OpenAI 调用器
        
        Args:
            api_key: OpenAI API Key（默认从环境变量读取）
            base_url: API Base URL（默认 OpenAI 官方地址）
            model: 默认使用的模型名称
            max_retries: 最大重试次数
            timeout: 请求超时时间（秒）
            cache_enabled: 是否启用缓存
            max_context_tokens: 最大上下文 token 数（超过时自动压缩）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", DEFAULT_API_KEY)
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL)
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.max_retries = max_retries
        self.timeout = timeout
        self.cache_enabled = cache_enabled
        self.max_context_tokens = max_context_tokens or DEFAULT_MAX_CONTEXT_TOKENS
        
        self._cache: Dict[str, LLMResponse] = {}
        self._client: Optional[AsyncOpenAI] = None
        
        # 延迟初始化客户端
        if self.api_key:
            self._init_client()
    
    def _init_client(self) -> None:
        """初始化 AsyncOpenAI 客户端"""
        if not self.api_key:
            logger.warning("OpenAI API Key 未配置")
            return
        
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0  # 手动处理重试逻辑
        )
        
        logger.info(
            f"OpenAI 客户端初始化成功 "
            f"(model={self.model}, base_url={self.base_url}, "
            f"max_context_tokens={self.max_context_tokens})"
        )
    
    def estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量
        
        使用更精确的估算方法：
        - 英文：1 token ≈ 4 个字符
        - 中文：1 token ≈ 1.5 个字符
        
        Args:
            text: 输入文本
            
        Returns:
            估算的 token 数
        """
        if not text:
            return 0
        
        # 统计中英文字符
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_chars = len(text) - chinese_chars
        
        # 中文约 1.5 字符/token，英文约 4 字符/token
        tokens = int(chinese_chars / 1.5 + english_chars / 4)
        
        return max(tokens, 1)
    
    def _compress_messages_if_needed(
        self,
        messages: List[Dict[str, str]],
        conversation: Optional[ConversationHistory] = None
    ) -> List[Dict[str, str]]:
        """
        如果消息超过上下文限制，自动压缩
        
        Args:
            messages: 原始消息列表
            conversation: 对话历史对象（可选）
            
        Returns:
            压缩后的消息列表
        """
        # 计算总 token 数
        total_tokens = sum(self.estimate_tokens(msg.get("content", "")) for msg in messages)
        
        if total_tokens <= self.max_context_tokens:
            return messages
        
        # 需要压缩
        mode = conversation.mode if conversation else ContextMode.SESSION
        
        if mode == ContextMode.DOCUMENT:
            # 文档模式：静默压缩
            logger.info(
                f"[文档模式] 上下文过长 (total_tokens={total_tokens}, "
                f"max={self.max_context_tokens})，正在自动压缩..."
            )
        else:
            # 会话模式：警告压缩
            logger.warning(
                f"[会话模式] 上下文过长 (total_tokens={total_tokens}, "
                f"max={self.max_context_tokens})，正在压缩..."
            )
        
        compressed = self.compress_messages(messages, self.max_context_tokens)
        
        compressed_tokens = sum(self.estimate_tokens(msg.get("content", "")) for msg in compressed)
        removed_count = len(messages) - len(compressed)
        
        # 如果有 conversation 对象，归档被移除的消息
        if conversation and removed_count > 0:
            removed_messages = []
            compressed_contents = {msg.get("content") for msg in compressed}
            
            for msg in messages:
                if msg.get("content") not in compressed_contents:
                    # 转换为 ConversationMessage 对象
                    removed_msg = ConversationMessage(
                        role=msg.get("role", "user"),
                        content=msg.get("content", ""),
                        metadata=msg.get("metadata", {}),
                        compressed=True
                    )
                    removed_messages.append(removed_msg)
            
            conversation.archive_removed_messages(removed_messages)
        
        logger.info(
            f"上下文压缩完成：移除 {removed_count} 条消息，"
            f"token 数从 {total_tokens} 降至 {compressed_tokens}"
        )
        
        return compressed
    
    def _get_cache_key(
        self,
        messages: List[Dict],
        model: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """
        生成缓存键
        
        基于消息内容、模型参数生成唯一的 MD5 哈希
        """
        cache_data = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[LLMResponse]:
        """从缓存获取响应"""
        if not self.cache_enabled:
            return None
        return self._cache.get(cache_key)
    
    def _save_to_cache(self, cache_key: str, response: LLMResponse):
        """保存响应到缓存"""
        if self.cache_enabled:
            self._cache[cache_key] = response
            logger.debug(f"缓存已保存 (key={cache_key[:8]}...)")
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成回复
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            model: 模型名称（可选，默认使用初始化时的模型）
            **kwargs: 其他 OpenAI API 参数
            
        Returns:
            LLM 响应
            
        Raises:
            ValueError: API 未配置
            Exception: 生成失败
        """
        if not self._client:
            self._init_client()
        
        if not self._client:
            raise ValueError("OpenAI API Key 未配置，请设置 OPENAI_API_KEY 环境变量")
        
        model = model or self.model
        
        # 自动压缩上下文（如果需要）
        messages = self._compress_messages_if_needed(messages, conversation=None)
        
        # 检查缓存
        cache_key = self._get_cache_key(messages, model, temperature, max_tokens)
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            logger.debug(f"命中缓存 (key={cache_key[:8]}...)")
            return cached_response
        
        # 重试机制（指数退避）
        last_error: Optional[Exception] = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"调用 OpenAI API (attempt={attempt + 1}, "
                    f"model={model}, temperature={temperature})"
                )
                
                response = await self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                # 封装响应
                llm_response = LLMResponse(
                    content=response.choices[0].message.content or "",
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    metadata={
                        "finish_reason": response.choices[0].finish_reason,
                        "attempt": attempt + 1
                    }
                )
                
                # 保存到缓存
                self._save_to_cache(cache_key, llm_response)
                
                logger.info(
                    f"生成成功 (tokens={llm_response.usage['total_tokens']}, "
                    f"attempt={attempt + 1})"
                )
                
                return llm_response
            
            except Exception as e:
                last_error = e
                logger.warning(
                    f"生成失败 (attempt={attempt + 1}/{self.max_retries}): {str(e)}"
                )
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < self.max_retries - 1:
                    # 指数退避：0.5s, 1s, 2s, ...
                    wait_time = (2 ** attempt) * 0.5
                    logger.debug(f"等待 {wait_time}s 后重试...")
                    await asyncio.sleep(wait_time)
                    continue
        
        # 所有重试均失败
        error_msg = f"LLM 生成失败（{self.max_retries} 次重试后）: {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式生成回复
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            model: 模型名称
            **kwargs: 其他参数
            
        Yields:
            生成的文本片段
            
        Raises:
            ValueError: API 未配置
            Exception: 生成失败
        """
        if not self._client:
            self._init_client()
        
        if not self._client:
            raise ValueError("OpenAI API Key 未配置")
        
        model = model or self.model
        
        # 自动压缩上下文（如果需要）
        messages = self._compress_messages_if_needed(messages, conversation=None)
        
        # 重试机制
        last_error: Optional[Exception] = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"调用 OpenAI Stream API (attempt={attempt + 1}, model={model})"
                )
                
                response = await self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    **kwargs
                )
                
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                
                logger.info("流式生成完成")
                return
            
            except Exception as e:
                last_error = e
                logger.warning(
                    f"流式生成失败 (attempt={attempt + 1}/{self.max_retries}): {str(e)}"
                )
                
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) * 0.5
                    await asyncio.sleep(wait_time)
                    continue
        
        error_msg = f"流式生成失败（{self.max_retries} 次重试后）: {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.model
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.api_key and self._client)
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("LLM 缓存已清空")
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)
    
    def create_conversation(
        self,
        system_prompt: Optional[str] = None,
        mode: ContextMode = ContextMode.SESSION
    ) -> ConversationHistory:
        """
        创建多轮对话历史管理器
        
        Args:
            system_prompt: 系统提示词（可选）
            mode: 上下文管理模式
                - SESSION: 会话模式，用于多轮对话，保留完整历史
                - DOCUMENT: 文档模式，用于长文本处理，自动静默压缩
            
        Returns:
            ConversationHistory 实例
            
        Example:
            # 会话模式：用于用户对话
            conversation = llm.create_conversation(
                system_prompt="你是一个友好的助手",
                mode=ContextMode.SESSION
            )
            # ... 多轮对话 ...
            # 清空对话时导出到图谱
            graph_data = conversation.clear_and_export()
            
            # 文档模式：用于处理长文本
            doc_conversation = llm.create_conversation(
                system_prompt="请分析以下文档",
                mode=ContextMode.DOCUMENT
            )
            # ... 自动静默压缩 ...
            # 处理完成后导出关键信息（LLM 分析结果）
            important_data = doc_conversation.export_important()
            
            # 或者清空并导出（自动根据 mode 选择导出策略）
            export_data = doc_conversation.clear_and_export()
        """
        conversation = ConversationHistory(
            max_context_tokens=self.max_context_tokens,
            mode=mode
        )
        
        if system_prompt:
            conversation.add_message("system", system_prompt)
        
        return conversation
    
    async def chat_with_history(
        self,
        conversation: ConversationHistory,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        使用对话历史进行多轮对话
        
        Args:
            conversation: 对话历史对象
            user_message: 用户消息
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数
            
        Returns:
            LLM 响应
        """
        # 添加用户消息到历史
        conversation.add_message("user", user_message)
        
        # 获取所有消息
        messages = conversation.get_messages()
        
        # 自动压缩（传入 conversation 对象以便归档）
        messages = self._compress_messages_if_needed(messages, conversation=conversation)
        
        # 生成回复
        response = await self.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # 添加 AI 回复到历史
        conversation.add_message("assistant", response.content)
        
        return response
    
    async def chat_stream_with_history(
        self,
        conversation: ConversationHistory,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        使用对话历史进行流式多轮对话
        
        Args:
            conversation: 对话历史对象
            user_message: 用户消息
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数
            
        Yields:
            生成的文本片段
        """
        # 添加用户消息到历史
        conversation.add_message("user", user_message)
        
        # 获取所有消息
        messages = conversation.get_messages()
        
        # 自动压缩（传入 conversation 对象以便归档）
        messages = self._compress_messages_if_needed(messages, conversation=conversation)
        
        # 收集流式输出
        full_response = ""
        
        async for chunk in self.generate_stream(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            full_response += chunk
            yield chunk
        
        # 添加完整回复到历史
        conversation.add_message("assistant", full_response)
