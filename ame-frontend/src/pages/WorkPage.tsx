/**
 * 工作页面 - 纵向三部分布局
 */
import { Card, Typography, Input, Button, Divider, Space, Table, Tabs } from 'antd';
import { useState } from 'react';

const { Title, Paragraph } = Typography;

export default function WorkPage() {
  const [activeTabKey, setActiveTabKey] = useState('new');
  
  const handleTabChange = (key: string) => {
    setActiveTabKey(key);
  };
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* 简化标题 */}
      <Title level={1} style={{ margin: 0, fontSize: '24px' }}>
        工作模式
      </Title>

      {/* 纵向三部分布局 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* 待办管理 */}
        <Card 
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
              <span style={{ fontSize: '20px' }}>🔄</span>
              <span>待办管理</span>
            </div>
          }
          style={{ 
            minHeight: '320px',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          }}
        >
          <div style={{ padding: '16px 0' }}>
            <Paragraph strong>工作任务跟踪与管理</Paragraph>
            <Paragraph>在此部分您可以查看和管理当前的工作任务。</Paragraph>
            
            <Space direction="vertical" style={{ width: '100%', margin: '16px 0' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <Input placeholder="输入新任务" style={{ flex: 1 }} />
                <Button type="primary">添加任务</Button>
              </div>
              
              <Table 
                columns={[
                  { title: '任务名称', dataIndex: 'name', key: 'name' },
                  { title: '优先级', dataIndex: 'priority', key: 'priority' },
                  { title: '状态', dataIndex: 'status', key: 'status' },
                  { title: '操作', key: 'action', render: () => <Button size="small">编辑</Button> }
                ]}
                dataSource={[
                  { key: '1', name: '完成项目规划', priority: '高', status: '进行中' },
                  { key: '2', name: '准备会议材料', priority: '中', status: '待处理' },
                  { key: '3', name: '更新文档', priority: '低', status: '已完成' }
                ]}
                pagination={false}
                size="small"
              />
            </Space>
          </div>
        </Card>

        {/* 项目拆解 */}
        <Card 
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
              <span style={{ fontSize: '20px' }}>📊</span>
              <span>项目拆解</span>
            </div>
          }
          style={{ 
            minHeight: '280px',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          }}
        >
          <Tabs 
            activeKey={activeTabKey} 
            onChange={handleTabChange}
            items={[
              {
                key: 'new',
                label: '新增',
                children: (
                  <div style={{ padding: '16px 0' }}>
                    <Paragraph strong>数据输入与分析</Paragraph>
                    <Paragraph>在此部分您可以输入数据并进行相关分析处理。</Paragraph>
                    
                    <Space direction="vertical" style={{ width: '100%', margin: '16px 0' }}>
                      <Input placeholder="请输入需要分析的数据" />
                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                        <Button>重置</Button>
                        <Button type="primary">开始分析</Button>
                      </div>
                    </Space>
                    
                    <Divider orientation="left">分析结果预览</Divider>
                    <div style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px', minHeight: '80px' }}>
                      <Paragraph type="secondary" style={{ margin: 0 }}>分析结果将显示在此区域</Paragraph>
                    </div>
                  </div>
                ),
              },
              {
                key: 'history',
                label: '历史拆解',
                children: (
                  <div style={{ padding: '16px 0' }}>
                    <Divider orientation="left">最近分析结果预览</Divider>
                    <div style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px', minHeight: '80px' }}>
                      <Paragraph type="secondary" style={{ margin: 0 }}>历史分析结果将显示在此区域</Paragraph>
                    </div>
                  </div>
                ),
              },
            ]}
          />
        </Card>

        {/* 智能建议 */}
        <Card 
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
              <span style={{ fontSize: '20px' }}>🚀</span>
              <span>智能建议</span>
            </div>
          }
          style={{ 
            minHeight: '280px',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          }}
        >
          <div style={{ padding: '16px 0' }}>
            <Paragraph strong>基于工作内容的智能建议</Paragraph>
            <Paragraph>系统根据您的工作模式和内容提供相关建议。</Paragraph>
            
            <div style={{ marginTop: '16px' }}>
              <Card type="inner" title="今日工作建议" style={{ marginBottom: '12px' }}>
                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                  <li style={{ marginBottom: '8px' }}>优先完成高优先级任务：完成项目规划</li>
                  <li style={{ marginBottom: '8px' }}>建议在上午10点前准备好会议材料</li>
                  <li>考虑更新项目文档以保持信息同步</li>
                </ul>
              </Card>
              
              <Card type="inner" title="效率提示">
                <Paragraph type="secondary">根据您的工作习惯，建议在每天下午3点进行工作回顾和明日计划安排。</Paragraph>
                <Button type="link" style={{ padding: 0 }}>查看更多建议</Button>
              </Card>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
