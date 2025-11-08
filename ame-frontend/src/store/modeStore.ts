/**
 * 模式状态管理
 * 管理工作/生活场景切换和模仿/分析能力切换
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SceneMode, CapabilityType, ModeContext, ModeConfig, CapabilityConfig, ActionConfig } from '@/types';

interface ModeState {
  // 状态
  currentMode: SceneMode;
  currentCapability: CapabilityType;
  history: ModeContext[];

  // 操作
  switchMode: (mode: SceneMode) => void;
  switchCapability: (capability: CapabilityType) => void;
  autoDetectMode: (input: string) => SceneMode;
  resetMode: () => void;

  // 计算属性
  getModeConfig: () => ModeConfig;
  getCapabilityConfig: () => CapabilityConfig;
  getAvailableActions: () => ActionConfig[];
}

// 模式配置常量
const MODE_CONFIGS: Record<SceneMode, ModeConfig> = {
  work: {
    mode: 'work',
    label: '工作',
    icon: '💼',
    description: '效率工具与工作助手',
    color: '#1890ff',
  },
  life: {
    mode: 'life',
    label: '生活',
    icon: '🏡',
    description: '情感陪伴与记忆回顾',
    color: '#52c41a',
  },
};

// 能力配置常量
const CAPABILITY_CONFIGS: Record<CapabilityType, CapabilityConfig> = {
  mimic: {
    type: 'mimic',
    label: '模仿我',
    icon: '🤖',
    description: '学习并模仿你的风格',
    actions: [],
  },
  analyze: {
    type: 'analyze',
    label: '分析我',
    icon: '🔍',
    description: '深度分析与洞察',
    actions: [],
  },
};

// 工作模式 + 模仿能力的操作
const WORK_MIMIC_ACTIONS: ActionConfig[] = [
  {
    key: 'weekly_report',
    label: '周报生成',
    icon: '📊',
    description: '自动生成本周工作总结',
    handler: 'generateWeeklyReport',
  },
  {
    key: 'organize_todos',
    label: '待办整理',
    icon: '✅',
    description: '智能整理待办事项',
    handler: 'organizeTodos',
  },
  {
    key: 'meeting_summary',
    label: '会议总结',
    icon: '📝',
    description: '总结会议内容和行动项',
    handler: 'summarizeMeeting',
  },
];

// 工作模式 + 分析能力的操作
const WORK_ANALYZE_ACTIONS: ActionConfig[] = [
  {
    key: 'project_progress',
    label: '项目进度',
    icon: '📈',
    description: '追踪项目进展情况',
    handler: 'trackProjectProgress',
  },
  {
    key: 'time_analysis',
    label: '时间分析',
    icon: '⏰',
    description: '分析时间使用效率',
    handler: 'analyzeTimeUsage',
  },
];

// 生活模式 + 模仿能力的操作
const LIFE_MIMIC_ACTIONS: ActionConfig[] = [
  {
    key: 'casual_chat',
    label: '闲聊',
    icon: '💬',
    description: '像朋友一样聊天',
    handler: 'casualChat',
  },
  {
    key: 'record_event',
    label: '记录事件',
    icon: '📔',
    description: '记录生活中的重要事件',
    handler: 'recordLifeEvent',
  },
];

// 生活模式 + 分析能力的操作
const LIFE_ANALYZE_ACTIONS: ActionConfig[] = [
  {
    key: 'mood_analysis',
    label: '心情分析',
    icon: '😊',
    description: '分析你的情绪状态',
    handler: 'analyzeMood',
  },
  {
    key: 'interest_tracking',
    label: '兴趣追踪',
    icon: '🎯',
    description: '追踪你的兴趣变化',
    handler: 'trackInterests',
  },
  {
    key: 'life_summary',
    label: '生活总结',
    icon: '📖',
    description: '生成生活总结报告',
    handler: 'generateLifeSummary',
  },
];

export const useModeStore = create<ModeState>()(
  persist(
    (set, get) => ({
      // 初始状态
      currentMode: 'work',
      currentCapability: 'mimic',
      history: [],

      // 切换场景模式
      switchMode: (mode: SceneMode) => {
        const context: ModeContext = {
          mode,
          capability: get().currentCapability,
          timestamp: new Date().toISOString(),
        };
        
        set({
          currentMode: mode,
          history: [...get().history, context],
        });
      },

      // 切换能力类型
      switchCapability: (capability: CapabilityType) => {
        const context: ModeContext = {
          mode: get().currentMode,
          capability,
          timestamp: new Date().toISOString(),
        };
        
        set({
          currentCapability: capability,
          history: [...get().history, context],
        });
      },

      // 自动检测模式（基于用户输入）
      autoDetectMode: (input: string) => {
        const workKeywords = ['周报', '日报', '项目', '任务', '工作', '会议', '待办'];
        const lifeKeywords = ['聊天', '开心', '朋友', '心情', '感觉', '生活'];

        if (workKeywords.some(k => input.includes(k))) {
          get().switchMode('work');
          return 'work';
        } else if (lifeKeywords.some(k => input.includes(k))) {
          get().switchMode('life');
          return 'life';
        }
        
        return get().currentMode;
      },

      // 重置为默认模式
      resetMode: () => {
        set({
          currentMode: 'work',
          currentCapability: 'mimic',
          history: [],
        });
      },

      // 获取当前模式配置
      getModeConfig: () => {
        return MODE_CONFIGS[get().currentMode];
      },

      // 获取当前能力配置
      getCapabilityConfig: () => {
        const capability = get().currentCapability;
        const config = { ...CAPABILITY_CONFIGS[capability] };
        
        // 根据模式和能力设置可用操作
        config.actions = get().getAvailableActions();
        
        return config;
      },

      // 获取当前可用操作
      getAvailableActions: () => {
        const { currentMode, currentCapability } = get();

        if (currentMode === 'work' && currentCapability === 'mimic') {
          return WORK_MIMIC_ACTIONS;
        } else if (currentMode === 'work' && currentCapability === 'analyze') {
          return WORK_ANALYZE_ACTIONS;
        } else if (currentMode === 'life' && currentCapability === 'mimic') {
          return LIFE_MIMIC_ACTIONS;
        } else if (currentMode === 'life' && currentCapability === 'analyze') {
          return LIFE_ANALYZE_ACTIONS;
        }

        return [];
      },
    }),
    {
      name: 'mode-storage',
    }
  )
);
