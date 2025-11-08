import { useState } from 'react';
import { Modal, Form, Input, Select, Radio, Switch, Button, Steps, message, DatePicker } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { workAPI } from '@/api';
import dayjs, { Dayjs } from 'dayjs';

const { TextArea } = Input;
const { Step } = Steps;

interface WeeklyReportOptions {
  timeRange: 'this_week' | 'last_week' | 'custom';
  tone: 'professional' | 'casual' | 'formal';
  includeStats: boolean;
  sections?: string[];
  customStartDate?: Dayjs;
  customEndDate?: Dayjs;
}

interface WeeklyReportGeneratorProps {
  visible: boolean;
  onClose: () => void;
  onGenerate?: (report: string) => void;
}

/**
 * 周报生成器组件
 * 支持配置、生成、预览三步流程
 */
export function WeeklyReportGenerator({ 
  visible, 
  onClose,
  onGenerate,
}: WeeklyReportGeneratorProps) {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState('');
  const [streamingContent, setStreamingContent] = useState('');

  /**
   * 计算周报的时间范围
   */
  const calculateDateRange = (options: WeeklyReportOptions): { start_date?: string; end_date?: string } => {
    const now = dayjs();
    let startDate: Dayjs;
    let endDate: Dayjs;

    switch (options.timeRange) {
      case 'this_week':
        // 本周：从周一到现在
        startDate = now.startOf('week').add(1, 'day'); // 周一
        endDate = now;
        break;
      
      case 'last_week':
        // 上周：上周一到上周日
        startDate = now.subtract(1, 'week').startOf('week').add(1, 'day');
        endDate = now.subtract(1, 'week').endOf('week').add(1, 'day');
        break;
      
      case 'custom':
        // 自定义时间
        startDate = options.customStartDate || now.subtract(7, 'day');
        endDate = options.customEndDate || now;
        break;
      
      default:
        startDate = now.subtract(7, 'day');
        endDate = now;
    }

    return {
      start_date: startDate.format('YYYY-MM-DD'),
      end_date: endDate.format('YYYY-MM-DD'),
    };
  };

  const handleConfigSubmit = async () => {
    try {
      const values = await form.validateFields();
      setCurrentStep(1);
      await generateReport(values);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const generateReport = async (options: WeeklyReportOptions) => {
    setLoading(true);
    setStreamingContent('');
    
    try {
      // 计算时间范围
      const dateRange = calculateDateRange(options);
      
      // 调用后端 API
      const response = await workAPI.generateWeeklyReport({
        start_date: dateRange.start_date,
        end_date: dateRange.end_date,
      });

      if (response.success) {
        // 模拟流式显示效果
        const reportText = response.report;
        for (let i = 0; i < reportText.length; i += 20) {
          await new Promise(resolve => setTimeout(resolve, 30));
          setStreamingContent(reportText.slice(0, i + 20));
        }
        
        setReport(reportText);
        setCurrentStep(2);
        message.success('周报生成完成！');
      } else {
        throw new Error('生成失败');
      }
    } catch (error: any) {
      console.error('生成失败:', error);
      message.error(error.response?.data?.detail || error.message || '生成失败，请检查后端服务是否启动');
      setCurrentStep(0); // 返回配置页
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(report);
    message.success('已复制到剪贴板');
  };

  const handleEdit = (value: string) => {
    setReport(value);
  };

  const handleFinish = () => {
    onGenerate?.(report);
    handleReset();
    onClose();
  };

  const handleReset = () => {
    setCurrentStep(0);
    setReport('');
    setStreamingContent('');
    form.resetFields();
  };

  return (
    <Modal
      title="📊 周报生成器"
      open={visible}
      onCancel={onClose}
      width={800}
      footer={null}
      destroyOnClose
    >
      <Steps current={currentStep} style={{ marginBottom: 24 }}>
        <Step title="配置" description="设置生成参数" />
        <Step title="生成中" description="AI正在生成" icon={loading ? <LoadingOutlined /> : undefined} />
        <Step title="预览" description="查看并编辑" />
      </Steps>

      {/* 步骤1: 配置 */}
      {currentStep === 0 && (
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            timeRange: 'this_week',
            tone: 'professional',
            includeStats: true,
          }}
        >
          <Form.Item
            name="timeRange"
            label="时间范围"
            rules={[{ required: true }]}
          >
            <Radio.Group onChange={(e) => {
              if (e.target.value !== 'custom') {
                form.setFieldsValue({ customStartDate: undefined, customEndDate: undefined });
              }
            }}>
              <Radio value="this_week">本周</Radio>
              <Radio value="last_week">上周</Radio>
              <Radio value="custom">自定义</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prev, curr) => prev.timeRange !== curr.timeRange}>
            {({ getFieldValue }) => {
              return getFieldValue('timeRange') === 'custom' ? (
                <>
                  <Form.Item
                    name="customStartDate"
                    label="开始日期"
                    rules={[{ required: true, message: '请选择开始日期' }]}
                  >
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                  <Form.Item
                    name="customEndDate"
                    label="结束日期"
                    rules={[{ required: true, message: '请选择结束日期' }]}
                  >
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </>
              ) : null;
            }}
          </Form.Item>

          <Form.Item
            name="tone"
            label="写作风格"
            rules={[{ required: true }]}
          >
            <Select>
              <Select.Option value="professional">专业</Select.Option>
              <Select.Option value="casual">轻松</Select.Option>
              <Select.Option value="formal">正式</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="includeStats"
            label="包含数据统计"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="additionalNotes"
            label="补充说明（可选）"
          >
            <TextArea 
              rows={3} 
              placeholder="如有需要补充的信息，请在此输入..."
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" onClick={handleConfigSubmit} block>
              开始生成
            </Button>
          </Form.Item>
        </Form>
      )}

      {/* 步骤2: 生成中 */}
      {currentStep === 1 && (
        <div style={{ minHeight: 300 }}>
          <div style={{ textAlign: 'center', marginBottom: 16 }}>
            <LoadingOutlined style={{ fontSize: 48, color: '#1890ff' }} />
            <p style={{ marginTop: 16, fontSize: 16 }}>AI 正在为你生成周报...</p>
          </div>
          <div 
            style={{ 
              background: '#f5f5f5', 
              padding: 16, 
              borderRadius: 8,
              maxHeight: 400,
              overflowY: 'auto',
            }}
          >
            <ReactMarkdown>{streamingContent}</ReactMarkdown>
          </div>
        </div>
      )}

      {/* 步骤3: 预览编辑 */}
      {currentStep === 2 && (
        <div>
          <TextArea
            value={report}
            onChange={(e) => handleEdit(e.target.value)}
            rows={15}
            style={{ marginBottom: 16 }}
          />
          <div style={{ display: 'flex', gap: 8 }}>
            <Button type="primary" onClick={handleFinish}>
              完成
            </Button>
            <Button onClick={handleCopy}>
              复制
            </Button>
            <Button onClick={handleReset}>
              重新生成
            </Button>
            <Button onClick={onClose}>
              取消
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
}
