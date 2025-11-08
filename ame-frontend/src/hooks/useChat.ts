/**
 * 对话管理Hook（增强版）
 */
import { useChatStore } from '@/store';
import { useState } from 'react';
import { memAPI } from '@/api';

export function useChat() {
  const store = useChatStore();
  const [streaming, setStreaming] = useState(false);

  const sendStreamMessage = async (message: string) => {
    setStreaming(true);
    
    // 添加用户消息
    store.addMessage({ 
      role: 'user', 
      content: message, 
      timestamp: new Date().toISOString() 
    });
    
    let assistantMessage = '';
    
    // 添加空的助手消息用于流式更新
    store.addMessage({
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString()
    });
    
    await memAPI.chatStream(
      message,
      (chunk) => {
        assistantMessage += chunk;
        // 更新最后一条助手消息
        const messages = store.messages;
        const lastIndex = messages.length - 1;
        if (lastIndex >= 0 && messages[lastIndex].role === 'assistant') {
          store.updateLastMessage(assistantMessage);
        }
      },
      (error) => {
        console.error('Stream error:', error);
        setStreaming(false);
      },
      () => {
        setStreaming(false);
      }
    );
  };

  const sendSyncMessage = async (message: string) => {
    store.setLoading(true);
    
    store.addMessage({ 
      role: 'user', 
      content: message, 
      timestamp: new Date().toISOString() 
    });
    
    try {
      const response = await memAPI.chatSync(message);
      
      store.addMessage({
        role: 'assistant',
        content: response.message,
        timestamp: response.timestamp
      });
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      store.setLoading(false);
    }
  };

  return {
    // 数据
    messages: store.messages,
    
    // 状态
    loading: store.isLoading || streaming,
    streaming,
    
    // 操作
    sendMessage: sendStreamMessage,
    sendSyncMessage,
    clearMessages: store.clearMessages,
    addMessage: store.addMessage,
  };
}
