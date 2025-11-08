/**
 * 记忆管理页面（完整版）
 */
import { useState } from 'react';
import {
  Card,
  Tabs,
  Timeline,
  Tag,
  Input,
  Space,
  Button,
  Row,
  Col,
  Popconfirm,
  message,
} from 'antd';
import {
  ClockCircleOutlined,
  SearchOutlined,
  DeleteOutlined,
  ExportOutlined,
  FilterOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons';
import { useMemory } from '@/hooks';
import { StatCard, EmptyState } from '@/components/common';
import { formatRelativeTime, formatEmotionToEmoji } from '@/utils';
import type { MemoryItem } from '@/types';

const { Search } = Input;

export default function MemoryPage() {
  const {
    memories,
    timeline,
    loading,
    total,
    searchMemories,
    deleteMemory,
    exportMemories,
    clearFilters,
  } = useMemory();

  const [viewMode, setViewMode] = useState<'timeline' | 'list'>('timeline');

  // 处理搜索
  const handleSearch = async (value: string) => {
    if (value.trim()) {
      await searchMemories(value);
    } else {
      clearFilters();
    }
  };

  // 处理删除
  const handleDelete = async (memoryId: string) => {
    try {
      await deleteMemory(memoryId);
      message.success('删除成功');
    } catch (error: any) {
      message.error(`删除失败: ${error.message}`);
    }
  };

  // 处理导出
  const handleExport = async (format: 'json' | 'csv') => {
    try {
      await exportMemories(format);
      message.success(`导出${format.toUpperCase()}成功`);
    } catch (error: any) {
      message.error(`导出失败: ${error.message}`);
    }
  };

  // 渲染时间线视图
  const renderTimeline = () => {
    if (timeline.length === 0) {
      return (
        <EmptyState
          title="暂无记忆"
          description="还没有记录任何记忆，开始对话或记录日记吧"
        />
      );
    }

    return (
      <div>
        {timeline.map((node) => (
          <div key={node.date} style={{ marginBottom: 32 }}>
            <h3 style={{ marginBottom: 16, color: '#1890ff' }}>
              📅 {node.date}
            </h3>
            <Timeline>
              {node.events.map((memory: MemoryItem) => (
                <Timeline.Item
                  key={memory.id}
                  color={memory.emotion ? 'blue' : 'gray'}
                >
                  <Card
                    size="small"
                    style={{ marginBottom: 8 }}
                    extra={
                      <Popconfirm
                        title="确认删除此记忆？"
                        onConfirm={() => handleDelete(memory.id)}
                        okText="确认"
                        cancelText="取消"
                      >
                        <Button
                          type="text"
                          size="small"
                          danger
                          icon={<DeleteOutlined />}
                        />
                      </Popconfirm>
                    }
                  >
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div>
                        {memory.emotion && (
                          <span style={{ marginRight: 8, fontSize: '18px' }}>
                            {formatEmotionToEmoji(memory.emotion)}
                          </span>
                        )}
                        <span>{memory.content}</span>
                      </div>
                      <div>
                        <Space size="small" wrap>
                          <Tag color="blue">
                            {formatRelativeTime(memory.timestamp)}
                          </Tag>
                          {memory.category && (
                            <Tag color="green">{memory.category}</Tag>
                          )}
                          {memory.tags?.map((tag) => (
                            <Tag key={tag}>{tag}</Tag>
                          ))}
                          {(memory.importance || 0) > 0.7 && (
                            <Tag color="red">重要</Tag>
                          )}
                        </Space>
                      </div>
                    </Space>
                  </Card>
                </Timeline.Item>
              ))}
            </Timeline>
          </div>
        ))}
      </div>
    );
  };

  // 渲染列表视图
  const renderList = () => {
    if (memories.length === 0) {
      return (
        <EmptyState
          title="暂无记忆"
          description="还没有记录任何记忆，开始对话或记录日记吧"
        />
      );
    }

    return (
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {memories.map((memory) => (
          <Card
            key={memory.id}
            size="small"
            extra={
              <Popconfirm
                title="确认删除此记忆？"
                onConfirm={() => handleDelete(memory.id)}
                okText="确认"
                cancelText="取消"
              >
                <Button
                  type="text"
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                />
              </Popconfirm>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                {memory.emotion && (
                  <span style={{ marginRight: 8, fontSize: '18px' }}>
                    {formatEmotionToEmoji(memory.emotion)}
                  </span>
                )}
                <span>{memory.content}</span>
              </div>
              <div>
                <Space size="small" wrap>
                  <Tag color="blue">
                    {formatRelativeTime(memory.timestamp)}
                  </Tag>
                  {memory.category && (
                    <Tag color="green">{memory.category}</Tag>
                  )}
                  {memory.tags?.map((tag) => (
                    <Tag key={tag}>{tag}</Tag>
                  ))}
                  {(memory.importance || 0) > 0.7 && <Tag color="red">重要</Tag>}
                </Space>
              </div>
            </Space>
          </Card>
        ))}
      </Space>
    );
  };

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>
          <ClockCircleOutlined style={{ marginRight: 8 }} />
          记忆管理
        </h1>
        <p style={{ margin: '8px 0 0', color: '#666' }}>
          查看和管理您的所有记忆，回顾过去的精彩时刻
        </p>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <StatCard
            title="总记忆数"
            value={total}
            icon={<ClockCircleOutlined />}
            color="#1890ff"
            suffix="条"
          />
        </Col>
        <Col xs={24} sm={8}>
          <StatCard
            title="本周新增"
            value={0}
            icon="📅"
            color="#52c41a"
            suffix="条"
          />
        </Col>
        <Col xs={24} sm={8}>
          <StatCard
            title="重要记忆"
            value={memories.filter((m) => (m.importance || 0) > 0.7).length}
            icon="⭐"
            color="#fa8c16"
            suffix="条"
          />
        </Col>
      </Row>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space
          style={{ width: '100%', justifyContent: 'space-between' }}
          wrap
        >
          <Space wrap>
            <Search
              placeholder="搜索记忆..."
              allowClear
              enterButton={<SearchOutlined />}
              style={{ width: 300 }}
              onSearch={handleSearch}
              loading={loading}
            />
            <Button icon={<FilterOutlined />}>过滤</Button>
          </Space>

          <Space>
            <Button
              icon={<ExportOutlined />}
              onClick={() => handleExport('json')}
            >
              导出JSON
            </Button>
            <Button
              icon={<ExportOutlined />}
              onClick={() => handleExport('csv')}
            >
              导出CSV
            </Button>
          </Space>
        </Space>
      </Card>

      {/* 主内容区 */}
      <Card>
        <Tabs
          activeKey={viewMode}
          onChange={(key) => setViewMode(key as 'timeline' | 'list')}
          items={[
            {
              key: 'timeline',
              label: (
                <span>
                  <ClockCircleOutlined /> 时间线
                </span>
              ),
              children: renderTimeline(),
            },
            {
              key: 'list',
              label: (
                <span>
                  <UnorderedListOutlined /> 列表
                </span>
              ),
              children: renderList(),
            },
          ]}
        />
      </Card>
    </div>
  );
}
