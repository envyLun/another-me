import { Card, Descriptions, Tag, Empty, Typography } from 'antd';
import { SmileOutlined, MehOutlined, FrownOutlined } from '@ant-design/icons';

const { Paragraph, Text } = Typography;

interface AnalysisResultProps {
  title: string;
  data: any;
  type?: 'mood' | 'interests' | 'summary' | 'general';
}

/**
 * 分析结果展示组件
 * 美化显示各类分析数据
 */
export function AnalysisResult({ title, data, type = 'general' }: AnalysisResultProps) {
  if (!data) {
    return (
      <Card title={title}>
        <Empty description="暂无数据" />
      </Card>
    );
  }

  // 心情分析展示
  if (type === 'mood') {
    const moodIcon = {
      happy: <SmileOutlined style={{ fontSize: 24, color: '#52c41a' }} />,
      neutral: <MehOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
      sad: <FrownOutlined style={{ fontSize: 24, color: '#ff4d4f' }} />,
    };

    return (
      <Card title={title}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          {moodIcon[data.mood as keyof typeof moodIcon] || moodIcon.neutral}
          <div style={{ marginTop: 8, fontSize: 18, fontWeight: 'bold' }}>
            {data.mood_label || '中性'}
          </div>
        </div>
        
        <Descriptions column={1}>
          {data.mood_score && (
            <Descriptions.Item label="心情评分">
              <Text strong>{data.mood_score}</Text>
            </Descriptions.Item>
          )}
          {data.analysis && (
            <Descriptions.Item label="分析">
              <Paragraph>{data.analysis}</Paragraph>
            </Descriptions.Item>
          )}
          {data.suggestions && Array.isArray(data.suggestions) && (
            <Descriptions.Item label="建议">
              {data.suggestions.map((suggestion: string, index: number) => (
                <div key={index} style={{ marginBottom: 4 }}>• {suggestion}</div>
              ))}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>
    );
  }

  // 兴趣追踪展示
  if (type === 'interests') {
    return (
      <Card title={title}>
        {data.interests && Array.isArray(data.interests) && (
          <div style={{ marginBottom: 16 }}>
            <Text strong style={{ marginBottom: 8, display: 'block' }}>兴趣爱好</Text>
            <div>
              {data.interests.map((interest: any, index: number) => (
                <Tag key={index} color="blue" style={{ marginBottom: 8 }}>
                  {interest.name || interest} 
                  {interest.count && ` (${interest.count}次)`}
                </Tag>
              ))}
            </div>
          </div>
        )}
        
        {data.summary && (
          <Paragraph>{data.summary}</Paragraph>
        )}
      </Card>
    );
  }

  // 生活总结展示
  if (type === 'summary') {
    return (
      <Card title={title}>
        <Descriptions column={1} bordered>
          {Object.entries(data).map(([key, value]) => {
            if (typeof value === 'object' && value !== null) {
              return (
                <Descriptions.Item key={key} label={formatLabel(key)}>
                  <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                    {JSON.stringify(value, null, 2)}
                  </pre>
                </Descriptions.Item>
              );
            }
            return (
              <Descriptions.Item key={key} label={formatLabel(key)}>
                {String(value)}
              </Descriptions.Item>
            );
          })}
        </Descriptions>
      </Card>
    );
  }

  // 通用展示
  return (
    <Card title={title}>
      <Descriptions column={1} bordered>
        {Object.entries(data).map(([key, value]) => (
          <Descriptions.Item key={key} label={formatLabel(key)}>
            {typeof value === 'object' ? (
              <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                {JSON.stringify(value, null, 2)}
              </pre>
            ) : (
              String(value)
            )}
          </Descriptions.Item>
        ))}
      </Descriptions>
    </Card>
  );
}

/**
 * 格式化字段名
 */
function formatLabel(key: string): string {
  const labelMap: Record<string, string> = {
    mood: '心情',
    mood_score: '心情评分',
    mood_label: '心情标签',
    analysis: '分析',
    suggestions: '建议',
    interests: '兴趣',
    summary: '摘要',
    period: '时间段',
    start_date: '开始日期',
    end_date: '结束日期',
  };

  return labelMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}
