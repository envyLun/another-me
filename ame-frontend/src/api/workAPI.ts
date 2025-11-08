/**
 * 工作场景 API 客户端
 */
import axios, { AxiosInstance } from 'axios';
import type {
  WeeklyReportRequest,
  WeeklyReportResponse,
  OrganizeTodosRequest,
  TodoOrganizeResponse,
  MeetingSummaryRequest,
  MeetingSummaryResponse,
  ProjectProgressRequest,
  ProjectProgressResponse,
} from '@/types';

class WorkAPIClient {
  private axios: AxiosInstance;

  constructor() {
    this.axios = axios.create({
      baseURL: '/api/v1/work',
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * 生成工作周报
   */
  async generateWeeklyReport(request: WeeklyReportRequest = {}): Promise<WeeklyReportResponse> {
    const response = await this.axios.post<WeeklyReportResponse>('/weekly-report', request);
    return response.data;
  }

  /**
   * 智能整理待办事项
   */
  async organizeTodos(request: OrganizeTodosRequest): Promise<TodoOrganizeResponse> {
    const response = await this.axios.post<TodoOrganizeResponse>('/organize-todos', request);
    return response.data;
  }

  /**
   * 总结会议内容
   */
  async summarizeMeeting(request: MeetingSummaryRequest): Promise<MeetingSummaryResponse> {
    const response = await this.axios.post<MeetingSummaryResponse>('/summarize-meeting', request);
    return response.data;
  }

  /**
   * 追踪项目进度
   */
  async trackProjectProgress(request: ProjectProgressRequest): Promise<ProjectProgressResponse> {
    const response = await this.axios.post<ProjectProgressResponse>('/track-project', request);
    return response.data;
  }
}

export const workAPI = new WorkAPIClient();
export default workAPI;
