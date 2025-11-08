import { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Typography, message, Space, Alert, Divider, InputNumber, Tag } from 'antd';
import { SaveOutlined, CheckCircleOutlined, ApiOutlined, ThunderboltOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { useConfigStore } from '@/store';
import apiClient from '@/api/client';
import type { ConfigTestResult } from '@/types';

const { Title, Paragraph } = Typography;

export default function ConfigPage() {
  const [form] = Form.useForm();
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<ConfigTestResult | null>(null);
  const { setConfig } = useConfigStore();

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const savedConfig = await apiClient.loadConfig();
      if (savedConfig) {
        form.setFieldsValue(savedConfig);
        setConfig(savedConfig);
      }
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const handleTest = async () => {
    try {
      const values = await form.validateFields();
      setTesting(true);
      setTestResult(null);
      
      const result = await apiClient.testConfig(values);
      setTestResult(result);
      
      if (result.success) {
        message.success('配置测试成功!');
      } else {
        message.error(result.message || '配置测试失败');
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '配置测试失败';
      setTestResult({ success: false, message: errorMsg });
      message.error(errorMsg);
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);
      
      const result = await apiClient.saveConfig(values);
      
      if (result.success) {
        setConfig(values);
        message.success('配置保存成功!');
        // 清除测试结果
        setTestResult(null);
      } else {
        message.error(result.message || '配置保存失败');
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '配置保存失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <Title level={2}>
        <ApiOutlined /> 系统配置
      </Title>
      <Paragraph style={{ color: '#666', fontSize: '15px' }}>
        配置 OpenAI API 相关参数，支持 OpenAI 和其他兼容 API
      </Paragraph>

      {/* 配置提示 */}
      <Alert
        message="配置说明"
        description={
          <div>
            <p>• API Key: 你的 API 密钥</p>
            <p>• Base URL: API 服务地址，默认为 OpenAI 官方地址</p>
            <p>• Model: 对话模型名称，如 gpt-3.5-turbo、qwen-turbo 等</p>
            <p>• Embedding Model: 文本向量化模型名称</p>
            <p>• Embedding Dimension: 向量维度，需与模型匹配</p>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />
      
      <Card style={{ maxWidth: 600 }}>
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            base_url: 'https://api.openai.com/v1',
            model: 'gpt-3.5-turbo',
            embedding_model: 'text-embedding-3-small',
            embedding_dimension: 1536,
          }}
        >
          <Form.Item
            label="API Key"
            name="api_key"
            rules={[
              { required: true, message: '请输入 API Key' },
            ]}
            extra="你的 API 密钥，将被安全存储"
          >
            <Input.Password 
              placeholder="输入你的 API Key" 
              autoComplete="off"
            />
          </Form.Item>

          <Form.Item
            label="API Base URL"
            name="base_url"
            rules={[
              { required: true, message: '请输入 Base URL' },
              { type: 'url', message: '请输入有效的 URL' }
            ]}
            extra="OpenAI、通义千问、智谱等平台的 API 地址"
          >
            <Input placeholder="https://api.openai.com/v1" />
          </Form.Item>

          <Form.Item
            label="对话模型"
            name="model"
            rules={[{ required: true, message: '请输入模型名称' }]}
            extra="如 gpt-3.5-turbo、qwen-turbo、glm-4 等"
          >
            <Input placeholder="输入模型名称" />
          </Form.Item>

          <Divider orientation="left">
            <Space>
              <ThunderboltOutlined />
              Embedding 配置
            </Space>
          </Divider>

          <Form.Item
            label="Embedding 模型"
            name="embedding_model"
            rules={[{ required: true, message: '请输入 Embedding 模型名称' }]}
            extra="用于文本向量化，如 text-embedding-3-small、text-embedding-v2 等"
          >
            <Input placeholder="输入 Embedding 模型名称" />
          </Form.Item>

          <Form.Item
            label="Embedding 维度"
            name="embedding_dimension"
            rules={[
              { required: true, message: '请输入 Embedding 维度' },
              { type: 'number', min: 128, max: 4096, message: '维度必须在 128-4096 之间' }
            ]}
            extra="模型输出的向量维度，如 1536、3072 等"
          >
            <InputNumber 
              style={{ width: '100%' }}
              placeholder="输入维度，如 1536" 
              min={128}
              max={4096}
              step={1}
            />
          </Form.Item>

          <Alert
            message="重要提示"
            description="修改 Embedding 配置后，需要重新处理所有文档和记忆数据。请确保配置的模型名称和维度与你使用的平台一致。"
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Divider />

          {/* 测试结果 */}
          {testResult && (
            <Alert
              message={testResult.success ? '测试成功' : '测试失败'}
              description={
                <div style={{ whiteSpace: 'pre-line' }}>
                  {testResult.message}
                  
                  {/* 详细状态 */}
                  {(testResult.model_available !== undefined || 
                    testResult.embedding_available !== undefined) && (
                    <div style={{ marginTop: 12 }}>
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        {testResult.model_available !== undefined && (
                          <div>
                            <Tag 
                              icon={testResult.model_available ? <CheckOutlined /> : <CloseOutlined />}
                              color={testResult.model_available ? 'success' : 'error'}
                            >
                              LLM 模型
                            </Tag>
                            <span style={{ marginLeft: 8, color: '#666' }}>
                              {testResult.model_available ? '可用' : '不可用'}
                            </span>
                          </div>
                        )}
                        
                        {testResult.embedding_available !== undefined && (
                          <div>
                            <Tag 
                              icon={testResult.embedding_available ? <CheckOutlined /> : <CloseOutlined />}
                              color={testResult.embedding_available ? 'success' : 'error'}
                            >
                              Embedding 模型
                            </Tag>
                            <span style={{ marginLeft: 8, color: '#666' }}>
                              {testResult.embedding_available ? '可用' : '不可用'}
                            </span>
                            {testResult.embedding_dimension && (
                              <span style={{ marginLeft: 8, color: '#999' }}>
                                (实际维度: {testResult.embedding_dimension})
                              </span>
                            )}
                          </div>
                        )}
                      </Space>
                    </div>
                  )}
                </div>
              }
              type={testResult.success ? 'success' : 'error'}
              showIcon
              closable
              onClose={() => setTestResult(null)}
              style={{ marginBottom: 16 }}
            />
          )}

          <Form.Item style={{ marginBottom: 0 }}>
            <Space>
              <Button
                type="default"
                icon={<CheckCircleOutlined />}
                onClick={handleTest}
                loading={testing}
              >
                测试配置
              </Button>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={handleSave}
                loading={saving}
              >
                保存配置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {/* 常见问题 */}
      <Card title="常见问题" style={{ marginTop: 24, maxWidth: 600 }}>
        <div style={{ lineHeight: 2 }}>
          <p><strong>Q: 如何获取 API Key？</strong></p>
          <p>A: 根据你使用的平台访问对应的控制台：</p>
          <ul style={{ marginLeft: 20 }}>
            <li>OpenAI: <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">platform.openai.com</a></li>
            <li>通义千问: <a href="https://dashscope.console.aliyun.com/apiKey" target="_blank" rel="noopener noreferrer">dashscope.console.aliyun.com</a></li>
            <li>智谱AI: <a href="https://open.bigmodel.cn/usercenter/apikeys" target="_blank" rel="noopener noreferrer">open.bigmodel.cn</a></li>
          </ul>
          
          <p><strong>Q: 支持哪些平台？</strong></p>
          <p>A: 支持所有兼容 OpenAI API 的平台，包括：</p>
          <ul style={{ marginLeft: 20 }}>
            <li>OpenAI 官方</li>
            <li>阿里云通义千问</li>
            <li>智谱AI (GLM)</li>
            <li>Moonshot (Kimi)</li>
            <li>其他兼容平台</li>
          </ul>
          
          <p><strong>Q: 配置保存在哪里？</strong></p>
          <p>A: 配置保存在后端服务器上，不会泄露到浏览器</p>

          <Divider />

          <p><strong>Q: Embedding 模型和维度如何填写？</strong></p>
          <p>A: 根据你使用的平台文档填写：</p>
          <ul style={{ marginLeft: 20 }}>
            <li>OpenAI: text-embedding-3-small (1536维) 或 text-embedding-3-large (3072维)</li>
            <li>通义千问: text-embedding-v2 (1536维)</li>
            <li>智谱AI: embedding-2 (1024维)</li>
          </ul>

          <p><strong>Q: 修改 Embedding 配置后需要做什么？</strong></p>
          <p>A: 需要重新上传所有文档和记忆，因为不同模型/维度生成的向量不兼容。建议在首次使用时就配置好。</p>
        </div>
      </Card>
    </div>
  );
}
