"""
模仿引擎 - 学习和模仿用户说话风格
"""

from typing import List, Dict, Any, Optional, AsyncIterator
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ame.foundation.llm import LLMCallerBase
from ame.foundation.storage import VectorStoreBase
from ame.retrieval.factory import RetrieverFactory
from ame.capabilities.memory import ConversationFilter


class MimicEngine:
    """模仿引擎 - 让 AI 用你的方式说话"""
    
    def __init__(
        self,
        llm_caller: LLMCallerBase,
        vector_store: VectorStoreBase,
        enable_filter: bool = True
    ):
        """
        初始化模仿引擎
        
        Args:
            llm_caller: LLM 调用器
            vector_store: 向量存储实例
            enable_filter: 是否启用对话过滤
        """
        self.llm_caller = llm_caller
        
        # 使用传入的向量存储
        self.vector_store = vector_store
        
        # 创建检索器（更注重时间和关键词）
        self.retriever = RetrieverFactory.create_retriever(
            retriever_type="hybrid",
            vector_store=self.vector_store,
            vector_weight=0.4,
            keyword_weight=0.4,
            time_weight=0.2
        )
        
        # 创建对话过滤器（v0.1.0 新增）
        self.filter = ConversationFilter(llm_caller) if enable_filter else None
    
    async def learn_from_conversation(
        self,
        user_message: str,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        从用户对话中学习（集成对话过滤）
        
        Args:
            user_message: 用户消息
            context: 对话上下文
            metadata: 元数据
            
        Returns:
            retention_type: 记忆保留类型（如果过滤器启用）
        """
        from datetime import datetime
        
        # v0.1.0: 对话过滤 - 判断是否需要存储
        retention_type = None
        if self.filter:
            retention_type = await self.filter.classify_conversation(
                user_message, 
                context={"context": context, **(metadata or {})}
            )
            
            # 如果是闲聊，不存储
            if not self.filter.should_store(retention_type):
                return retention_type
        
        # 构建学习数据
        doc = {
            "content": user_message,
            "source": "user_conversation",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "context": context or "",
                "retention_type": retention_type.value if retention_type else "permanent",
                **(metadata or {})
            }
        }
        
        # 存储到记忆库
        await self.vector_store.add_documents([doc])
        
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
            生成的回复
        """
        # 检索相关的历史对话
        relevant_history = []
        if use_history:
            results = await self.retriever.retrieve(
                query=prompt,
                top_k=5
            )
            relevant_history = [r.to_dict() for r in results]
        
        # 构建系统提示词
        system_prompt = self._build_mimic_prompt(relevant_history)
        
        # 生成回复
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm_caller.generate(
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
            生成的文本片段
        """
        # 检索相关的历史对话
        relevant_history = []
        if use_history:
            results = await self.retriever.retrieve(
                query=prompt,
                top_k=5
            )
            relevant_history = [r.to_dict() for r in results]
        
        # 构建系统提示词
        system_prompt = self._build_mimic_prompt(relevant_history)
        
        # 流式生成回复
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        async for chunk in self.llm_caller.generate_stream(
            messages=messages,
            temperature=temperature
        ):
            yield chunk
    
    async def generate_styled_text(
        self,
        template: str,
        data: Dict[str, Any],
        tone: str = "casual",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成用户风格的文本（支持多模板）
        
        Args:
            template: 模板类型（weekly_report/daily_report/todo_list/mood_support）
            data: 数据字典
            tone: 语气风格（professional/casual/warm）
            context: 上下文信息
            
        Returns:
            生成的文本
        """
        # 检索相关的历史对话
        relevant_history = []
        query = f"{template} {tone}"
        results = await self.retriever.retrieve(query=query, top_k=3)
        relevant_history = [r.to_dict() for r in results]
        
        # 根据模板构建提示词
        system_prompt = self._build_template_prompt(template, tone, relevant_history)
        
        # 构建用户提示词
        user_prompt = self._format_template_data(template, data, context)
        
        # 生成文本
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.llm_caller.generate(
            messages=messages,
            temperature=0.7 if tone == "warm" else 0.5
        )
        
        return response.content
    
    def _build_mimic_prompt(self, relevant_history: List[Dict]) -> str:
        """
        构建模仿提示词（增强版）
        
        算法优化：
        1. 风格学习：从历史对话中提取语言风格特征
        2. 个性化：第一人称“我”表达
        3. 风格保持：保留用户惯用词汇和句式
        """
        prompt = """你是用户的 AI 分身，任务是用用户的风格和方式回答问题。

**重要事项**：
1. 用第一人称“我”来表达，而不是“用户”或“他/她”
2. 模仿用户的说话风格、惯用词汇和表达习惯
3. 保持真实感，不要过于形式化
4. 如果不确定，可以说“我不太确定”或“我需要想想”
"""
        
        if relevant_history:
            prompt += "\n**参考用户的历史表达**（学习风格）：\n"
            for i, h in enumerate(relevant_history[:3], 1):
                content = h.get('content', '')[:150]
                prompt += f"{i}. {content}...\n"
            prompt += "\n请模仿上述表达风格来回答。\n"
        
        return prompt
    
    def _build_template_prompt(self, template: str, tone: str, history: List[Dict]) -> str:
        """构建模板提示词"""
        
        # 基础风格描述
        tone_descriptions = {
            "professional": "专业、简洁、条理清晰",
            "casual": "轻松、自然、接地气",
            "warm": "温暖、关怀、鼓励"
        }
        
        tone_desc = tone_descriptions.get(tone, "自然、真诚")
        
        # 模板特定指导
        template_guides = {
            "weekly_report": "生成工作周报，包含关键任务、成就、挑战等内容。使用 Markdown 格式。",
            "daily_report": "生成工作日报，总结今天的工作进展和明日计划。使用 Markdown 格式。",
            "todo_list": "整理待办事项，按优先级分组，每项任务简洁明确。使用 Markdown 格式。",
            "mood_support": "分析心情并提供情绪支持，语气要温暖、共情、鼓励。使用 Markdown 格式。"
        }
        
        template_guide = template_guides.get(template, "生成相关内容")
        
        # 构建提示词
        prompt = f"""你是用户的 AI 分身，任务是：{template_guide}

**语气风格**: {tone_desc}

**注意事项**:
1. 用第一人称“我”来表达
2. 保持{tone_desc}的语气
3. 使用 Markdown 格式输出
4. 不要过于形式化，保持真实感
"""
        
        # 添加历史参考
        if history:
            examples = "\n".join([f"- {h['content'][:80]}..." for h in history[:2]])
            prompt += f"\n**参考用户的历史表达**:\n{examples}\n"
        
        return prompt
    
    def _format_template_data(self, template: str, data: Dict[str, Any], context: Optional[Dict]) -> str:
        """格式化模板数据"""
        
        if template == "weekly_report":
            return f"""请生成本周的工作周报：

**时间范围**: {context.get('period', '未知') if context else '未知'}
**工作记录数**: {context.get('total_logs', 0) if context else 0}

**关键任务**: 
{self._format_list(data.get('key_tasks', []))}

**成就**: 
{self._format_list(data.get('achievements', []))}

**挑战**: 
{self._format_list(data.get('challenges', []))}

请以 Markdown 格式生成完整的周报。
"""
        
        elif template == "mood_support":
            return f"""请分析以下心情并提供支持：

**情绪类型**: {data.get('emotion', {}).get('type', '未知')}
**情绪强度**: {data.get('emotion', {}).get('intensity', 0.5) * 10:.1f}/10
**触发因素**: {', '.join(data.get('triggers', [])) or '未知'}
**趋势**: {data.get('trend', {}).get('trend_direction', '稳定') if data.get('trend') else '稳定'}

请以温暖、关怀的语气，提供 2-3 条具体的建议。
"""
        
        else:
            # 默认格式
            return f"""请根据以下数据生成内容：

{str(data)}
"""
    
    def _format_list(self, items: List) -> str:
        """格式化列表"""
        if not items:
            return "无"
        
        result = ""
        for item in items[:5]:
            if isinstance(item, dict):
                result += f"- {item.get('entity', item.get('content', '未知'))}\n"
            else:
                result += f"- {str(item)}\n"
        return result
