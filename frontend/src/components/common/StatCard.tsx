/**
 * 统计卡片组件
 */
import { Card, Statistic } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, MinusOutlined } from '@ant-design/icons';
import React from 'react';

interface StatCardProps {
  title: string;
  value: number | string;
  icon?: React.ReactNode;
  color?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
  suffix?: string;
  prefix?: string;
  loading?: boolean;
  onClick?: () => void;
}

export function StatCard({
  title,
  value,
  icon,
  color = '#1890ff',
  trend,
  trendValue,
  suffix,
  prefix,
  loading = false,
  onClick,
}: StatCardProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <ArrowUpOutlined style={{ color: '#52c41a' }} />;
      case 'down':
        return <ArrowDownOutlined style={{ color: '#ff4d4f' }} />;
      case 'stable':
        return <MinusOutlined style={{ color: '#faad14' }} />;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return '#52c41a';
      case 'down':
        return '#ff4d4f';
      case 'stable':
        return '#faad14';
      default:
        return color;
    }
  };

  return (
    <Card 
      hoverable={!!onClick} 
      onClick={onClick}
      loading={loading}
      style={{ height: '100%' }}
    >
      <Statistic
        title={title}
        value={value}
        prefix={
          icon ? (
            <span style={{ color, fontSize: '24px', marginRight: '8px' }}>
              {icon}
            </span>
          ) : prefix
        }
        suffix={suffix}
        valueStyle={{ color }}
      />
      {trend && trendValue && (
        <div style={{ marginTop: '8px', fontSize: '14px', color: getTrendColor() }}>
          {getTrendIcon()} {trendValue}
        </div>
      )}
    </Card>
  );
}
