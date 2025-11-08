/**
 * "模仿我"能力面板
 * 展示模仿相关的操作
 */
import { Row, Col, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useMode } from '@/hooks';
import { ActionCard } from '@/components/common';
import { TodoOrganizer, WeeklyReportGenerator, MeetingSummaryGenerator, LifeEventRecorder } from '@/components/mode';
import { lifeAPI } from '@/api';
import { handleError } from '@/utils/errorHandler';
import { useState } from 'react';

export function MimicPanel() {
  const navigate = useNavigate();
  const { mode, availableActions } = useMode();
  const [loadingActions, setLoadingActions] = useState<Record<string, boolean>>({});
  const [todoOrganizerVisible, setTodoOrganizerVisible] = useState(false);
  const [weeklyReportVisible, setWeeklyReportVisible] = useState(false);
  const [meetingSummaryVisible, setMeetingSummaryVisible] = useState(false);
  const [lifeEventRecorderVisible, setLifeEventRecorderVisible] = useState(false);

  const handleAction = async (actionKey: string) => {
    setLoadingActions(prev => ({ ...prev, [actionKey]: true }));

    try {
      switch (actionKey) {
        case 'weekly_report':
          // 弹出周报生成器
          setWeeklyReportVisible(true);
          break;

        case 'organize_todos':
          // 弹出待办整理对话框
          setTodoOrganizerVisible(true);
          break;

        case 'meeting_summary':
          // 弹出会议总结对话框
          setMeetingSummaryVisible(true);
          break;

        case 'casual_chat':
          // 闲聊功能 - 跳转到聊天页面
          message.info('跳转到聊天界面...');
          navigate('/chat');
          break;

        case 'record_event':
          // 弹出生活事件记录对话框
          setLifeEventRecorderVisible(true);
          break;

        default:
          message.warning('该功能即将上线');
      }
    } catch (error: any) {
      handleError(error, '操作失败');
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

      {/* 待办整理对话框 */}
      <TodoOrganizer
        visible={todoOrganizerVisible}
        onClose={() => setTodoOrganizerVisible(false)}
        onOrganized={(todos) => {
          console.log('整理后的待办:', todos);
          message.success('待办事项已整理完成！');
          setTodoOrganizerVisible(false);
        }}
      />

      {/* 周报生成器 */}
      <WeeklyReportGenerator
        visible={weeklyReportVisible}
        onClose={() => setWeeklyReportVisible(false)}
        onGenerate={(report) => {
          console.log('生成的周报:', report);
          message.success('周报生成完成！');
          setWeeklyReportVisible(false);
        }}
      />

      {/* 会议总结生成器 */}
      <MeetingSummaryGenerator
        visible={meetingSummaryVisible}
        onClose={() => setMeetingSummaryVisible(false)}
        onGenerated={(summary) => {
          console.log('生成的会议总结:', summary);
          message.success('会议总结生成完成！');
          setMeetingSummaryVisible(false);
        }}
      />

      {/* 生活事件记录器 */}
      <LifeEventRecorder
        visible={lifeEventRecorderVisible}
        onClose={() => setLifeEventRecorderVisible(false)}
        onRecord={async (eventData) => {
          try {
            const result = await lifeAPI.recordLifeEvent(eventData);
            if (result.success) {
              message.success('生活事件已记录');
            }
          } catch (error: any) {
            handleError(error, '记录失败');
          } finally {
            setLifeEventRecorderVisible(false);
          }
        }}
      />
    </div>
  );
}
