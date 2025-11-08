import { useEffect, useRef } from 'react';
import { Card, Avatar, Typography, Space, Spin } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage } from '@/hooks/useStreamChat';

const { Text } = Typography;

interface MessageListProps {
  messages: ChatMessage[];
  streaming?: boolean;
}

/**
 * 聊天消息列表组件
 * 支持用户和AI消息的区分展示，自动滚动到底部
 */
export function MessageList({ messages, streaming = false }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streaming]);

  if (messages.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px', color: '#999' }}>
        <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
        <p>开始对话吧！我会像你一样思考和表达。</p>
      </div>
    );
  }

  return (
    <div style={{ maxHeight: '600px', overflowY: 'auto', padding: '16px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {messages.map((msg) => (
          <MessageItem key={msg.id} message={msg} />
        ))}
        {streaming && <TypingIndicator />}
      </Space>
      <div ref={messagesEndRef} />
    </div>
  );
}

/**
 * 单条消息组件
 */
function MessageItem({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        gap: 12,
      }}
    >
      {!isUser && (
        <Avatar
          icon={<RobotOutlined />}
          style={{ backgroundColor: '#1890ff', flexShrink: 0 }}
        />
      )}
      
      <Card
        size="small"
        style={{
          maxWidth: '70%',
          backgroundColor: isUser ? '#1890ff' : '#f5f5f5',
          color: isUser ? '#fff' : '#000',
          borderRadius: 12,
        }}
        bodyStyle={{ padding: '12px 16px' }}
      >
        {isUser ? (
          <Text style={{ color: '#fff' }}>{message.content}</Text>
        ) : (
          <div className="markdown-content">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.6 }}>
          {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </Card>
      
      {isUser && (
        <Avatar
          icon={<UserOutlined />}
          style={{ backgroundColor: '#52c41a', flexShrink: 0 }}
        />
      )}
    </div>
  );
}

/**
 * 打字指示器
 */
function TypingIndicator() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <Avatar
        icon={<RobotOutlined />}
        style={{ backgroundColor: '#1890ff', flexShrink: 0 }}
      />
      <Card
        size="small"
        style={{
          backgroundColor: '#f5f5f5',
          borderRadius: 12,
        }}
        bodyStyle={{ padding: '12px 16px' }}
      >
        <Space>
          <Spin size="small" />
          <Text type="secondary">正在思考...</Text>
        </Space>
      </Card>
    </div>
  );
}
