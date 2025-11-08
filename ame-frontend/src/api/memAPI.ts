/**
 * 记忆 API 客户端（增强版）
 */
import axios, { AxiosInstance } from 'axios';
import type {
  BaseResponse,
  ChatResponse,
  MemoryListResponse,
  MemoryRecallRequest,
  MemoryRecallResponse,
} from '@/types';

class MemAPIClient {
  private axios: AxiosInstance;

  constructor() {
    this.axios = axios.create({
      baseURL: '/api/v1/mem',
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * 同步对话
   */
  async chatSync(message: string): Promise<ChatResponse> {
    const response = await this.axios.post<ChatResponse>('/chat-sync', {
      message,
    });
    return response.data;
  }

  /**
   * 流式对话
   */
  async chatStream(
    message: string,
    onMessage: (chunk: string) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): Promise<void> {
    try {
      const response = await fetch('/api/v1/mem/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          onComplete?.();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              onComplete?.();
              return;
            }
            if (data.startsWith('[ERROR]')) {
              onError?.(new Error(data.slice(8)));
              return;
            }
            onMessage(data);
          }
        }
      }
    } catch (error) {
      onError?.(error as Error);
    }
  }

  /**
   * 从对话中学习
   */
  async learnFromConversation(message: string, context?: string): Promise<BaseResponse> {
    const response = await this.axios.post<BaseResponse>('/learn', {
      message,
      context,
    });
    return response.data;
  }

  /**
   * 获取记忆列表
   */
  async getMemories(limit: number = 100, offset: number = 0): Promise<MemoryListResponse> {
    const response = await this.axios.get<MemoryListResponse>('/memories', {
      params: { limit, offset },
    });
    return response.data;
  }

  /**
   * 搜索记忆
   */
  async searchMemories(query: string, limit: number = 20): Promise<MemoryListResponse> {
    const response = await this.axios.post<MemoryListResponse>('/memories/search', {
      query,
      limit,
    });
    return response.data;
  }

  /**
   * 回顾记忆（语义化呈现）
   */
  async recallMemories(request: MemoryRecallRequest): Promise<MemoryRecallResponse> {
    const response = await this.axios.post<MemoryRecallResponse>('/recall', request);
    return response.data;
  }

  /**
   * 删除记忆
   */
  async deleteMemory(memoryId: string): Promise<BaseResponse> {
    const response = await this.axios.delete<BaseResponse>(`/memories/${memoryId}`);
    return response.data;
  }

  /**
   * 批量删除记忆
   */
  async batchDeleteMemories(memoryIds: string[]): Promise<BaseResponse> {
    const response = await this.axios.post<BaseResponse>('/memories/batch-delete', {
      memory_ids: memoryIds,
    });
    return response.data;
  }

  /**
   * 导出记忆
   */
  async exportMemories(format: 'json' | 'csv' = 'json'): Promise<Blob> {
    const response = await this.axios.get('/memories/export', {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }
}

export const memAPI = new MemAPIClient();
export default memAPI;
