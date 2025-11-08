/**
 * 模式与能力相关类型定义
 */

/** 场景模式 */
export type SceneMode = 'work' | 'life';

/** 能力类型 */
export type CapabilityType = 'mimic' | 'analyze';

/** 模式上下文 */
export interface ModeContext {
  mode: SceneMode;
  capability: CapabilityType;
  timestamp: string;
}

/** 模式配置 */
export interface ModeConfig {
  mode: SceneMode;
  label: string;
  icon: string;
  description: string;
  color: string;
}

/** 能力配置 */
export interface CapabilityConfig {
  type: CapabilityType;
  label: string;
  icon: string;
  description: string;
  actions: ActionConfig[];
}

/** 操作配置 */
export interface ActionConfig {
  key: string;
  label: string;
  icon: string;
  description: string;
  handler: string; // 对应的API方法名
}
