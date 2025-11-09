"""
Mimic Service - 模仿对话服务

基于 MimicEngine 提供用户风格模仿的对话服务
整合 capabilities 层的能力，提供业务级服务
"""

from typing import Dict, Any, Optional, AsyncIterator
from datetime import datetime

from ame.foundation.llm import LLMCallerBase
from ame.foundation.storage import VectorStoreBase
from ame.capabilities.memory import ConversationFilter
from ame.models.domain import MemoryRetentionType


class MimicService:
    """
    模仿对话服务
    
    职责：
    - 学习用户对话风格
    - 生成模仿用户风格的回复
    - 管理对话记忆（集成 ConversationFilter）
    """
    
    def __init__(
        self,
        llm_caller: LLMCallerBase,
        vector_store: VectorStoreBase,
        enable_filter: bool = True
    ):
        """
        初始化模仿服务
        
        Args:
            llm_caller: LLM 调用器
            vector_store: 向量存储
            enable_filter: 是否启用对话过滤
        """
        self.llm = llm_caller
        self.vector_store = vector_store
        self.filter = ConversationFilter(llm_caller) if enable_filter else None
    
    async def learn_from_conversation(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MemoryRetentionType:
        """
        从用户对话中学习
        
        Args:
            user_message: 用户消息
            context: 对话上下文
        
        Returns:
            retention_type: 记忆保留类型
        """
        # 对话过滤 - 判断是否需要存储
        retention_type = MemoryRetentionType.TEMPORARY
        
        if self.filter:
            retention_type = await self.filter.classify_conversation(
                user_message,
                context=context
            )
            
            # 如果是闲聊，不存储
            if not self.filter.should_store(retention_type):
                return retention_type
        
        # 构建学习数据
        doc = {
            "doc_id": f"conv_{datetime.now().timestamp()}",
            "content": user_message,
            "embedding": None,  # 需要外部生成
            "metadata": {
                "source": "user_conversation",
                "timestamp": datetime.now().isoformat(),
                "retention_type": retention_type.value,
                "context": context or {}
            }
        }
        
        # TODO: 生成 embedding 并存储到 vector_store
        # await self.vector_store.add(doc)
        
        return retention_type
    
    async def generate_response(
        self,
        prompt: str,
        temperature: float = 0.8,
        use_history: bool = True
    ) -> str:
        """
        生成模仿用户风格的回复
        
        Args:
            prompt: 提示词
            temperature: 温度参数
            use_history: 是否使用历史记录
        
        Returns:
            response: 生成的回复
        """
        # TODO: 检索相关的历史对话
        # if use_history:
        #     results = await self.vector_store.search(...)
        
        # 构建系统提示词
        system_prompt = self._build_mimic_prompt([])
        
        # 生成回复
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.generate(
            messages=messages,
            temperature=temperature
        )
        
        return response.content
    
    async def generate_response_stream(
        self,
        prompt: str,
        temperature: float = 0.8,
        use_history: bool = True
    ) -> AsyncIterator[str]:
        """
        流式生成模仿用户风格的回复
        
        Args:
            prompt: 提示词
            temperature: 温度参数
            use_history: 是否使用历史记录
        
        Yields:
            chunk: 生成的文本片段
        """
        # 构建系统提示词
        system_prompt = self._build_mimic_prompt([])
        
        # 流式生成回复
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        async for chunk in self.llm.generate_stream(
            messages=messages,
            temperature=temperature
        ):
            yield chunk
    
    def _build_mimic_prompt(self, relevant_history: list) -> str:
        """
        构建模仿提示词
        
        Args:
            relevant_history: 相关历史对话
        
        Returns:
            prompt: 提示词
        """
        prompt = """你是用户的 AI 分身，任务是用用户的风格和方式回答问题。

**重要事项**：
1. 用第一人称"我"来表达，而不是"用户"或"他/她"
2. 模仿用户的说话风格、惯用词汇和表达习惯
3. 保持真实感，不要过于形式化
4. 如果不确定，可以说"我不太确定"或"我需要想想"
"""
        
        if relevant_history:
            prompt += "\n**参考用户的历史表达**（学习风格）：\n"
            for i, h in enumerate(relevant_history[:3], 1):
                content = h.get('content', '')[:150]
                prompt += f"{i}. {content}...\n"
            prompt += "\n请模仿上述表达风格来回答。\n"
        
        return prompt
