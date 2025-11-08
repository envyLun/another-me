import { useState } from 'react';
import { Modal, Input, Button, List, Tag, Space, Typography, message, Divider } from 'antd';
import { CheckCircleOutlined, ClockCircleOutlined, FireOutlined } from '@ant-design/icons';
import { workAPI } from '@/api';

const { TextArea } = Input;
const { Text, Title } = Typography;

interface TodoItem {
  id: string;
  content: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
  estimatedTime?: string;
  dependencies?: string[];
}

interface OrganizedTodos {
  high: TodoItem[];
  medium: TodoItem[];
  low: TodoItem[];
  categories: Record<string, TodoItem[]>;
}

interface TodoOrganizerProps {
  visible: boolean;
  onClose: () => void;
  onOrganized?: (todos: OrganizedTodos) => void;
}

/**
 * 待办整理组件
 * 智能分析待办事项并进行分类和优先级排序
 */
export function TodoOrganizer({ visible, onClose, onOrganized }: TodoOrganizerProps) {
  const [rawInput, setRawInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OrganizedTodos | null>(null);

  const handleOrganize = async () => {
    if (!rawInput.trim()) {
      message.warning('请输入待办事项');
      return;
    }

    setLoading(true);
    
    try {
      // 调用后端 API
      const todos = rawInput.split('\n').filter(line => line.trim());
      const response = await workAPI.organizeTodos({ todos });
      
      // 将 API 响应转换为组件需要的格式
      if (response.success) {
        const organized: OrganizedTodos = {
          high: response.high_priority.map(item => ({
            id: item.id,
            content: item.title,
            priority: 'high',
            category: item.description || '工作',
            estimatedTime: undefined,
          })),
          medium: response.medium_priority.map(item => ({
            id: item.id,
            content: item.title,
            priority: 'medium',
            category: item.description || '工作',
            estimatedTime: undefined,
          })),
          low: response.low_priority.map(item => ({
            id: item.id,
            content: item.title,
            priority: 'low',
            category: item.description || '工作',
            estimatedTime: undefined,
          })),
          categories: {}, // 简化处理
        };
        
        setResult(organized);
        message.success('整理完成！');
      } else {
        throw new Error('整理失败');
      }
    } catch (error: any) {
      console.error('整理失败:', error);
      message.error(error.response?.data?.detail || error.message || '整理失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setRawInput('');
    setResult(null);
  };

  const handleFinish = () => {
    if (result) {
      onOrganized?.(result);
    }
    handleReset();
    onClose();
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'red';
      case 'medium': return 'orange';
      case 'low': return 'blue';
      default: return 'default';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <FireOutlined />;
      case 'medium': return <ClockCircleOutlined />;
      case 'low': return <CheckCircleOutlined />;
      default: return null;
    }
  };

  return (
    <Modal
      title="✅ 智能待办整理"
      open={visible}
      onCancel={onClose}
      width={800}
      footer={null}
      destroyOnClose
    >
      {!result ? (
        <div>
          <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
            请输入你的待办事项，每行一个任务，AI 将帮你智能分类和排序：
          </Text>
          <TextArea
            value={rawInput}
            onChange={(e) => setRawInput(e.target.value)}
            placeholder="例如：&#10;完成季度报告&#10;修复生产环境Bug&#10;更新项目文档&#10;整理邮箱"
            rows={10}
            style={{ marginBottom: 16 }}
          />
          <Space>
            <Button type="primary" onClick={handleOrganize} loading={loading}>
              开始整理
            </Button>
            <Button onClick={onClose}>取消</Button>
          </Space>
        </div>
      ) : (
        <div>
          {/* 按优先级展示 */}
          <div style={{ marginBottom: 24 }}>
            <Title level={5}>📌 按优先级排序</Title>
            
            {result.high.length > 0 && (
              <>
                <Divider orientation="left" orientationMargin={0}>
                  <Tag color="red" icon={<FireOutlined />}>高优先级</Tag>
                </Divider>
                <List
                  size="small"
                  dataSource={result.high}
                  renderItem={(item) => (
                    <List.Item>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text strong>{item.content}</Text>
                        <Space>
                          <Tag color={getPriorityColor(item.priority)}>
                            {getPriorityIcon(item.priority)} {item.priority.toUpperCase()}
                          </Tag>
                          <Tag>{item.category}</Tag>
                          {item.estimatedTime && <Tag color="cyan">⏱ {item.estimatedTime}</Tag>}
                        </Space>
                      </Space>
                    </List.Item>
                  )}
                />
              </>
            )}

            {result.medium.length > 0 && (
              <>
                <Divider orientation="left" orientationMargin={0}>
                  <Tag color="orange" icon={<ClockCircleOutlined />}>中优先级</Tag>
                </Divider>
                <List
                  size="small"
                  dataSource={result.medium}
                  renderItem={(item) => (
                    <List.Item>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text>{item.content}</Text>
                        <Space>
                          <Tag color={getPriorityColor(item.priority)}>
                            {getPriorityIcon(item.priority)} {item.priority.toUpperCase()}
                          </Tag>
                          <Tag>{item.category}</Tag>
                          {item.estimatedTime && <Tag color="cyan">⏱ {item.estimatedTime}</Tag>}
                        </Space>
                      </Space>
                    </List.Item>
                  )}
                />
              </>
            )}

            {result.low.length > 0 && (
              <>
                <Divider orientation="left" orientationMargin={0}>
                  <Tag color="blue" icon={<CheckCircleOutlined />}>低优先级</Tag>
                </Divider>
                <List
                  size="small"
                  dataSource={result.low}
                  renderItem={(item) => (
                    <List.Item>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text type="secondary">{item.content}</Text>
                        <Space>
                          <Tag color={getPriorityColor(item.priority)}>
                            {getPriorityIcon(item.priority)} {item.priority.toUpperCase()}
                          </Tag>
                          <Tag>{item.category}</Tag>
                          {item.estimatedTime && <Tag color="cyan">⏱ {item.estimatedTime}</Tag>}
                        </Space>
                      </Space>
                    </List.Item>
                  )}
                />
              </>
            )}
          </div>

          <Space>
            <Button type="primary" onClick={handleFinish}>
              完成
            </Button>
            <Button onClick={handleReset}>
              重新整理
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
