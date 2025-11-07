/**
 * 工作场景相关类型定义
 */

/** 周报生成请求 */
export interface WeeklyReportRequest {
  start_date?: string;
  end_date?: string;
}

/** 时间统计 */
export interface TimeStats {
  total_hours: number;
  breakdown: Record<string, number>;
}

/** 周报生成响应 */
export interface WeeklyReportResponse {
  success: boolean;
  report: string;
  insights?: {
    key_tasks?: string[];
    achievements?: string[];
    challenges?: string[];
    time_stats?: TimeStats;
  };
  timestamp: string;
}

/** 待办事项 */
export interface TodoItem {
  id: string;
  title: string;
  description?: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed';
  deadline?: string;
  dependencies?: string[];
  created_at: string;
}

/** 待办整理请求 */
export interface OrganizeTodosRequest {
  todos: string[];
}

/** 待办整理响应 */
export interface TodoOrganizeResponse {
  success: boolean;
  high_priority: TodoItem[];
  medium_priority: TodoItem[];
  low_priority: TodoItem[];
  statistics: {
    total: number;
    completed: number;
    pending: number;
  };
  timestamp: string;
}

/** 会议总结请求 */
export interface MeetingSummaryRequest {
  meeting_notes: string;
  meeting_info?: {
    title?: string;
    date?: string;
    participants?: string[];
  };
}

/** 会议总结响应 */
export interface MeetingSummaryResponse {
  success: boolean;
  summary: string;
  key_points?: string[];
  decisions?: string[];
  action_items?: string[];
  timestamp: string;
}

/** 项目进度请求 */
export interface ProjectProgressRequest {
  project_name: string;
}

/** 项目进度响应 */
export interface ProjectProgressResponse {
  success: boolean;
  project_name: string;
  progress_report: string;
  milestones?: Array<{
    name: string;
    status: string;
    completion: number;
  }>;
  timestamp: string;
}
