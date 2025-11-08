/**
 * 生活场景相关类型定义
 */

/** 心情分析请求 */
export interface MoodAnalysisRequest {
  mood_entry: string;
  entry_time?: string;
}

/** 心情分析响应 */
export interface MoodAnalysisResponse {
  success: boolean;
  analysis: string;
  emotion?: string;
  suggestions?: string[];
  timestamp: string;
}

/** 兴趣追踪响应 */
export interface InterestTrackingResponse {
  success: boolean;
  interests: Array<{
    name: string;
    frequency: number;
    trend: 'rising' | 'stable' | 'declining';
  }>;
  summary: string;
  timestamp: string;
}

/** 生活总结请求 */
export interface LifeSummaryRequest {
  period: 'week' | 'month' | 'year';
}

/** 生活总结响应 */
export interface LifeSummaryResponse {
  success: boolean;
  period: string;
  summary: string;
  highlights?: string[];
  insights?: string[];
  timestamp: string;
}

/** 生活建议请求 */
export interface LifeSuggestionsRequest {
  context?: string;
}

/** 生活建议响应 */
export interface LifeSuggestionsResponse {
  success: boolean;
  suggestions: string[];
  reasoning?: string;
  timestamp: string;
}

/** 生活事件记录请求 */
export interface RecordLifeEventRequest {
  event_content: string;
  event_type?: string;
  event_time?: string;
  tags?: string[];
}

/** 生活事件记录响应 */
export interface RecordLifeEventResponse {
  success: boolean;
  event_id: string;
  message: string;
  timestamp: string;
}

/** 聊天请求 */
export interface ChatRequest {
  message: string;
  context?: {
    emotion?: string;
    mode: 'work' | 'life';
  };
}

/** 聊天响应（流式） */
export interface ChatStreamResponse {
  chunk: string;
  done: boolean;
  emotion_detected?: string;
  related_memories?: string[];
}

/** 记忆项 */
export interface MemoryItem {
  id: string;
  content: string;
  timestamp: string;
  emotion?: string;
  importance: number;
  category: string;
  tags: string[];
  metadata: Record<string, any>;
}

/** 时间线节点 */
export interface TimelineNode {
  date: string;
  events: MemoryItem[];
}

/** 记忆回顾请求 */
export interface MemoryRecallRequest {
  query: string;
  time_range?: {
    start: string;
    end: string;
  };
}

/** 记忆回顾响应 */
export interface MemoryRecallResponse {
  success: boolean;
  memories: MemoryItem[];
  presentation: string;
  timeline?: TimelineNode[];
  timestamp: string;
}
