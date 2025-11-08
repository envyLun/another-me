/**
 * 生活模式页面
 */
import { Tabs, Card } from 'antd';
import { useMode } from '@/hooks';
import { ModeSelector, MimicPanel, AnalyzePanel } from '@/components/mode';
import type { CapabilityType } from '@/types';
import { useEffect } from 'react';

export default function LifePage() {
  const { mode, capability, switchMode, switchCapability, modeConfig } = useMode();

  // 确保在生活模式
  useEffect(() => {
    if (mode !== 'life') {
      switchMode('life');
    }
  }, [mode, switchMode]);

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>
          {modeConfig.icon} {modeConfig.label}模式
        </h1>
        <p style={{ margin: '8px 0 0', color: '#666' }}>
          {modeConfig.description}
        </p>
      </div>

      {/* 模式选择器 */}
      <ModeSelector />

      {/* 能力切换标签页 */}
      <Card>
        <Tabs
          activeKey={capability}
          onChange={(key) => switchCapability(key as CapabilityType)}
          items={[
            {
              key: 'mimic',
              label: (
                <span>
                  <span style={{ fontSize: '16px', marginRight: '8px' }}>🤖</span>
                  模仿我
                </span>
              ),
              children: <MimicPanel />,
            },
            {
              key: 'analyze',
              label: (
                <span>
                  <span style={{ fontSize: '16px', marginRight: '8px' }}>🔍</span>
                  分析我
                </span>
              ),
              children: <AnalyzePanel />,
            },
          ]}
        />
      </Card>
    </div>
  );
}
