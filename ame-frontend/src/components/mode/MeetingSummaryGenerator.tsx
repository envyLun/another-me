import { useState } from 'react';
import { Modal, Input, Button, Typography, message, Space, Tag, Divider } from 'antd';
import { FileTextOutlined } from '@ant-design/icons';
import { workAPI } from '@/api';

const { TextArea } = Input;
const { Text, Title, Paragraph } = Typography;

interface MeetingSummaryGeneratorProps {
  visible: boolean;
  onClose: () => void;
  onGenerated?: (summary: string) => void;
}

interface SummaryResult {
  success: boolean;
  summary: string;
  key_points?: string[];
  action_items?: string[];
  decisions?: string[];
  next_steps?: string[];
}

/**
 * 会议总结生成器组件
 * 根据会议记录生成结构化总结
 */
export function MeetingSummaryGenerator({ 
  visible, 
  onClose,
  onGenerated,
}: MeetingSummaryGeneratorProps) {
  const [meetingNotes, setMeetingNotes] = useState('');
  const [meetingTitle, setMeetingTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SummaryResult | null>(null);

  const handleGenerate = async () => {
    if (!meetingNotes.trim()) {
      message.warning('请输入会议记录');
      return;
    }

    setLoading(true);
    
    try {
      const response = await workAPI.summarizeMeeting({
        meeting_notes: meetingNotes,
        meeting_info: meetingTitle ? { title: meetingTitle } : undefined,
      });

      setResult(response);
      message.success('会议总结生成完成！');
    } catch (error: any) {
      console.error('生成失败:', error);
      message.error(error.response?.data?.detail || '生成失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setMeetingNotes('');
    setMeetingTitle('');
    setResult(null);
  };

  const handleCopy = () => {
    if (result) {
      navigator.clipboard.writeText(result.summary);
      message.success('已复制到剪贴板');
    }
  };

  const handleFinish = () => {
    if (result) {
      onGenerated?.(result.summary);
    }
    handleReset();
    onClose();
  };

  return (
    <Modal
      title="📝 会议总结生成器"
      open={visible}
      onCancel={onClose}
      width={800}
      footer={null}
      destroyOnClose
    >
      {!result ? (
        <div>
          <div style={{ marginBottom: 16 }}>
            <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
              会议标题（可选）：
            </Text>
            <Input
              value={meetingTitle}
              onChange={(e) => setMeetingTitle(e.target.value)}
              placeholder="例如：产品规划会议"
              style={{ marginBottom: 16 }}
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
              会议记录：
            </Text>
            <TextArea
              value={meetingNotes}
              onChange={(e) => setMeetingNotes(e.target.value)}
              placeholder="请输入会议记录内容，包括讨论的主题、要点、决策等..."
              rows={12}
            />
          </div>

          <Space>
            <Button 
              type="primary" 
              icon={<FileTextOutlined />}
              onClick={handleGenerate} 
              loading={loading}
            >
              生成总结
            </Button>
            <Button onClick={onClose}>取消</Button>
          </Space>
        </div>
      ) : (
        <div>
          <div style={{ marginBottom: 24 }}>
            {meetingTitle && (
              <Title level={4} style={{ marginBottom: 16 }}>
                {meetingTitle}
              </Title>
            )}

            <div style={{ 
              background: '#f5f5f5', 
              padding: 16, 
              borderRadius: 8,
              marginBottom: 16,
            }}>
              <Paragraph style={{ whiteSpace: 'pre-wrap', marginBottom: 0 }}>
                {result.summary}
              </Paragraph>
            </div>

            {result.key_points && result.key_points.length > 0 && (
              <>
                <Divider orientation="left">📌 关键要点</Divider>
                <ul>
                  {result.key_points.map((point, index) => (
                    <li key={index}><Text>{point}</Text></li>
                  ))}
                </ul>
              </>
            )}

            {result.decisions && result.decisions.length > 0 && (
              <>
                <Divider orientation="left">✅ 决策事项</Divider>
                <ul>
                  {result.decisions.map((decision, index) => (
                    <li key={index}><Text strong>{decision}</Text></li>
                  ))}
                </ul>
              </>
            )}

            {result.action_items && result.action_items.length > 0 && (
              <>
                <Divider orientation="left">🎯 行动项</Divider>
                <ul>
                  {result.action_items.map((item, index) => (
                    <li key={index}>
                      <Tag color="blue">{item}</Tag>
                    </li>
                  ))}
                </ul>
              </>
            )}

            {result.next_steps && result.next_steps.length > 0 && (
              <>
                <Divider orientation="left">➡️ 下一步</Divider>
                <ul>
                  {result.next_steps.map((step, index) => (
                    <li key={index}><Text>{step}</Text></li>
                  ))}
                </ul>
              </>
            )}
          </div>

          <Space>
            <Button type="primary" onClick={handleFinish}>
              完成
            </Button>
            <Button onClick={handleCopy}>
              复制
            </Button>
            <Button onClick={handleReset}>
              重新生成
            </Button>
            <Button onClick={onClose}>
              取消
            </Button>
          </Space>
        </div>
      )}
    </Modal>
  );
}
