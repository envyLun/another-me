/**
 * "模仿我"能力面板
 * 展示模仿相关的操作
 */
import { Row, Col, message } from 'antd';
import { useMode } from '@/hooks';
import { ActionCard } from '@/components/common';
import { workAPI, lifeAPI } from '@/api';
import { useState } from 'react';

export function MimicPanel() {
  const { mode, availableActions } = useMode();
  const [loadingActions, setLoadingActions] = useState<Record<string, boolean>>({});

  const handleAction = async (actionKey: string) => {
    setLoadingActions(prev => ({ ...prev, [actionKey]: true }));

    try {
      switch (actionKey) {
        case 'weekly_report':
          const report = await workAPI.generateWeeklyReport();
          message.success('周报生成成功');
          console.log('周报内容:', report);
          break;

        case 'organize_todos':
          // 这里需要用户输入待办列表，实际应该弹出对话框
          message.info('请输入待办事项');
          break;

        case 'meeting_summary':
          message.info('请输入会议记录');
          break;

        case 'casual_chat':
          message.info('开始闲聊');
          break;

        case 'record_event':
          message.info('记录生活事件');
          break;

        default:
          message.warning('该功能即将上线');
      }
    } catch (error: any) {
      message.error(error.message || '操作失败');
    } finally {
      setLoadingActions(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  return (
    <div>
      <h3 style={{ marginBottom: '16px' }}>
        🤖 模仿我 - {mode === 'work' ? '工作助手' : '生活伙伴'}
      </h3>
      
      <Row gutter={[16, 16]}>
        {availableActions.map(action => (
          <Col xs={24} sm={12} md={8} key={action.key}>
            <ActionCard
              title={action.label}
              description={action.description}
              icon={action.icon}
              onClick={() => handleAction(action.key)}
              loading={loadingActions[action.key]}
            />
          </Col>
        ))}
      </Row>

      {availableActions.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          当前模式下暂无可用操作
        </div>
      )}
    </div>
  );
}
