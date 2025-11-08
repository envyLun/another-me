import { useState, useCallback } from 'react';
import apiClient from '@/api/client';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

/**
 * 流式对话 Hook
 * 管理聊天消息和流式响应
 */
export function useStreamChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || streaming) return;

    setError(null);
    
    // 添加用户消息
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);

    // 创建 AI 消息占位
    const aiMsgId = `assistant-${Date.now()}`;
    const aiMsg: ChatMessage = {
      id: aiMsgId,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, aiMsg]);

    setStreaming(true);
    let fullContent = '';

    try {
      await apiClient.chatStream(
        content,
        // onMessage: 接收流式数据块
        (chunk: string) => {
          fullContent += chunk;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMsgId ? { ...msg, content: fullContent } : msg
            )
          );
        },
        // onError: 处理错误
        (err: Error) => {
          console.error('Stream error:', err);
          setError(err.message);
          setStreaming(false);
        },
        // onComplete: 流式完成
        () => {
          setStreaming(false);
        }
      );
    } catch (err) {
      const errorMessage = (err as Error).message || '发送消息失败';
      setError(errorMessage);
      setStreaming(false);
      
      // 移除失败的 AI 消息
      setMessages((prev) => prev.filter((msg) => msg.id !== aiMsgId));
    }
  }, [streaming]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const deleteMessage = useCallback((id: string) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== id));
  }, []);

  return {
    messages,
    streaming,
    error,
    sendMessage,
    clearMessages,
    deleteMessage,
  };
}
