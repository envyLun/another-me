import { useState } from 'react';
import { Card, Input, Button, Upload, message, Typography, Space, List, Avatar, Spin, Tag } from 'antd';
import { FileOutlined, ImageOutlined, SendOutlined, SmileOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

const { Title, Text } = Typography;
const { TextArea } = Input;

export default function CompanionPage() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{
    type: 'user' | 'ai';
    content: string;
    attachments?: Array<{ name: string; type: string; url?: string }>;
  }>>([]);
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<Array<{ name: string; type: string; url?: string }>>([]);

  // 处理消息发送
  const handleSend = async () => {
    if (!message.trim() && uploadedFiles.length === 0) {
      return;
    }

    // 添加用户消息
    const userMessage = {
      type: 'user' as const,
      content: message,
      attachments: uploadedFiles.length > 0 ? [...uploadedFiles] : undefined,
    };
    setMessages([...messages, userMessage]);
    
    // 清空输入和上传文件
    setMessage('');
    setUploadedFiles([]);
    
    // 模拟AI回复
    setLoading(true);
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 固定回复内容
      const aiResponse = {
        type: 'ai' as const,
        content: '吾既是汝，汝亦是我，镜中映像，心中共鸣',
        attachments: undefined
      };
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Failed to get AI response:', error);
      message.error('获取回复失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 处理文件上传
  const handleUpload: UploadProps['onChange'] = ({ fileList, file }) => {
    if (file.status === 'done') {
      const newFile = {
        name: file.name,
        type: file.type || 'unknown',
        url: URL.createObjectURL(file.originFileObj as File),
      };
      setUploadedFiles([...uploadedFiles, newFile]);
      message.success(`${file.name} 文件上传成功`);
    } else if (file.status === 'error') {
      message.error(`${file.name} 文件上传失败`);
    }
  };

  // 移除附件
  const removeAttachment = (index: number) => {
    const newAttachments = [...uploadedFiles];
    newAttachments.splice(index, 1);
    setUploadedFiles(newAttachments);
  };

  // 上传配置
  const uploadProps: UploadProps = {
    multiple: true,
    beforeUpload: (file) => {
      // 限制文件大小为10MB
      const isLessThan10M = file.size / 1024 / 1024 < 10;
      if (!isLessThan10M) {
        message.error('文件大小不能超过10MB');
      }
      return isLessThan10M;
    },
    onChange: handleUpload,
    showUploadList: false,
    maxCount: 5,
  };

  // 渲染消息项
  const renderMessageItem = (item: typeof messages[0], index: number) => {
    const isUser = item.type === 'user';
    return (
      <div
        key={index}
        style={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          marginBottom: '16px',
          paddingHorizontal: '16px'
        }}
      >
        {!isUser && (
          <Avatar icon={<SmileOutlined />} style={{ marginRight: '8px', alignSelf: 'flex-start' }} />
        )}
        <div
          style={{
            maxWidth: '70%',
            backgroundColor: isUser ? '#1890ff' : '#f0f0f0',
            color: isUser ? 'white' : '#333',
            borderRadius: isUser ? '8px 8px 0 8px' : '8px 8px 8px 0',
            padding: '12px',
            boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
          }}
        >
          {!isUser && (
              <div style={{ fontSize: '12px', marginBottom: '4px', color: !isUser ? '#666' : 'rgba(255,255,255,0.8)' }}>
                  陪伴AI
                </div>
              )}
          <div style={{ wordBreak: 'break-word', lineHeight: '1.5' }}>
            {item.content}
          </div>
          {item.attachments && item.attachments.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              {item.attachments.map((attach, idx) => (
                <Tag
                  key={idx}
                  color={isUser ? 'white' : 'blue'}
                  style={{ 
                    backgroundColor: isUser ? 'rgba(255,255,255,0.2)' : undefined,
                    marginRight: '4px',
                    marginTop: '4px',
                    display: 'inline-block'
                  }}
                >
                  {attach.name}
                </Tag>
              ))}
            </div>
          )}
        </div>
        {isUser && (
          <Avatar icon={<SmileOutlined />} style={{ marginLeft: '8px', alignSelf: 'flex-start' }} />
        )}
      </div>
    );
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', padding: '24px 24px 0' }}>
      <Title level={2}>
        <SmileOutlined /> 陪伴模式
      </Title>
      <Card style={{ flex: 1, display: 'flex', flexDirection: 'column', marginBottom: 0 }}>
        {/* 消息列表 */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 0' }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '32px', color: '#999' }}>
              开始对话吧！
            </div>
          ) : (
            messages.map((item, index) => renderMessageItem(item, index))
          )}
        </div>
        
        {loading && (
          <div style={{ textAlign: 'center', padding: '16px' }}>
            <Spin size="small" />
            <span style={{ marginLeft: '8px' }}>AI正在思考...</span>
          </div>
        )}
      </Card>
      
      {/* 输入区域 - 固定在页面底部 */}
      <div style={{
        backgroundColor: '#fff',
        borderTop: '1px solid #f0f0f0',
        padding: '16px',
        position: 'sticky',
        bottom: 0,
        zIndex: 10
      }}>
        {/* 已上传文件列表 */}
        {uploadedFiles.length > 0 && (
          <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0', marginBottom: '8px' }}>
            <Text type="secondary">已选择的附件: </Text>
            <Space size={[4, 8]} wrap>
              {uploadedFiles.map((file, index) => (
                <Tag key={index} color="blue" closable onClose={() => removeAttachment(index)}>
                  {file.name}
                </Tag>
              ))}
            </Space>
          </div>
        )}
        
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '12px', marginBottom: '8px' }}>
          <TextArea
            rows={3}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="输入你的消息..."
            onPressEnter={(e) => {
              if (e.ctrlKey || e.metaKey) {
                handleSend();
              }
            }}
            maxLength={1000}
            showCount
            style={{ flex: 1, minWidth: 0 }}
          />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <Upload {...uploadProps}>
              <Button icon={<FileOutlined />} style={{ width: '120px' }}>上传文件</Button>
            </Upload>
            <Button 
              type="primary" 
              icon={<SendOutlined />}
              size="large"
              onClick={handleSend}
              disabled={!message.trim() && uploadedFiles.length === 0}
              style={{ width: '120px' }}
            >
              发送
            </Button>
          </div>
        </div>
          
          <Text type="secondary" style={{ fontSize: '12px', display: 'block' }}>
            支持文本、图片、文档等多种格式，按 Ctrl+Enter 快速发送
          </Text>
      </div>
    </div>
  );
}
