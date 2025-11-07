/**
 * 模式选择器组件
 * 用于切换工作/生活场景
 */
import { Segmented } from 'antd';
import { useMode } from '@/hooks';
import type { SceneMode } from '@/types';

export function ModeSelector() {
  const { mode, switchMode, modeConfig } = useMode();

  const options = [
    {
      label: (
        <div style={{ padding: '4px 8px' }}>
          <span style={{ fontSize: '18px', marginRight: '8px' }}>💼</span>
          <span>工作</span>
        </div>
      ),
      value: 'work' as SceneMode,
    },
    {
      label: (
        <div style={{ padding: '4px 8px' }}>
          <span style={{ fontSize: '18px', marginRight: '8px' }}>🏡</span>
          <span>生活</span>
        </div>
      ),
      value: 'life' as SceneMode,
    },
  ];

  return (
    <div style={{ marginBottom: '24px' }}>
      <Segmented
        options={options}
        value={mode}
        onChange={(value) => switchMode(value as SceneMode)}
        size="large"
        block
      />
      <div
        style={{
          marginTop: '8px',
          textAlign: 'center',
          color: modeConfig.color,
          fontSize: '14px',
        }}
      >
        {modeConfig.description}
      </div>
    </div>
  );
}
