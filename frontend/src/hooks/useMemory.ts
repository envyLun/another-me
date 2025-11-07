/**
 * 记忆管理Hook
 */
import { useMemoryStore } from '@/store';
import { useEffect } from 'react';

export function useMemory() {
  const store = useMemoryStore();

  useEffect(() => {
    // 初始化时加载数据
    store.loadMemories();
  }, []);

  return {
    // 数据
    memories: store.memories,
    timeline: store.timeline,
    selectedMemory: store.selectedMemory,
    
    // 状态
    loading: store.loading,
    error: store.error,
    
    // 过滤
    filters: store.filters,
    
    // 分页
    currentPage: store.currentPage,
    pageSize: store.pageSize,
    total: store.total,
    
    // 操作
    loadMemories: store.loadMemories,
    searchMemories: store.searchMemories,
    deleteMemory: store.deleteMemory,
    exportMemories: store.exportMemories,
    setFilters: store.setFilters,
    clearFilters: store.clearFilters,
  };
}
