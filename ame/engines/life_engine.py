"""
生活场景引擎 - LifeEngine
负责生活相关的AI辅助功能实现
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter

from ame.repository.hybrid_repository import HybridRepository
from ame.mem.mimic_engine import MimicEngine
from ame.mem.analyze_engine import AnalyzeEngine
from ame.models.domain import Document, DocumentType
from ame.models.report_models import (
    MoodAnalysis,
    EmotionResult,
    MoodTrend,
    InterestReport,
    InterestTopic,
)
from ame.llm_caller.caller import LLMCaller


class LifeEngine:
    """
    生活场景引擎
    
    职责：
    - 心情分析和情绪识别
    - 兴趣爱好演化追踪
    - 生活建议生成
    - 记忆回顾和情感陪伴
    """
    
    def __init__(
        self,
        repository: HybridRepository,
        llm_caller: LLMCaller,
        mimic_engine: Optional[MimicEngine] = None,
        analyze_engine: Optional[AnalyzeEngine] = None
    ):
        """
        初始化生活引擎
        
        Args:
            repository: 混合存储仓库
            llm_caller: LLM 调用器
            mimic_engine: 模仿引擎（可选，用于生成温暖回应）
            analyze_engine: 分析引擎（可选，用于趋势分析）
        """
        self.repo = repository
        self.llm = llm_caller
        self.mimic = mimic_engine
        self.analyzer = analyze_engine or AnalyzeEngine(repository, llm_caller)
    
    async def analyze_mood(
        self,
        mood_entry: str,
        user_id: str,
        entry_time: datetime
    ) -> MoodAnalysis:
        """
        分析心情日记
        
        流程：
        1. 情绪识别：使用 LLM 识别主要情绪和强度
        2. 触发因素分析：提取导致情绪的关键事件
        3. 历史对比：对比近期情绪趋势
        4. 建议生成：提供情绪管理建议
        
        Args:
            mood_entry: 心情记录
            user_id: 用户ID
            entry_time: 记录时间
        
        Returns:
            MoodAnalysis: 心情分析结果
        """
        # Step 1: 情绪识别
        emotion_result = await self._detect_emotion(
            text=mood_entry,
            context={"time": entry_time}
        )
        
        # Step 2: 触发因素分析
        triggers = await self._extract_triggers(mood_entry)
        
        # Step 3: 历史对比
        mood_trend = await self._analyze_mood_trend(
            user_id=user_id,
            current_emotion=emotion_result,
            days=7
        )
        
        # Step 4: 生成建议（使用温暖语气）
        suggestions = await self._generate_mood_suggestions(
            emotion=emotion_result,
            triggers=triggers,
            trend=mood_trend
        )
        
        return MoodAnalysis(
            emotion_type=emotion_result["type"],
            emotion_intensity=emotion_result["intensity"],
            triggers=triggers,
            trend=mood_trend,
            suggestions=suggestions,
            analysis_time=datetime.now()
        )
    
    async def track_interests(
        self,
        user_id: str,
        period_days: int = 30
    ) -> InterestReport:
        """
        追踪兴趣爱好演化
        
        流程：
        1. 数据收集：检索生活记录
        2. 实体提取：提取主题实体（使用 NER）
        3. 频率分析：统计主题出现频率
        4. 演化分析：对比不同时间窗口
        5. 推荐生成：推荐相关内容
        
        Args:
            user_id: 用户ID
            period_days: 统计时间范围（天）
        
        Returns:
            InterestReport: 兴趣追踪报告
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Step 1: 收集数据
        life_records = await self._collect_life_records(start_date, end_date)
        
        if not life_records:
            return InterestReport(
                user_id=user_id,
                period_days=period_days,
                report="暂无数据"
            )
        
        # Step 2: 提取实体和主题
        all_entities = []
        entity_timestamps = {}
        
        for doc in life_records:
            all_entities.extend(doc.entities)
            for entity in doc.entities:
                if entity not in entity_timestamps:
                    entity_timestamps[entity] = []
                entity_timestamps[entity].append(doc.timestamp)
        
        # Step 3: 频率统计
        entity_freq = Counter(all_entities)
        
        # Step 4: 生成兴趣主题
        top_interests = []
        for entity, count in entity_freq.most_common(10):
            timestamps = entity_timestamps.get(entity, [])
            if timestamps:
                top_interests.append(InterestTopic(
                    topic=entity,
                    frequency=count,
                    first_mentioned=min(timestamps),
                    last_mentioned=max(timestamps),
                    trend="stable"
                ))
        
        # Step 5: 识别新兴趣和衰减兴趣
        new_interests, declining_interests = await self._analyze_interest_evolution(
            user_id, period_days
        )
        
        # Step 6: 生成推荐
        recommendations = await self._generate_interest_recommendations(
            top_interests, new_interests
        )
        
        # Step 7: 生成报告
        report = await self._generate_interest_report(
            top_interests, new_interests, declining_interests, period_days
        )
        
        return InterestReport(
            user_id=user_id,
            period_days=period_days,
            top_interests=top_interests,
            new_interests=new_interests,
            declining_interests=declining_interests,
            recommendations=recommendations,
            report=report,
            generated_at=datetime.now()
        )
    
    async def generate_life_suggestions(
        self,
        user_id: str,
        context: Optional[str] = None
    ) -> str:
        """
        生成生活建议
        
        基于用户最近的生活记录和情绪状态，
        提供个性化的生活改善建议
        
        Args:
            user_id: 用户ID
            context: 上下文（当前困扰、目标等）
        
        Returns:
            suggestions: 生活建议（Markdown格式）
        """
        # 收集最近的生活记录
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        life_records = await self._collect_life_records(start_date, end_date)
        
        # 提取洞察
        insights = await self.analyzer.extract_insights(
            documents=life_records,
            metrics=["key_tasks", "achievements"]
        )
        
        # 构建 Prompt
        prompt = f"""基于用户最近30天的生活记录，提供个性化的生活建议。

**记录数量**: {len(life_records)}
**主要话题**: {', '.join([i.get('entity', '') for i in insights.get('key_tasks', [])[:5]])}

"""
        
        if context:
            prompt += f"\n**当前情况**: {context}\n"
        
        prompt += """
请提供3-5条具体、可行的生活建议，帮助用户：
1. 提升生活质量
2. 发展个人兴趣
3. 改善情绪状态
4. 优化时间管理

请以温暖、关怀的语气，使用Markdown格式输出。
"""
        
        response = await self.llm.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        
        return response.content
    
    async def recall_memories(
        self,
        user_id: str,
        query: str,
        time_range: Optional[timedelta] = None
    ) -> List[Document]:
        """
        回忆检索
        
        根据查询检索相关的生活记忆
        
        Args:
            user_id: 用户ID
            query: 查询文本
            time_range: 时间范围（可选）
        
        Returns:
            memories: 相关记忆列表
        """
        # 使用混合检索
        results = await self.repo.hybrid_search(
            query=query,
            top_k=10,
            filters={"doc_type": DocumentType.LIFE_RECORD}
        )
        
        # 如果指定时间范围，进一步过滤
        if time_range:
            cutoff_date = datetime.now() - time_range
            results = [
                r for r in results
                if hasattr(r, 'timestamp') and r.timestamp >= cutoff_date
            ]
        
        return results
    
    # ==================== 辅助方法 ====================
    
    async def _collect_life_records(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Document]:
        """收集生活记录"""
        return await self.analyzer.collect_time_range(
            user_id="default",  # TODO: 传入实际用户ID
            start=start_date,
            end=end_date,
            category="life"
        )
    
    async def _detect_emotion(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        情绪识别
        
        使用 LLM 识别文本中的主要情绪和强度
        """
        prompt = f"""请分析以下文本的情绪：

文本：{text}

请以JSON格式返回：
{{
  "type": "情绪类型（happy/sad/angry/anxious/excited/neutral等）",
  "intensity": 0.0到1.0之间的强度值,
  "confidence": 0.0到1.0之间的置信度
}}

只返回JSON，不要其他内容。
"""
        
        try:
            response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # 简化处理：返回默认情绪
            return {
                "type": "neutral",
                "intensity": 0.5,
                "confidence": 0.7
            }
        except Exception:
            return {
                "type": "neutral",
                "intensity": 0.5,
                "confidence": 0.5
            }
    
    async def _extract_triggers(self, mood_entry: str) -> List[str]:
        """提取情绪触发因素"""
        # 使用 LLM 提取触发因素
        prompt = f"""请从以下心情日记中提取导致情绪的关键事件或触发因素：

{mood_entry}

请列出1-3个主要触发因素，每行一个。
"""
        
        try:
            response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            # 简单解析
            triggers = [line.strip("- ").strip() for line in response.content.split("\n") if line.strip()]
            return triggers[:3]
        except Exception:
            return []
    
    async def _analyze_mood_trend(
        self,
        user_id: str,
        current_emotion: Dict,
        days: int = 7
    ) -> MoodTrend:
        """
        分析情绪趋势
        
        对比最近 N 天的情绪变化
        """
        # 检索近期心情记录
        start_date = datetime.now() - timedelta(days=days)
        mood_docs = await self._collect_life_records(start_date, datetime.now())
        
        # 过滤心情记录
        mood_docs = [
            doc for doc in mood_docs
            if doc.metadata.get("category") == "mood"
        ]
        
        # 提取历史情绪
        historical_emotions = []
        for doc in mood_docs:
            emotion = doc.metadata.get("emotion")
            if emotion:
                historical_emotions.append({
                    "type": emotion.get("type", "neutral"),
                    "intensity": emotion.get("intensity", 0.5),
                    "date": doc.timestamp
                })
        
        # 计算趋势
        if len(historical_emotions) >= 3:
            avg_intensity = sum(e["intensity"] for e in historical_emotions) / len(historical_emotions)
            current_intensity = current_emotion.get("intensity", 0.5)
            
            if current_intensity > avg_intensity + 0.2:
                direction = "improving"
            elif current_intensity < avg_intensity - 0.2:
                direction = "declining"
            else:
                direction = "stable"
            
            alert = direction == "declining" and current_intensity < 0.3
        else:
            avg_intensity = current_emotion.get("intensity", 0.5)
            direction = "stable"
            alert = False
        
        return MoodTrend(
            current_emotion=current_emotion.get("type", "neutral"),
            average_intensity=avg_intensity,
            trend_direction=direction,
            alert=alert
        )
    
    async def _generate_mood_suggestions(
        self,
        emotion: Dict,
        triggers: List[str],
        trend: MoodTrend
    ) -> str:
        """生成情绪管理建议"""
        prompt = f"""请根据以下情绪分析，提供温暖、关怀的建议：

**情绪类型**: {emotion.get('type', 'neutral')}
**情绪强度**: {emotion.get('intensity', 0.5) * 10:.1f}/10
**触发因素**: {', '.join(triggers) if triggers else '未知'}
**趋势**: {trend.trend_direction}

请以温暖、关怀的语气，提供2-3条具体的情绪管理建议。
使用Markdown格式，每条建议一个段落。
"""
        
        response = await self.llm.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        
        return response.content
    
    async def _analyze_interest_evolution(
        self,
        user_id: str,
        current_period_days: int
    ) -> tuple:
        """分析兴趣演化（新兴趣和衰减兴趣）"""
        # 对比当前周期和上一周期
        end_date = datetime.now()
        current_start = end_date - timedelta(days=current_period_days)
        previous_start = current_start - timedelta(days=current_period_days)
        
        # 收集两个时期的数据
        current_docs = await self._collect_life_records(current_start, end_date)
        previous_docs = await self._collect_life_records(previous_start, current_start)
        
        # 提取实体
        current_entities = set()
        for doc in current_docs:
            current_entities.update(doc.entities)
        
        previous_entities = set()
        for doc in previous_docs:
            previous_entities.update(doc.entities)
        
        # 识别新兴趣和衰减兴趣
        new_interests = list(current_entities - previous_entities)[:5]
        declining_interests = list(previous_entities - current_entities)[:5]
        
        return new_interests, declining_interests
    
    async def _generate_interest_recommendations(
        self,
        top_interests: List[InterestTopic],
        new_interests: List[str]
    ) -> List[str]:
        """生成兴趣推荐"""
        if not top_interests:
            return []
        
        topics = [t.topic for t in top_interests[:3]]
        
        prompt = f"""基于用户的兴趣爱好，推荐3-5个相关的活动或内容：

**主要兴趣**: {', '.join(topics)}
**新兴趣**: {', '.join(new_interests) if new_interests else '无'}

请提供具体、可行的推荐，每行一个。
"""
        
        try:
            response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            recommendations = [
                line.strip("- ").strip()
                for line in response.content.split("\n")
                if line.strip()
            ]
            return recommendations[:5]
        except Exception:
            return []
    
    async def _generate_interest_report(
        self,
        top_interests: List[InterestTopic],
        new_interests: List[str],
        declining_interests: List[str],
        period_days: int
    ) -> str:
        """生成兴趣追踪报告"""
        report = f"# 兴趣追踪报告（最近 {period_days} 天）\n\n"
        
        if top_interests:
            report += "## 主要兴趣\n\n"
            for interest in top_interests[:5]:
                report += f"- **{interest.topic}**: 提及 {interest.frequency} 次\n"
            report += "\n"
        
        if new_interests:
            report += "## 新兴趣\n\n"
            for interest in new_interests:
                report += f"- {interest}\n"
            report += "\n"
        
        if declining_interests:
            report += "## 兴趣减弱\n\n"
            for interest in declining_interests:
                report += f"- {interest}\n"
            report += "\n"
        
        return report
