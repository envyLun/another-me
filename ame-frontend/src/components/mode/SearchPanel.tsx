import { useState } from 'react';
import { Card, Input, List, Tag, Typography, Spin, Empty, Button, Space, Collapse } from 'antd';
import { SearchOutlined, FileTextOutlined, ThunderboltOutlined } from '@ant-design/icons';
import apiClient from '@/api/client';

const { Search } = Input;
const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

import type { SearchResult as APISearchResult } from '@/types/api';

interface SearchResult extends APISearchResult {
  id: string;
  similarity: number;
}

interface SearchPanelProps {
  onResultClick?: (result: SearchResult) => void;
}

/**
 * 知识库检索面板
 * 支持语义搜索和结果预览
 */
export function SearchPanel({ onResultClick }: SearchPanelProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTime, setSearchTime] = useState<number>(0);

  const handleSearch = async (searchQuery?: string) => {
    const q = searchQuery || query;
    
    if (!q.trim()) {
      return;
    }

    setLoading(true);
    const startTime = Date.now();

    try {
      const response = await apiClient.searchKnowledge(q.trim(), 5);
      const endTime = Date.now();
      
      setResults((response.results || []).map(r => ({
        id: r.metadata?.doc_id || Math.random().toString(),
        content: r.content,
        similarity: r.score,
        score: r.score,
        metadata: r.metadata
      })));
      setSearchTime(endTime - startTime);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSearch = (quickQuery: string) => {
    setQuery(quickQuery);
    handleSearch(quickQuery);
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.8) return 'green';
    if (similarity >= 0.6) return 'blue';
    if (similarity >= 0.4) return 'orange';
    return 'default';
  };

  const quickSearches = [
    '如何使用RAG',
    '记忆模仿原理',
    '配置API Key',
    '上传文档',
  ];

  return (
    <Card title={
      <Space>
        <SearchOutlined />
        知识检索
      </Space>
    }>
      <Search
        placeholder="输入问题，搜索知识库..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onSearch={handleSearch}
        enterButton="搜索"
        size="large"
        loading={loading}
        disabled={loading}
        style={{ marginBottom: 16 }}
      />

      {/* 快捷搜索 */}
      {results.length === 0 && !loading && (
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary" style={{ marginBottom: 8, display: 'block' }}>
            快捷搜索:
          </Text>
          <Space wrap>
            {quickSearches.map((quickQuery, index) => (
              <Tag
                key={index}
                icon={<ThunderboltOutlined />}
                color="processing"
                style={{ cursor: 'pointer' }}
                onClick={() => handleQuickSearch(quickQuery)}
              >
                {quickQuery}
              </Tag>
            ))}
          </Space>
        </div>
      )}

      {/* 加载状态 */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" tip="搜索中..." />
        </div>
      )}

      {/* 搜索结果 */}
      {!loading && results.length > 0 && (
        <>
          <div style={{ marginBottom: 12 }}>
            <Text type="secondary">
              找到 {results.length} 条相关结果 ({searchTime}ms)
            </Text>
          </div>

          <List
            dataSource={results}
            renderItem={(item, index) => (
              <List.Item
                style={{ cursor: 'pointer' }}
                onClick={() => onResultClick?.(item)}
              >
                <Card
                  size="small"
                  hoverable
                  style={{ width: '100%' }}
                  title={
                    <Space>
                      <FileTextOutlined />
                      <Text>结果 {index + 1}</Text>
                      <Tag color={getSimilarityColor(item.similarity)}>
                        相似度: {(item.similarity * 100).toFixed(1)}%
                      </Tag>
                    </Space>
                  }
                >
                  <Paragraph
                    ellipsis={{ rows: 3, expandable: true, symbol: '展开' }}
                    style={{ marginBottom: 8 }}
                  >
                    {item.content}
                  </Paragraph>

                  {item.metadata && (
                    <Space size="small" wrap>
                      {item.metadata.source && (
                        <Tag icon={<FileTextOutlined />}>
                          {item.metadata.source}
                        </Tag>
                      )}
                      {item.metadata.page && (
                        <Tag>第 {item.metadata.page} 页</Tag>
                      )}
                      {item.metadata.timestamp && (
                        <Tag>
                          {new Date(item.metadata.timestamp).toLocaleDateString()}
                        </Tag>
                      )}
                    </Space>
                  )}
                </Card>
              </List.Item>
            )}
          />
        </>
      )}

      {/* 空状态 */}
      {!loading && results.length === 0 && query && (
        <Empty
          description="未找到相关内容"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary" onClick={() => setQuery('')}>
            重新搜索
          </Button>
        </Empty>
      )}

      {/* 搜索提示 */}
      {!loading && results.length === 0 && !query && (
        <Collapse ghost style={{ marginTop: 16 }}>
          <Panel header="💡 搜索技巧" key="1">
            <ul style={{ paddingLeft: 20 }}>
              <li>使用完整的问题或关键词进行搜索</li>
              <li>支持语义搜索，理解问题的含义而非仅匹配关键词</li>
              <li>可以使用自然语言提问，如"如何配置API Key?"</li>
              <li>尝试使用不同的表达方式以获得更好的结果</li>
            </ul>
          </Panel>
        </Collapse>
      )}
    </Card>
  );
}
