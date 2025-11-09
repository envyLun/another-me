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
from .base import LLMCallerBase, LLMResponse

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_API_KEY = ""
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 3


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
        cache_enabled: bool = True
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
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", DEFAULT_API_KEY)
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL)
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.max_retries = max_retries
        self.timeout = timeout
        self.cache_enabled = cache_enabled
        
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
            f"(model={self.model}, base_url={self.base_url})"
        )
    
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
