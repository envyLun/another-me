/**
 * 知识库管理页面（完整版）
 */
import { useState } from 'react';
import {
  Card,
  Button,
  Table,
  Space,
  Upload,
  Input,
  message,
  Modal,
  Tag,
  Row,
  Col,
  Popconfirm,
} from 'antd';
import {
  UploadOutlined,
  SearchOutlined,
  DeleteOutlined,
  EyeOutlined,
  FileTextOutlined,
  DatabaseOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useKnowledge } from '@/hooks';
import { EmptyState, StatCard } from '@/components/common';
import { formatFileSize, formatRelativeTime } from '@/utils';
import type { DocumentInfo } from '@/types';
import type { UploadFile } from 'antd';

const { Search } = Input;

export default function KnowledgePage() {
  const {
    documents,
    stats,
    loading,
    uploading,
    searchResults,
    searching,
    uploadDocument,
    deleteDocument,
    searchKnowledge,
    clearSearch,
    loadDocuments,
  } = useKnowledge();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDoc, setSelectedDoc] = useState<DocumentInfo | null>(null);
  const [viewModalVisible, setViewModalVisible] = useState(false);

  // 处理文件上传
  const handleUpload = async (file: UploadFile) => {
    try {
      await uploadDocument(file as any);
      message.success(`${file.name} 上传成功`);
    } catch (error: any) {
      message.error(`${file.name} 上传失败: ${error.message}`);
    }
    return false; // 阻止默认上传行为
  };

  // 处理搜索
  const handleSearch = async (value: string) => {
    setSearchQuery(value);
    if (value.trim()) {
      await searchKnowledge(value);
    } else {
      clearSearch();
    }
  };

  // 处理删除
  const handleDelete = async (docId: string) => {
    try {
      await deleteDocument(docId);
      message.success('删除成功');
    } catch (error: any) {
      message.error(`删除失败: ${error.message}`);
    }
  };

  // 查看文档
  const handleView = (doc: DocumentInfo) => {
    setSelectedDoc(doc);
    setViewModalVisible(true);
  };

  // 表格列定义
  const columns = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      render: (text: string) => (
        <span>
          <FileTextOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          {text}
        </span>
      ),
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      width: 120,
      render: (size: number) => formatFileSize(size),
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      width: 150,
      render: (time: string) => formatRelativeTime(time),
    },
    {
      title: '分块数',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
      width: 100,
      render: (count: number) => count || '-',
    },
    {
      title: '操作',
      key: 'actions',
      width: 180,
      render: (_: any, record: DocumentInfo) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          <Popconfirm
            title="确认删除此文档？"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 显示数据（搜索结果或文档列表）
  const displayData = searchQuery ? searchResults.map((r: any) => ({
    id: r.metadata?.doc_id || Math.random().toString(),
    filename: r.metadata?.filename || '搜索结果',
    size: 0,
    upload_time: new Date().toISOString(),
    content: r.content,
    score: r.score,
  })) : documents;

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>
          <DatabaseOutlined style={{ marginRight: 8 }} />
          RAG 知识库
        </h1>
        <p style={{ margin: '8px 0 0', color: '#666' }}>
          管理您的知识文档，构建专属知识库
        </p>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <StatCard
            title="文档总数"
            value={stats?.document_count || 0}
            icon={<FileTextOutlined />}
            color="#1890ff"
            suffix="个"
          />
        </Col>
        <Col xs={24} sm={8}>
          <StatCard
            title="总分块数"
            value={stats?.total_chunks || 0}
            icon={<DatabaseOutlined />}
            color="#52c41a"
            suffix="块"
          />
        </Col>
        <Col xs={24} sm={8}>
          <StatCard
            title="总大小"
            value={formatFileSize(stats?.total_size || 0)}
            icon={<ClockCircleOutlined />}
            color="#faad14"
          />
        </Col>
      </Row>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Upload
              beforeUpload={handleUpload}
              showUploadList={false}
              accept=".txt,.md,.pdf,.docx,.doc"
            >
              <Button
                type="primary"
                icon={<UploadOutlined />}
                loading={uploading}
              >
                上传文档
              </Button>
            </Upload>
            <Button onClick={() => loadDocuments(1)}>刷新</Button>
          </Space>

          <Search
            placeholder="搜索知识..."
            allowClear
            enterButton={<SearchOutlined />}
            style={{ width: 300 }}
            onSearch={handleSearch}
            loading={searching}
          />
        </Space>
      </Card>

      {/* 文档列表 */}
      <Card>
        {displayData.length === 0 ? (
          <EmptyState
            title={searchQuery ? '未找到相关文档' : '暂无文档'}
            description={
              searchQuery
                ? '尝试使用不同的关键词搜索'
                : '点击上传按钮开始构建知识库'
            }
            action={!searchQuery ? {
              text: '上传文档',
              onClick: () => document.querySelector<HTMLElement>('.ant-upload input')?.click(),
            } : undefined}
          />
        ) : (
          <Table
            dataSource={displayData}
            columns={columns}
            loading={loading || searching}
            rowKey="id"
            pagination={{
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个文档`,
            }}
          />
        )}
      </Card>

      {/* 文档查看对话框 */}
      <Modal
        title={
          <span>
            <FileTextOutlined style={{ marginRight: 8 }} />
            {selectedDoc?.filename}
          </span>
        }
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedDoc && (
          <div>
            <Space direction="vertical" size="small" style={{ marginBottom: 16 }}>
              <div>
                <Tag color="blue">大小: {formatFileSize(selectedDoc.size)}</Tag>
                <Tag color="green">
                  上传时间: {formatRelativeTime(selectedDoc.upload_time)}
                </Tag>
                {selectedDoc.chunk_count && (
                  <Tag color="orange">分块: {selectedDoc.chunk_count}</Tag>
                )}
              </div>
            </Space>
            <div
              style={{
                maxHeight: '400px',
                overflow: 'auto',
                padding: '16px',
                background: '#f5f5f5',
                borderRadius: '4px',
              }}
            >
              <p>文档内容预览功能待实现...</p>
              <p style={{ color: '#999' }}>（需要后端 API 支持）</p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
