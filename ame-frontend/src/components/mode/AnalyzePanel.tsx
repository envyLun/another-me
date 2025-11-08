/**
 * "分析我"能力面板
 * 展示分析相关的操作和数据可视化
 */
import { Row, Col, message, Space } from 'antd';
import { useMode } from '@/hooks';
import { ActionCard, DataChart, AnalysisResult } from '@/components/common';
import { lifeAPI } from '@/api';
import { handleError } from '@/utils/errorHandler';
import { useState } from 'react';

export function AnalyzePanel() {
  const { mode, availableActions } = useMode();
  const [loadingActions, setLoadingActions] = useState<Record<string, boolean>>({});
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [analysisType, setAnalysisType] = useState<'mood' | 'interests' | 'summary' | 'general'>('general');

  const handleAction = async (actionKey: string) => {
    setLoadingActions(prev => ({ ...prev, [actionKey]: true }));

    try {
      switch (actionKey) {
        case 'project_progress':
          message.info('选择项目');
          break;

        case 'time_analysis':
          message.info('分析时间使用');
          break;

        case 'mood_analysis':
          const moodResult = await lifeAPI.analyzeMood({
            mood_entry: '最近几天的心情记录...',
          });
          setAnalysisData(moodResult);
          setAnalysisType('mood');
          message.success('心情分析完成');
          break;

        case 'interest_tracking':
          const interests = await lifeAPI.trackInterests(30);
          setAnalysisData(interests);
          setAnalysisType('interests');
          message.success('兴趣追踪完成');
          break;

        case 'life_summary':
          const summary = await lifeAPI.generateLifeSummary({ period: 'week' });
          setAnalysisData(summary);
          setAnalysisType('summary');
          message.success('生活总结生成成功');
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
        🔍 分析我 - {mode === 'work' ? '工作洞察' : '生活分析'}
      </h3>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 操作卡片 */}
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

        {/* 分析结果展示 */}
        {analysisData && (
          <AnalysisResult 
            title="分析结果" 
            data={analysisData} 
            type={analysisType}
          />
        )}

        {/* 数据可视化占位 */}
        {mode === 'work' && (
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <DataChart
                title="项目进度统计"
                data={[]}
                type="bar"
                height={250}
              />
            </Col>
            <Col xs={24} md={12}>
              <DataChart
                title="时间分布"
                data={[]}
                type="pie"
                height={250}
              />
            </Col>
          </Row>
        )}

        {mode === 'life' && (
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <DataChart
                title="情绪变化趋势"
                data={[]}
                type="line"
                height={250}
              />
            </Col>
            <Col xs={24} md={12}>
              <DataChart
                title="兴趣爱好分布"
                data={[]}
                type="pie"
                height={250}
              />
            </Col>
          </Row>
        )}

        {availableActions.length === 0 && !analysisData && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            当前模式下暂无可用分析
          </div>
        )}
      </Space>
    </div>
  );
}
