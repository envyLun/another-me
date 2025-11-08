import { useState } from 'react';
import { Upload, Button, message, Progress, List, Typography, Space, Tag } from 'antd';
import { InboxOutlined, FileTextOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import apiClient from '@/api/client';

const { Dragger } = Upload;
const { Text } = Typography;

interface FileUploaderProps {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

interface UploadFileWithStatus extends UploadFile {
  uploadStatus?: 'uploading' | 'success' | 'error';
  errorMessage?: string;
}

/**
 * 文件上传组件
 * 支持拖拽上传、批量上传、进度展示
 */
export function FileUploader({ onSuccess, onError }: FileUploaderProps) {
  const [fileList, setFileList] = useState<UploadFileWithStatus[]>([]);
  const [uploading, setUploading] = useState(false);

  // 支持的文件类型
  const ALLOWED_TYPES = [
    'text/plain',
    'text/markdown',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
  ];

  const ALLOWED_EXTENSIONS = ['.txt', '.md', '.pdf', '.docx', '.doc'];

  const beforeUpload: UploadProps['beforeUpload'] = (file) => {
    const isAllowedType = ALLOWED_TYPES.includes(file.type) || 
      ALLOWED_EXTENSIONS.some(ext => file.name.toLowerCase().endsWith(ext));
    
    if (!isAllowedType) {
      message.error(`不支持的文件类型: ${file.name}。请上传 TXT, MD, PDF, DOCX 文件。`);
      return Upload.LIST_IGNORE;
    }

    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error(`文件 ${file.name} 超过 10MB 限制`);
      return Upload.LIST_IGNORE;
    }

    return false; // 阻止自动上传
  };

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择文件');
      return;
    }

    setUploading(true);
    let successCount = 0;
    let failedCount = 0;

    for (const file of fileList) {
      try {
        // 更新状态为上传中
        setFileList(prev => prev.map(f => 
          f.uid === file.uid 
            ? { ...f, uploadStatus: 'uploading' as const }
            : f
        ));

        await apiClient.uploadDocument(file.originFileObj as File);
        
        // 更新状态为成功
        setFileList(prev => prev.map(f => 
          f.uid === file.uid 
            ? { ...f, uploadStatus: 'success' as const }
            : f
        ));
        
        successCount++;
      } catch (error) {
        console.error(`Upload failed for ${file.name}:`, error);
        
        // 更新状态为失败
        setFileList(prev => prev.map(f => 
          f.uid === file.uid 
            ? { 
                ...f, 
                uploadStatus: 'error' as const,
                errorMessage: (error as Error).message || '上传失败'
              }
            : f
        ));
        
        failedCount++;
        onError?.(error as Error);
      }
    }

    setUploading(false);

    if (successCount > 0) {
      message.success(`成功上传 ${successCount} 个文件`);
      onSuccess?.();
    }
    
    if (failedCount > 0) {
      message.error(`${failedCount} 个文件上传失败`);
    }

    // 清空已成功的文件
    setFileList(prev => prev.filter(f => f.uploadStatus !== 'success'));
  };

  const uploadProps: UploadProps = {
    multiple: true,
    fileList,
    beforeUpload,
    onChange: ({ fileList: newFileList }) => {
      setFileList(newFileList as UploadFileWithStatus[]);
    },
    onRemove: (file) => {
      setFileList(prev => prev.filter(f => f.uid !== file.uid));
    },
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'uploading':
        return <Progress type="circle" percent={50} width={20} />;
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <FileTextOutlined />;
    }
  };

  return (
    <div>
      <Dragger {...uploadProps} disabled={uploading}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p className="ant-upload-hint">
          支持 TXT, MD, PDF, DOCX 格式，单个文件不超过 10MB
        </p>
      </Dragger>

      {fileList.length > 0 && (
        <>
          <List
            style={{ marginTop: 16 }}
            size="small"
            dataSource={fileList}
            renderItem={(file) => (
              <List.Item>
                <Space>
                  {getStatusIcon(file.uploadStatus)}
                  <Text>{file.name}</Text>
                  <Tag>{(file.size! / 1024).toFixed(1)} KB</Tag>
                  {file.uploadStatus === 'error' && (
                    <Text type="danger" style={{ fontSize: 12 }}>
                      {file.errorMessage}
                    </Text>
                  )}
                </Space>
              </List.Item>
            )}
          />

          <Button
            type="primary"
            onClick={handleUpload}
            loading={uploading}
            disabled={uploading}
            style={{ marginTop: 16, width: '100%' }}
          >
            {uploading ? '上传中...' : `上传 ${fileList.length} 个文件`}
          </Button>
        </>
      )}
    </div>
  );
}
