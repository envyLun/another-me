"""
心情分析服务
职责: 情绪识别、趋势分析、建议生成
"""
from typing import Dict, List
from datetime import datetime, timedelta

from ame.foundation.nlp.emotion import HybridEmotionDetector
from ame.capabilities.analysis import DataAnalyzer
from ame.capabilities.generation import RAGGenerator
from ame.capabilities.memory import MemoryManager
from ame.models.report_models import MoodAnalysis, MoodTrend


class MoodService:
    """心情分析服务"""
    
    def __init__(
        self,
        emotion_detector: HybridEmotionDetector,
        data_analyzer: DataAnalyzer,
        rag_generator: RAGGenerator,
        memory_manager: MemoryManager
    ):
        self.detector = emotion_detector
        self.analyzer = data_analyzer
        self.generator = rag_generator
        self.memory = memory_manager
    
    async def analyze_mood(
        self,
        mood_entry: str,
        user_id: str,
        entry_time: datetime
    ) -> MoodAnalysis:
        """
        分析心情日记
        
        Args:
            mood_entry: 心情记录
            user_id: 用户ID
            entry_time: 记录时间
        
        Returns:
            MoodAnalysis: 心情分析结果
        """
        # Step 1: 情绪识别
        emotion_result = await self.detector.detect(
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
        
        # Step 4: 生成建议
        suggestions = await self.generator.generate(
            template="mood_support",
            data={
                "emotion": emotion_result,
                "triggers": triggers,
                "trend": mood_trend
            },
            style="warm"
        )
        
        return MoodAnalysis(
            emotion_type=emotion_result["type"],
            emotion_intensity=emotion_result["intensity"],
            triggers=triggers,
            trend=mood_trend,
            suggestions=suggestions,
            analysis_time=datetime.now()
        )
    
    async def _extract_triggers(self, mood_entry: str) -> List[str]:
        """提取情绪触发因素"""
        # TODO: 实现 LLM 提取逻辑
        return []
    
    async def _analyze_mood_trend(
        self,
        user_id: str,
        current_emotion: Dict,
        days: int = 7
    ) -> MoodTrend:
        """分析情绪趋势"""
        start_date = datetime.now() - timedelta(days=days)
        mood_docs = await self.memory.retrieve_by_timerange(
            start_time=start_date,
            end_time=datetime.now(),
            filters={"doc_type": "mood", "user_id": user_id}
        )
        
        historical_emotions = []
        for doc in mood_docs:
            emotion = doc.metadata.get("emotion")
            if emotion:
                historical_emotions.append({
                    "type": emotion.get("type", "neutral"),
                    "intensity": emotion.get("intensity", 0.5),
                    "date": doc.timestamp
                })
        
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
