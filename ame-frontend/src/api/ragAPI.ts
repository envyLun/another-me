/**
 * 知识库 API 客户端（增强版）
 */
import axios, { AxiosInstance } from 'axios';
import type {
  BaseResponse,
  UploadResponse,
  SearchResponse,
  RAGStats,
  DocumentInfo,
  DocumentDetail,
  PaginatedResponse,
} from '@/types';

class RAGAPIClient {
  private axios: AxiosInstance;

  constructor() {
    this.axios = axios.create({
      baseURL: '/api/v1/rag',
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * 上传文档
   */
  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.axios.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * 搜索知识
   */
  async searchKnowledge(query: string, topK: number = 5): Promise<SearchResponse> {
    const response = await this.axios.post<SearchResponse>('/search', {
      query,
      top_k: topK,
    });
    return response.data;
  }

  /**
   * 获取文档列表（分页）
   */
  async getDocuments(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<DocumentInfo>> {
    const response = await this.axios.get<PaginatedResponse<DocumentInfo>>('/documents', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  /**
   * 获取文档详情
   */
  async getDocumentDetail(docId: string): Promise<DocumentDetail> {
    const response = await this.axios.get<DocumentDetail>(`/documents/${docId}`);
    return response.data;
  }

  /**
   * 删除文档
   */
  async deleteDocument(docId: string): Promise<BaseResponse> {
    const response = await this.axios.delete<BaseResponse>(`/documents/${docId}`);
    return response.data;
  }

  /**
   * 获取RAG统计信息
   */
  async getStats(): Promise<RAGStats> {
    const response = await this.axios.get<RAGStats>('/stats');
    return response.data;
  }

  /**
   * 批量删除文档
   */
  async batchDeleteDocuments(docIds: string[]): Promise<BaseResponse> {
    const response = await this.axios.post<BaseResponse>('/documents/batch-delete', {
      document_ids: docIds,
    });
    return response.data;
  }
}

export const ragAPI = new RAGAPIClient();
export default ragAPI;
