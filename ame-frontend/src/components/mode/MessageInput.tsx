import { useState, KeyboardEvent } from 'react';
import { Input, Button, Space } from 'antd';
import { SendOutlined, ClearOutlined } from '@ant-design/icons';

const { TextArea } = Input;

interface MessageInputProps {
  onSend: (message: string) => void;
  onClear?: () => void;
  disabled?: boolean;
  placeholder?: string;
}

/**
 * 消息输入组件
 * 支持回车发送、Shift+Enter换行
 */
export function MessageInput({
  onSend,
  onClear,
  disabled = false,
  placeholder = '输入消息... (按 Enter 发送，Shift+Enter 换行)',
}: MessageInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim() || disabled) return;
    
    onSend(input.trim());
    setInput('');
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter 发送，Shift+Enter 换行
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setInput('');
    onClear?.();
  };

  return (
    <div style={{ padding: '16px', borderTop: '1px solid #f0f0f0' }}>
      <Space.Compact style={{ width: '100%' }}>
        <TextArea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          autoSize={{ minRows: 1, maxRows: 4 }}
          style={{ resize: 'none' }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          disabled={disabled || !input.trim()}
        >
          发送
        </Button>
        {onClear && (
          <Button
            icon={<ClearOutlined />}
            onClick={handleClear}
            disabled={disabled}
          >
            清空
          </Button>
        )}
      </Space.Compact>
    </div>
  );
}
