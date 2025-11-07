/**
 * 模式管理Hook
 * 提供场景模式和能力类型的便捷操作
 */
import { useModeStore } from '@/store';

export function useMode() {
  const {
    currentMode,
    currentCapability,
    switchMode,
    switchCapability,
    autoDetectMode,
    getModeConfig,
    getCapabilityConfig,
    getAvailableActions,
  } = useModeStore();

  return {
    // 当前状态
    mode: currentMode,
    capability: currentCapability,
    
    // 配置信息
    modeConfig: getModeConfig(),
    capabilityConfig: getCapabilityConfig(),
    availableActions: getAvailableActions(),
    
    // 操作方法
    switchMode,
    switchCapability,
    autoDetectMode,
  };
}
