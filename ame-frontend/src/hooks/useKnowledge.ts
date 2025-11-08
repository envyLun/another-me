/**
 * 知识库管理Hook
 */
import { useKnowledgeStore } from '@/store';
import { useEffect } from 'react';

export function useKnowledge() {
  const store = useKnowledgeStore();

  useEffect(() => {
    // 初始化时加载数据
    store.loadDocuments();
    store.loadStats();
  }, []);

  return {
    // 数据
    documents: store.documents,
    stats: store.stats,
    searchResults: store.searchResults,
    selectedDocument: store.selectedDocument,
    
    // 状态
    loading: store.loading,
    uploading: store.uploading,
    searching: store.searching,
    error: store.error,
    
    // 分页
    currentPage: store.currentPage,
    pageSize: store.pageSize,
    total: store.total,
    
    // 操作
    loadDocuments: store.loadDocuments,
    loadDocumentDetail: store.loadDocumentDetail,
    uploadDocument: store.uploadDocument,
    deleteDocument: store.deleteDocument,
    searchKnowledge: store.searchKnowledge,
    clearSearch: store.clearSearch,
  };
}
