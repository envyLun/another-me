import { useState } from 'react';
import { Card, Empty, Spin, Tag, Space, Descriptions, Tabs, List, Badge } from 'antd';
import { NodeIndexOutlined, BranchesOutlined, ApartmentOutlined, LinkOutlined } from '@ant-design/icons';

interface GraphNode {
  id: string;
  label: string;
  type: string; // Entity, Document, etc.
  properties?: Record<string, any>;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string; // MENTIONS, RELATES_TO, etc.
  weight?: number;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface GraphVisualizationProps {
  data: GraphData | null;
  loading?: boolean;
  title?: string;
}

/**
 * 图谱可视化组件
 * 以列表和表格形式展示知识图谱
 */
export function GraphVisualization({
  data,
  loading = false,
  title = '知识图谱',
}: GraphVisualizationProps) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  // 节点类型颜色映射
  const colorMap: Record<string, string> = {
    'Entity': 'blue',
    'Document': 'green',
    'Person': 'orange',
    'Organization': 'red',
    'Location': 'cyan',
    'Topic': 'purple',
  };

  // 节点类型图标映射
  const iconMap: Record<string, string> = {
    'Document': '📄',
    'Person': '👤',
    'Organization': '🏢',
    'Location': '📍',
    'Topic': '💡',
    'Entity': '⚡',
  };

  // 获取节点的关联边
  const getNodeEdges = (nodeId: string) => {
    if (!data) return { incoming: [], outgoing: [] };
    
    const incoming = data.edges.filter(e => e.target === nodeId);
    const outgoing = data.edges.filter(e => e.source === nodeId);
    
    return { incoming, outgoing };
  };

  // 获取节点名称
  const getNodeLabel = (nodeId: string) => {
    const node = data?.nodes.find(n => n.id === nodeId);
    return node?.label || nodeId;
  };

  if (loading) {
    return (
      <Card title={title}>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" tip="加载图谱数据..." />
        </div>
      </Card>
    );
  }

  if (!data || data.nodes.length === 0) {
    return (
      <Card title={title}>
        <Empty description="暂无图谱数据" />
      </Card>
    );
  }

  // 按类型统计节点
  const nodeStats = data.nodes.reduce((acc, node) => {
    acc[node.type] = (acc[node.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <Card
      title={
        <Space>
          <BranchesOutlined />
          {title}
        </Space>
      }
    >
      {/* 统计信息 */}
      <Space style={{ marginBottom: 16 }}>
        <Tag color="blue" icon={<NodeIndexOutlined />}>
          {data.nodes.length} 个节点
        </Tag>
        <Tag color="green" icon={<LinkOutlined />}>
          {data.edges.length} 条关系
        </Tag>
      </Space>

      <Tabs
        defaultActiveKey="nodes"
        items={[
          {
            key: 'nodes',
            label: (
              <span>
                <NodeIndexOutlined /> 节点列表
              </span>
            ),
            children: (
              <div>
                {/* 节点类型统计 */}
                <div style={{ marginBottom: 16 }}>
                  <Space wrap>
                    {Object.entries(nodeStats).map(([type, count]) => (
                      <Tag key={type} color={colorMap[type] || 'default'}>
                        {iconMap[type]} {type}: {count}
                      </Tag>
                    ))}
                  </Space>
                </div>

                {/* 节点列表 */}
                <List
                  dataSource={data.nodes}
                  renderItem={(node) => {
                    const { incoming, outgoing } = getNodeEdges(node.id);
                    const totalEdges = incoming.length + outgoing.length;

                    return (
                      <List.Item
                        key={node.id}
                        style={{
                          cursor: 'pointer',
                          backgroundColor: selectedNode?.id === node.id ? '#f0f5ff' : undefined,
                        }}
                        onClick={() => setSelectedNode(node)}
                      >
                        <List.Item.Meta
                          avatar={
                            <div style={{ fontSize: 24 }}>
                              {iconMap[node.type] || '⚡'}
                            </div>
                          }
                          title={
                            <Space>
                              <Tag color={colorMap[node.type] || 'default'}>
                                {node.type}
                              </Tag>
                              <span>{node.label}</span>
                              <Badge count={totalEdges} showZero style={{ backgroundColor: '#52c41a' }} />
                            </Space>
                          }
                          description={
                            node.properties && Object.keys(node.properties).length > 0 ? (
                              <div style={{ fontSize: 12, color: '#666' }}>
                                {Object.entries(node.properties).slice(0, 2).map(([key, value]) => (
                                  <span key={key} style={{ marginRight: 12 }}>
                                    {key}: {String(value)}
                                  </span>
                                ))}
                              </div>
                            ) : null
                          }
                        />
                      </List.Item>
                    );
                  }}
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    showTotal: (total) => `共 ${total} 个节点`,
                  }}
                />
              </div>
            ),
          },
          {
            key: 'edges',
            label: (
              <span>
                <LinkOutlined /> 关系列表
              </span>
            ),
            children: (
              <List
                dataSource={data.edges}
                renderItem={(edge) => (
                  <List.Item key={`${edge.source}-${edge.target}`}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Space>
                        <Tag color="blue">{getNodeLabel(edge.source)}</Tag>
                        <span>→</span>
                        <Tag color="purple">{edge.type}</Tag>
                        <span>→</span>
                        <Tag color="green">{getNodeLabel(edge.target)}</Tag>
                        {edge.weight !== undefined && (
                          <Tag color="orange">权重: {edge.weight.toFixed(2)}</Tag>
                        )}
                      </Space>
                    </Space>
                  </List.Item>
                )}
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showTotal: (total) => `共 ${total} 条关系`,
                }}
              />
            ),
          },
          {
            key: 'detail',
            label: (
              <span>
                <ApartmentOutlined /> 节点详情
              </span>
            ),
            children: selectedNode ? (
              <div>
                <Descriptions title={selectedNode.label} bordered column={1}>
                  <Descriptions.Item label="ID">{selectedNode.id}</Descriptions.Item>
                  <Descriptions.Item label="类型">
                    <Tag color={colorMap[selectedNode.type] || 'default'}>
                      {selectedNode.type}
                    </Tag>
                  </Descriptions.Item>
                  
                  {selectedNode.properties && Object.entries(selectedNode.properties).map(([key, value]) => (
                    <Descriptions.Item key={key} label={key}>
                      {String(value)}
                    </Descriptions.Item>
                  ))}
                </Descriptions>

                {/* 关联关系 */}
                <div style={{ marginTop: 24 }}>
                  <h4>入边关系 ({getNodeEdges(selectedNode.id).incoming.length})</h4>
                  <List
                    size="small"
                    dataSource={getNodeEdges(selectedNode.id).incoming}
                    renderItem={(edge) => (
                      <List.Item>
                        <Tag color="blue">{getNodeLabel(edge.source)}</Tag>
                        <span>→</span>
                        <Tag color="purple">{edge.type}</Tag>
                        <span>→</span>
                        <Tag color="green">{selectedNode.label}</Tag>
                      </List.Item>
                    )}
                  />
                </div>

                <div style={{ marginTop: 16 }}>
                  <h4>出边关系 ({getNodeEdges(selectedNode.id).outgoing.length})</h4>
                  <List
                    size="small"
                    dataSource={getNodeEdges(selectedNode.id).outgoing}
                    renderItem={(edge) => (
                      <List.Item>
                        <Tag color="blue">{selectedNode.label}</Tag>
                        <span>→</span>
                        <Tag color="purple">{edge.type}</Tag>
                        <span>→</span>
                        <Tag color="green">{getNodeLabel(edge.target)}</Tag>
                      </List.Item>
                    )}
                  />
                </div>
              </div>
            ) : (
              <Empty description="请从节点列表中选择一个节点查看详情" />
            ),
          },
        ]}
      />
    </Card>
  );
}
