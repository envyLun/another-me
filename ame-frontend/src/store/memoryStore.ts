/**
 * 记忆状态管理
 */
import { create } from 'zustand';
import type { Memory, MemoryItem, TimelineNode } from '@/types';
import { memAPI } from '@/api';

interface MemoryState {
  // 数据
  memories: Memory[];
  selectedMemory: Memory | null;
  timeline: TimelineNode[];

  // UI状态
  loading: boolean;
  error: string | null;

  // 过滤条件
  filters: {
    dateRange?: { start: string; end: string };
    emotion?: string;
    category?: string;
    searchQuery?: string;
  };

  // 分页
  currentPage: number;
  pageSize: number;
  total: number;

  // 操作
  loadMemories: (limit?: number, offset?: number) => Promise<void>;
  searchMemories: (query: string) => Promise<void>;
  deleteMemory: (memoryId: string) => Promise<void>;
  exportMemories: (format?: 'json' | 'csv') => Promise<void>;
  setFilters: (filters: Partial<MemoryState['filters']>) => void;
  clearFilters: () => void;
  setError: (error: string | null) => void;
  
  // 时间线相关
  loadTimeline: () => void;
}

export const useMemoryStore = create<MemoryState>((set, get) => ({
  // 初始状态
  memories: [],
  selectedMemory: null,
  timeline: [],
  loading: false,
  error: null,
  filters: {},
  currentPage: 1,
  pageSize: 50,
  total: 0,

  // 加载记忆列表
  loadMemories: async (limit?: number, offset?: number) => {
    set({ loading: true, error: null });
    try {
      const response = await memAPI.getMemories(
        limit || get().pageSize,
        offset || (get().currentPage - 1) * get().pageSize
      );
      
      set({
        memories: response.memories,
        total: response.total,
        loading: false,
      });

      // 自动构建时间线
      get().loadTimeline();
    } catch (error: any) {
      set({
        error: error.message || '加载记忆失败',
        loading: false,
      });
    }
  },

  // 搜索记忆
  searchMemories: async (query: string) => {
    if (!query.trim()) {
      await get().loadMemories();
      return;
    }

    set({ loading: true, error: null });
    try {
      const response = await memAPI.searchMemories(query);
      set({
        memories: response.memories,
        total: response.total,
        loading: false,
      });
      
      get().loadTimeline();
    } catch (error: any) {
      set({
        error: error.message || '搜索记忆失败',
        loading: false,
      });
    }
  },

  // 删除记忆
  deleteMemory: async (memoryId: string) => {
    set({ loading: true, error: null });
    try {
      await memAPI.deleteMemory(memoryId);
      
      // 重新加载列表
      await get().loadMemories();
      
      set({ loading: false });
    } catch (error: any) {
      set({
        error: error.message || '删除记忆失败',
        loading: false,
      });
      throw error;
    }
  },

  // 导出记忆
  exportMemories: async (format: 'json' | 'csv' = 'json') => {
    set({ loading: true, error: null });
    try {
      const blob = await memAPI.exportMemories(format);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `memories_${new Date().toISOString()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      set({ loading: false });
    } catch (error: any) {
      set({
        error: error.message || '导出记忆失败',
        loading: false,
      });
      throw error;
    }
  },

  // 设置过滤条件
  setFilters: (filters: Partial<MemoryState['filters']>) => {
    set({
      filters: { ...get().filters, ...filters },
    });
  },

  // 清除过滤条件
  clearFilters: () => {
    set({ filters: {} });
    get().loadMemories();
  },

  // 设置错误信息
  setError: (error: string | null) => {
    set({ error });
  },

  // 构建时间线
  loadTimeline: () => {
    const memories = get().memories;
    
    // 按日期分组
    const grouped = memories.reduce((acc, memory) => {
      const date = new Date(memory.timestamp).toISOString().split('T')[0];
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(memory as any);
      return acc;
    }, {} as Record<string, MemoryItem[]>);

    // 转换为时间线节点，按日期倒序
    const timeline: TimelineNode[] = Object.entries(grouped)
      .map(([date, events]) => ({
        date,
        events: events.sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        ),
      }))
      .sort((a, b) => b.date.localeCompare(a.date));

    set({ timeline });
  },
}));
