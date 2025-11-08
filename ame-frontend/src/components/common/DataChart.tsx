/**
 * 数据图表组件
 */
import { Card } from 'antd';

interface DataChartProps {
  title?: string;
  data: any[];
  type: 'line' | 'bar' | 'pie' | 'area';
  xKey?: string;
  yKey?: string;
  height?: number;
  loading?: boolean;
}

export function DataChart({
  title,
  data,
  type,
  height = 300,
  loading = false,
}: DataChartProps) {
  // 简单实现，实际项目中应使用 recharts 或 ECharts
  const renderChart = () => {
    if (loading) {
      return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        加载中...
      </div>;
    }

    if (!data || data.length === 0) {
      return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
        暂无数据
      </div>;
    }

    // 这里只是占位，实际应该使用图表库
    return (
      <div style={{ 
        height, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: '#f5f5f5',
        borderRadius: '4px',
        color: '#999'
      }}>
        {type.toUpperCase()} 图表 - 数据点: {data.length}
        <br />
        <small>(实际项目中使用 recharts 或 ECharts 渲染)</small>
      </div>
    );
  };

  return (
    <Card title={title} loading={loading}>
      {renderChart()}
    </Card>
  );
}

// 便捷的图表类型组件
export function LineChart(props: Omit<DataChartProps, 'type'>) {
  return <DataChart {...props} type="line" />;
}

export function BarChart(props: Omit<DataChartProps, 'type'>) {
  return <DataChart {...props} type="bar" />;
}

export function PieChart(props: Omit<DataChartProps, 'type'>) {
  return <DataChart {...props} type="pie" />;
}

export function AreaChart(props: Omit<DataChartProps, 'type'>) {
  return <DataChart {...props} type="area" />;
}
