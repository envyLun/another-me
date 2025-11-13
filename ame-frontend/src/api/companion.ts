import apiClient from './client';

// 消息类型定义
export interface CompanionMessage {
  type: 'user' | 'ai';
  content: string;
  attachments?: Array<{
    name: string;
    type: string;
    url?: string;
    fileId?: string;
  }>;
  timestamp: number;
}

// 发送消息请求参数
export interface SendMessageParams {
  content: string;
  attachments?: Array<{
    name: string;
    type: string;
    fileId: string;
  }>;
}

// 上传文件响应
export interface UploadFileResponse {
  success: boolean;
  fileId: string;
  name: string;
  type: string;
  url?: string;
}

/**
 * 陪伴模式API服务
 */
const companionService = {
  /**
   * 发送消息
   */
  async sendMessage(params: SendMessageParams): Promise<CompanionMessage> {
    try {
      // 实际项目中应该调用真实的后端API
      // const response = await apiClient.post('/companion/message', params);
      // return response.data;
      
      // 模拟API响应
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        type: 'ai',
        content: `我收到了你的消息: "${params.content}"
${params.attachments?.length ? `以及 ${params.attachments.length} 个附件` : ''}`,
        timestamp: Date.now(),
      };
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  },

  /**
   * 上传文件
   */
  async uploadFile(file: File): Promise<UploadFileResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // 实际项目中应该调用真实的后端API
      // const response = await apiClient.post('/companion/upload', formData, {
      //   headers: {
      //     'Content-Type': 'multipart/form-data',
      //   },
      // });
      // return response.data;
      
      // 模拟API响应
      await new Promise(resolve => setTimeout(resolve, 800));
      
      return {
        success: true,
        fileId: `file_${Date.now()}`,
        name: file.name,
        type: file.type || 'application/octet-stream',
        url: URL.createObjectURL(file),
      };
    } catch (error) {
      console.error('Failed to upload file:', error);
      throw error;
    }
  },

  /**
   * 获取历史消息
   */
  async getHistoryMessages(limit: number = 20): Promise<CompanionMessage[]> {
    try {
      // 实际项目中应该调用真实的后端API
      // const response = await apiClient.get(`/companion/history?limit=${limit}`);
      // return response.data;
      
      // 返回空数组作为模拟
      return [];
    } catch (error) {
      console.error('Failed to get history messages:', error);
      return [];
    }
  },
};

export default companionService;
