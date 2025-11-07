/**
 * 知识库状态管理
 */
import { create } from 'zustand';
import type { DocumentInfo, DocumentDetail, SearchResult, RAGStats } from '@/types';
import { ragAPI } from '@/api';

interface KnowledgeState {
  // 数据
  documents: DocumentInfo[];
  selectedDocument: DocumentDetail | null;
  searchResults: SearchResult[];
  stats: RAGStats | null;

  // UI状态
  loading: boolean;
  uploading: boolean;
  searching: boolean;
  error: string | null;

  // 分页
  currentPage: number;
  pageSize: number;
  total: number;

  // 操作
  loadDocuments: (page?: number) => Promise<void>;
  loadDocumentDetail: (docId: string) => Promise<void>;
  uploadDocument: (file: File) => Promise<void>;
  deleteDocument: (docId: string) => Promise<void>;
  searchKnowledge: (query: string, topK?: number) => Promise<void>;
  loadStats: () => Promise<void>;
  clearSearch: () => void;
  setError: (error: string | null) => void;
}

export const useKnowledgeStore = create<KnowledgeState>((set, get) => ({
  // 初始状态
  documents: [],
  selectedDocument: null,
  searchResults: [],
  stats: null,
  loading: false,
  uploading: false,
  searching: false,
  error: null,
  currentPage: 1,
  pageSize: 20,
  total: 0,

  // 加载文档列表
  loadDocuments: async (page?: number) => {
    set({ loading: true, error: null });
    try {
      const currentPage = page || get().currentPage;
      const response = await ragAPI.getDocuments(currentPage, get().pageSize);
      
      set({
        documents: response.data,
        currentPage: response.pagination.page,
        total: response.pagination.total,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || '加载文档列表失败',
        loading: false,
      });
    }
  },

  // 加载文档详情
  loadDocumentDetail: async (docId: string) => {
    set({ loading: true, error: null });
    try {
      const detail = await ragAPI.getDocumentDetail(docId);
      set({
        selectedDocument: detail,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || '加载文档详情失败',
        loading: false,
      });
    }
  },

  // 上传文档
  uploadDocument: async (file: File) => {
    set({ uploading: true, error: null });
    try {
      await ragAPI.uploadDocument(file);
      set({ uploading: false });
      
      // 重新加载文档列表和统计
      await get().loadDocuments(1);
      await get().loadStats();
    } catch (error: any) {
      set({
        error: error.message || '上传文档失败',
        uploading: false,
      });
      throw error;
    }
  },

  // 删除文档
  deleteDocument: async (docId: string) => {
    set({ loading: true, error: null });
    try {
      await ragAPI.deleteDocument(docId);
      
      // 重新加载列表和统计
      await get().loadDocuments();
      await get().loadStats();
      
      set({ loading: false });
    } catch (error: any) {
      set({
        error: error.message || '删除文档失败',
        loading: false,
      });
      throw error;
    }
  },

  // 搜索知识
  searchKnowledge: async (query: string, topK: number = 5) => {
    if (!query.trim()) {
      get().clearSearch();
      return;
    }

    set({ searching: true, error: null });
    try {
      const response = await ragAPI.searchKnowledge(query, topK);
      set({
        searchResults: response.results,
        searching: false,
      });
    } catch (error: any) {
      set({
        error: error.message || '搜索知识失败',
        searching: false,
      });
    }
  },

  // 加载统计信息
  loadStats: async () => {
    try {
      const stats = await ragAPI.getStats();
      set({ stats });
    } catch (error: any) {
      console.error('Failed to load stats:', error);
    }
  },

  // 清除搜索结果
  clearSearch: () => {
    set({ searchResults: [] });
  },

  // 设置错误信息
  setError: (error: string | null) => {
    set({ error });
  },
}));
