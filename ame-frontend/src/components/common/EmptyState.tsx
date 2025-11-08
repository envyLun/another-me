/**
 * 空状态占位组件
 */
import { Button } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import React from 'react';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title?: string;
  description?: string;
  action?: {
    text: string;
    onClick: () => void;
    type?: 'default' | 'primary' | 'dashed' | 'link' | 'text';
  };
  image?: React.ReactNode;
}

export function EmptyState({
  icon,
  title = '暂无数据',
  description,
  action,
  image,
}: EmptyStateProps) {
  const defaultIcon = icon || <InboxOutlined style={{ fontSize: '64px', color: '#d9d9d9' }} />;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 24px',
        textAlign: 'center',
      }}
    >
      {image || defaultIcon}
      
      <h3 style={{ marginTop: '16px', fontSize: '16px', color: '#262626' }}>
        {title}
      </h3>
      
      {description && (
        <p style={{ margin: '8px 0 0', fontSize: '14px', color: '#8c8c8c' }}>
          {description}
        </p>
      )}
      
      {action && (
        <Button
          type={action.type || 'primary'}
          onClick={action.onClick}
          style={{ marginTop: '16px' }}
        >
          {action.text}
        </Button>
      )}
    </div>
  );
}

// 预设的空状态场景
export const NoDocuments = (props: Partial<EmptyStateProps>) => (
  <EmptyState
    title="暂无文档"
    description="还没有上传任何文档，立即上传开始构建知识库"
    {...props}
  />
);

export const NoMemories = (props: Partial<EmptyStateProps>) => (
  <EmptyState
    title="暂无记忆"
    description="还没有记录任何记忆，开始对话或记录日记吧"
    {...props}
  />
);

export const NoSearchResults = (props: Partial<EmptyStateProps>) => (
  <EmptyState
    title="未找到相关内容"
    description="尝试使用不同的关键词搜索"
    {...props}
  />
);
