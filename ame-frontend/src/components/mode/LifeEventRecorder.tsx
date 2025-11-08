import { useState } from 'react';
import { Modal, Form, Input, Select, DatePicker, Button, message } from 'antd';
import { CalendarOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

const { TextArea } = Input;

interface LifeEventRecorderProps {
  visible: boolean;
  onClose: () => void;
  onRecord?: (event: any) => void;
}

/**
 * 生活事件记录器
 * 用于记录日常生活中的重要事件
 */
export function LifeEventRecorder({ 
  visible, 
  onClose,
  onRecord,
}: LifeEventRecorderProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      const eventData = {
        event_content: values.content,
        event_type: values.type,
        event_time: values.time ? values.time.toISOString() : new Date().toISOString(),
        tags: values.tags || [],
      };

      onRecord?.(eventData);
      message.success('生活事件已记录');
      form.resetFields();
      onClose();
    } catch (error) {
      console.error('Validation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={
        <span>
          <CalendarOutlined style={{ marginRight: 8 }} />
          记录生活事件
        </span>
      }
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={handleSubmit}>
          记录
        </Button>,
      ]}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          type: 'general',
          time: dayjs(),
        }}
      >
        <Form.Item
          name="content"
          label="事件内容"
          rules={[
            { required: true, message: '请输入事件内容' },
            { min: 5, message: '至少输入5个字符' },
          ]}
        >
          <TextArea 
            rows={4} 
            placeholder="描述一下发生了什么事..."
            maxLength={500}
            showCount
          />
        </Form.Item>

        <Form.Item
          name="type"
          label="事件类型"
          rules={[{ required: true, message: '请选择事件类型' }]}
        >
          <Select>
            <Select.Option value="general">日常</Select.Option>
            <Select.Option value="achievement">成就</Select.Option>
            <Select.Option value="learning">学习</Select.Option>
            <Select.Option value="social">社交</Select.Option>
            <Select.Option value="health">健康</Select.Option>
            <Select.Option value="entertainment">娱乐</Select.Option>
            <Select.Option value="other">其他</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="time"
          label="事件时间"
        >
          <DatePicker 
            showTime 
            format="YYYY-MM-DD HH:mm"
            style={{ width: '100%' }}
          />
        </Form.Item>

        <Form.Item
          name="tags"
          label="标签（可选）"
        >
          <Select
            mode="tags"
            placeholder="添加标签，如：健身、阅读、旅行等"
            maxTagCount={5}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
}
