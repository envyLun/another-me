/**
 * 操作卡片组件
 */
import { Card, Button } from 'antd';
import { RightOutlined } from '@ant-design/icons';
import React from 'react';

interface ActionCardProps {
  title: string;
  description: string;
  icon: string | React.ReactNode;
  onClick: () => void;
  loading?: boolean;
  disabled?: boolean;
  color?: string;
}

export function ActionCard({
  title,
  description,
  icon,
  onClick,
  loading = false,
  disabled = false,
  color = '#1890ff',
}: ActionCardProps) {
  return (
    <Card
      hoverable={!disabled}
      onClick={disabled ? undefined : onClick}
      style={{
        height: '100%',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.6 : 1,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
        <div
          style={{
            fontSize: '32px',
            color,
            flexShrink: 0,
          }}
        >
          {typeof icon === 'string' ? icon : icon}
        </div>
        
        <div style={{ flex: 1 }}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: 600 }}>
            {title}
          </h3>
          <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
            {description}
          </p>
        </div>
        
        <Button
          type="text"
          icon={<RightOutlined />}
          loading={loading}
          disabled={disabled}
          style={{ flexShrink: 0 }}
        />
      </div>
    </Card>
  );
}
