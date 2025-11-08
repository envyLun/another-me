/**
 * UI 状态管理
 * 管理全局 UI 状态，如侧边栏折叠、主题等
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  // 侧边栏状态
  sidebarCollapsed: boolean;
  
  // 主题设置
  theme: 'light' | 'dark';
  
  // 全局loading
  globalLoading: boolean;
  globalLoadingText: string;
  
  // 全局消息提示
  notification: {
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
    description?: string;
  } | null;

  // 操作
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setGlobalLoading: (loading: boolean, text?: string) => void;
  showNotification: (
    type: 'success' | 'error' | 'info' | 'warning',
    message: string,
    description?: string
  ) => void;
  clearNotification: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // 初始状态
      sidebarCollapsed: false,
      theme: 'light',
      globalLoading: false,
      globalLoadingText: '',
      notification: null,

      // 切换侧边栏
      toggleSidebar: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
      },

      // 设置侧边栏状态
      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed });
      },

      // 设置主题
      setTheme: (theme: 'light' | 'dark') => {
        set({ theme });
      },

      // 设置全局loading
      setGlobalLoading: (loading: boolean, text: string = '加载中...') => {
        set({ globalLoading: loading, globalLoadingText: text });
      },

      // 显示通知
      showNotification: (type, message, description) => {
        set({
          notification: { type, message, description },
        });
      },

      // 清除通知
      clearNotification: () => {
        set({ notification: null });
      },
    }),
    {
      name: 'ui-storage',
    }
  )
);
