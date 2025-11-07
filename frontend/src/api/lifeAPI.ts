/**
 * 生活场景 API 客户端
 */
import axios, { AxiosInstance } from 'axios';
import type {
  MoodAnalysisRequest,
  MoodAnalysisResponse,
  InterestTrackingResponse,
  LifeSummaryRequest,
  LifeSummaryResponse,
  LifeSuggestionsRequest,
  LifeSuggestionsResponse,
  RecordLifeEventRequest,
  RecordLifeEventResponse,
} from '@/types';

class LifeAPIClient {
  private axios: AxiosInstance;

  constructor() {
    this.axios = axios.create({
      baseURL: '/api/v1/life',
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * 分析心情日记
   */
  async analyzeMood(request: MoodAnalysisRequest): Promise<MoodAnalysisResponse> {
    const response = await this.axios.post<MoodAnalysisResponse>('/analyze-mood', request);
    return response.data;
  }

  /**
   * 追踪兴趣爱好
   */
  async trackInterests(periodDays: number = 30): Promise<InterestTrackingResponse> {
    const response = await this.axios.get<InterestTrackingResponse>('/track-interests', {
      params: { period_days: periodDays },
    });
    return response.data;
  }

  /**
   * 生成生活总结
   */
  async generateLifeSummary(request: LifeSummaryRequest): Promise<LifeSummaryResponse> {
    const response = await this.axios.post<LifeSummaryResponse>('/life-summary', request);
    return response.data;
  }

  /**
   * 获取生活建议
   */
  async getLifeSuggestions(request: LifeSuggestionsRequest = {}): Promise<LifeSuggestionsResponse> {
    const response = await this.axios.post<LifeSuggestionsResponse>('/suggestions', request);
    return response.data;
  }

  /**
   * 记录生活事件
   */
  async recordLifeEvent(request: RecordLifeEventRequest): Promise<RecordLifeEventResponse> {
    const response = await this.axios.post<RecordLifeEventResponse>('/record-event', request);
    return response.data;
  }
}

export const lifeAPI = new LifeAPIClient();
export default lifeAPI;
