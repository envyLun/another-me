import { useState, useEffect } from 'react';
import { Input, Button, Select, Space, Card, Row, Col, Statistic, message } from 'antd';
import { SearchOutlined, ApartmentOutlined, BarChartOutlined } from '@ant-design/icons';
import { GraphVisualization } from '@/components/common';
import { graphAPI, type GraphData, type GraphStatsResponse } from '@/api';
import { handleError } from '@/utils/errorHandler';
import { spacing } from '@/styles/theme';

const { Search } = Input;

export default function GraphPage() {
  const [loading, setLoading] = useState(false);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [stats, setStats] = useState<GraphStatsResponse | null>(null);
  const [searchType, setSearchType] = useState<'entity' | 'document' | 'overview'>('overview');
  const [depth, setDepth] = useState(2);

  // 加载图谱统计信息
  useEffect(() => {
    loadStats();
    loadOverview();
  }, []);

  const loadStats = async () => {
    try {
      const data = await graphAPI.getGraphStats();
      setStats(data);
    } catch (error) {
      handleError(error, '加载统计信息失败');
    }
  };

  const loadOverview = async () => {
    setLoading(true);
    try {
      const response = await graphAPI.getGraphOverview(100);
      if (response.success) {
        setGraphData(response.data);
      }
    } catch (error) {
      handleError(error, '加载图谱概览失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (value: string) => {
    if (!value.trim()) {
      message.warning('请输入搜索内容');
      return;
    }

    setLoading(true);
    try {
      if (searchType === 'entity') {
        const response = await graphAPI.getEntityGraph(value, depth);
        if (response.success) {
          setGraphData(response.data);
          message.success(`找到 ${response.data.nodes.length} 个相关节点`);
        }
      } else if (searchType === 'document') {
        const response = await graphAPI.getDocumentGraph(value, depth);
        if (response.success) {
          setGraphData(response.data);
          message.success(`找到 ${response.related_docs.length} 个相关文档`);
        }
      }
    } catch (error) {
      handleError(error, '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* 页面标题和统计 */}
      <div style={{ marginBottom: spacing.lg }}>
        <h2>
          <ApartmentOutlined /> 知识图谱
        </h2>
        
        {stats && (
          <Row gutter={16} style={{ marginTop: spacing.md }}>
            <Col span={6}>
              <Card>
                <Statistic
                  title="总节点数"
                  value={stats.total_nodes}
                  prefix={<ApartmentOutlined />}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="总关系数"
                  value={stats.total_edges}
                  prefix={<BarChartOutlined />}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="节点类型"
                  value={Object.keys(stats.node_types).length}
                  suffix="种"
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="关系类型"
                  value={Object.keys(stats.edge_types).length}
                  suffix="种"
                />
              </Card>
            </Col>
          </Row>
        )}
      </div>

      {/* 搜索控件 */}
      <Card style={{ marginBottom: spacing.md }}>
        <Space.Compact style={{ width: '100%' }}>
          <Select
            value={searchType}
            onChange={setSearchType}
            style={{ width: 150 }}
            options={[
              { label: '全局概览', value: 'overview' },
              { label: '实体搜索', value: 'entity' },
              { label: '文档搜索', value: 'document' },
            ]}
          />
          
          <Select
            value={depth}
            onChange={setDepth}
            style={{ width: 120 }}
            disabled={searchType === 'overview'}
            options={[
              { label: '深度: 1', value: 1 },
              { label: '深度: 2', value: 2 },
              { label: '深度: 3', value: 3 },
            ]}
          />

          {searchType === 'overview' ? (
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={loadOverview}
              loading={loading}
              style={{ flex: 1 }}
            >
              刷新概览
            </Button>
          ) : (
            <Search
              placeholder={
                searchType === 'entity'
                  ? '输入实体名称，如：机器学习'
                  : '输入文档 ID'
              }
              enterButton="搜索"
              size="middle"
              onSearch={handleSearch}
              loading={loading}
              style={{ flex: 1 }}
            />
          )}
        </Space.Compact>

        <div style={{ marginTop: spacing.sm, fontSize: 12, color: '#666' }}>
          💡 提示：
          {searchType === 'overview' && ' 显示全局知识图谱概览（限制 100 个节点）'}
          {searchType === 'entity' && ' 搜索特定实体及其关联节点'}
          {searchType === 'document' && ' 搜索文档及其相关文档'}
        </div>
      </Card>

      {/* 图谱可视化 */}
      <GraphVisualization
        data={graphData}
        loading={loading}
        title="知识图谱可视化"
      />

      {/* 节点类型分布（如果有统计数据） */}
      {stats && stats.node_types && Object.keys(stats.node_types).length > 0 && (
        <Card
          title={<span><BarChartOutlined /> 节点类型分布</span>}
          style={{ marginTop: spacing.md }}
        >
          <Row gutter={[16, 16]}>
            {Object.entries(stats.node_types).map(([type, count]) => (
              <Col key={type} span={6}>
                <Statistic title={type} value={count} />
              </Col>
            ))}
          </Row>
        </Card>
      )}
    </div>
  );
}
