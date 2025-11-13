/**
 * 工作页面 - 一次滚动切换一个模块 + 右侧导航 + 暗版卡片边框 + 模块内独立滚动
 */
import { Card, Typography, Input, Button, Divider, Space, Table, Tabs, Tag } from 'antd';
import { useState, useRef, useEffect } from 'react';

const { Title, Paragraph } = Typography;

export default function WorkPage() {
  const [activeTabKey, setActiveTabKey] = useState('new');

  // 当前模块索引：0=待办，1=项目，2=智能建议
  const [currentIndex, setCurrentIndex] = useState(0);

  // 滚动动画锁
  const isAnimatingRef = useRef(false);
  const currentIndexRef = useRef(0);

  const todoSectionRef = useRef<HTMLDivElement | null>(null);
  const projectSectionRef = useRef<HTMLDivElement | null>(null);
  const suggestionSectionRef = useRef<HTMLDivElement | null>(null);

  const sections = [todoSectionRef, projectSectionRef, suggestionSectionRef];
  const sectionLabels = ['待办管理', '项目拆解', '智能建议'];

  const handleTabChange = (key: string) => {
    setActiveTabKey(key);
  };

  const scrollToIndex = (index: number) => {
    const target = sections[index]?.current;
    if (!target) return;

    isAnimatingRef.current = true;
    currentIndexRef.current = index;
    setCurrentIndex(index);

    const top = target.offsetTop;

    window.scrollTo({
      top,
      behavior: 'smooth',
    });

    setTimeout(() => {
      isAnimatingRef.current = false;
    }, 600);
  };

  // 找到最近的可滚动父元素（overflowY 为 auto/scroll 且内容超出）
  const findScrollableParent = (el: HTMLElement | null): HTMLElement | null => {
    let node: HTMLElement | null = el;
    while (node && node !== document.body) {
      const style = window.getComputedStyle(node);
      const overflowY = style.overflowY;
      const canScrollY =
        (overflowY === 'auto' || overflowY === 'scroll') &&
        node.scrollHeight > node.clientHeight;

      if (canScrollY) return node;
      node = node.parentElement;
    }
    return null;
  };

  useEffect(() => {
    const handleWheel = (e: WheelEvent) => {
      const deltaY = e.deltaY;
      const cur = currentIndexRef.current;

      const target = e.target as HTMLElement | null;
      const scrollableParent = findScrollableParent(target);

      // 如果在某个内部可滚容器里，而且该容器在当前滚动方向上还没到边界，就让它自己滚
      if (scrollableParent) {
        const { scrollTop, scrollHeight, clientHeight } = scrollableParent;
        const atTop = scrollTop <= 0;
        const atBottom = scrollTop + clientHeight >= scrollHeight - 1;

        if ((deltaY < 0 && !atTop) || (deltaY > 0 && !atBottom)) {
          // 内部还可以继续滚动 -> 不打断，不切模块
          return;
        }
        // 否则已经到顶部/底部，滚一格就切模块（下面逻辑处理）
      }

      // 第一屏向上滚：放行默认行为
      if (cur === 0 && deltaY < 0) {
        return;
      }
      // 最后一屏向下滚：放行默认行为
      if (cur === sections.length - 1 && deltaY > 0) {
        return;
      }

      // 其他情况接管，实现一滚一屏
      e.preventDefault();

      if (isAnimatingRef.current) return;

      if (deltaY > 0 && cur < sections.length - 1) {
        scrollToIndex(cur + 1);
      } else if (deltaY < 0 && cur > 0) {
        scrollToIndex(cur - 1);
      }
    };

    window.addEventListener('wheel', handleWheel, { passive: false });

    return () => {
      window.removeEventListener('wheel', handleWheel);
    };
  }, [sections.length]);

  // 初始进入时滚到第一个模块顶部
  useEffect(() => {
    const first = sections[0]?.current;
    if (first) {
      window.scrollTo({ top: first.offsetTop, behavior: 'auto' });
    }
  }, []);

  // 暗版卡片边框 + 阴影复用样式
  const darkCardFrame: React.CSSProperties = {
    borderRadius: 16,
    boxShadow: '0 18px 45px rgba(15, 23, 42, 0.15)',
    border: '1px solid rgba(148, 163, 184, 0.45)',
  };

  // 卡片内部内容区域：固定高度 + 独立滚动条
  const cardInnerScroll: React.CSSProperties = {
    maxHeight: 'calc(100vh - 220px)', // 留出标题、外边距等空间，自己可以调
    overflowY: 'auto',
    paddingRight: 4, // 给滚动条一点空间
  };

  return (
    <div>
      {/* 右侧悬浮导航（只有名称） */}
      <div
        style={{
          position: 'fixed',
          right: 24,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 1000,
          padding: '10px 8px',
          borderRadius: 999,
          background: 'rgba(255, 255, 255, 0.95)',
          boxShadow: '0 6px 20px rgba(0, 0, 0, 0.12)',
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          border: '1px solid #f0f0f0',
        }}
      >
        {sectionLabels.map((label, index) => {
          const active = index === currentIndex;
          return (
            <div
              key={label}
              onClick={() => scrollToIndex(index)}
              style={{
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '6px 10px',
                borderRadius: 999,
                background: active ? 'rgba(22, 119, 255, 0.08)' : 'transparent',
                transition: 'background 0.2s, opacity 0.2s',
                opacity: active ? 1 : 0.6,
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLDivElement).style.opacity = '1';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLDivElement).style.opacity = active ? '1' : '0.6';
              }}
            >
              <div
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: '50%',
                  border: '2px solid #1677ff',
                  backgroundColor: active ? '#1677ff' : '#fff',
                }}
              />
              <span
                style={{
                  fontSize: 13,
                  color: active ? '#1677ff' : '#666',
                  whiteSpace: 'nowrap',
                }}
              >
                {label}
              </span>
            </div>
          );
        })}
      </div>

      {/* 第一屏：标题 + 待办管理 */}
      <section
        ref={todoSectionRef}
        style={{
          height: '100vh',
          boxSizing: 'border-box',
          padding: '32px 24px 24px',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#fafafa',
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: '1200px',
            margin: '0 auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 24,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12 }}>
            <Title level={1} style={{ margin: 0 }}>
              工作模式
            </Title>
            <Tag color="processing" style={{ borderRadius: 999 }}>
              Focus Mode
            </Tag>
          </div>

          <Card
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
                <span style={{ fontSize: '20px' }}>🔄</span>
                <span>待办管理</span>
                <Tag color="blue" style={{ borderRadius: 999 }}>
                  Today
                </Tag>
              </div>
            }
            style={{
              ...darkCardFrame,
              padding: '24px',
            }}
            bodyStyle={{ paddingTop: 16 }}
          >
            <div style={cardInnerScroll}>
              <Paragraph strong>工作任务跟踪与管理</Paragraph>
              <Paragraph type="secondary">
                在此部分您可以查看和管理当前的工作任务。
              </Paragraph>

              <Space direction="vertical" style={{ width: '100%', margin: '16px 0' }} size={16}>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Input
                    placeholder="输入新任务，例如：整理接口文档 / 准备周会汇报..."
                    style={{ flex: 1 }}
                  />
                  <Button type="primary">添加任务</Button>
                </div>

                <Table
                  columns={[
                    { title: '任务名称', dataIndex: 'name', key: 'name' },
                    { title: '优先级', dataIndex: 'priority', key: 'priority' },
                    { title: '状态', dataIndex: 'status', key: 'status' },
                    {
                      title: '操作',
                      key: 'action',
                      render: () => (
                        <Space size={8}>
                          <Button size="small" type="link">
                            编辑
                          </Button>
                          <Button size="small" type="link">
                            完成
                          </Button>
                        </Space>
                      ),
                    },
                  ]}
                  dataSource={[
                    { key: '1', name: '完成项目规划', priority: '高', status: '进行中' },
                    { key: '2', name: '准备会议材料', priority: '中', status: '待处理' },
                    { key: '3', name: '更新文档', priority: '低', status: '已完成' },
                    // 这里你后面可以塞很多行，滚动条会出现
                  ]}
                  pagination={false}
                  size="small"
                />
              </Space>
            </div>
          </Card>
        </div>
      </section>

      {/* 第二屏：项目拆解 */}
      <section
        ref={projectSectionRef}
        style={{
          height: '100vh',
          boxSizing: 'border-box',
          padding: '32px 24px 24px',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#ffffff',
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: '1200px',
            margin: '0 auto',
          }}
        >
          <Card
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
                <span style={{ fontSize: '20px' }}>📊</span>
                <span>项目拆解</span>
                <Tag color="geekblue" style={{ borderRadius: 999 }}>
                  Analysis
                </Tag>
              </div>
            }
            style={{
              ...darkCardFrame,
              padding: '24px',
            }}
            bodyStyle={{ paddingTop: 16 }}
          >
            <div style={cardInnerScroll}>
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
                        <Paragraph type="secondary">
                          在此部分您可以输入数据并进行相关分析处理。
                        </Paragraph>

                        <Space
                          direction="vertical"
                          style={{ width: '100%', margin: '16px 0' }}
                          size={16}
                        >
                          <Input placeholder="请输入需要分析的内容，例如：某个项目的需求拆解 / 风险点..." />
                          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                            <Button>重置</Button>
                            <Button type="primary">开始分析</Button>
                          </div>
                        </Space>

                        <Divider orientation="left">分析结果预览</Divider>
                        <div
                          style={{
                            backgroundColor: '#fafafa',
                            padding: '12px',
                            borderRadius: '8px',
                            minHeight: '80px',
                            border: '1px dashed #d9d9d9',
                          }}
                        >
                          <Paragraph type="secondary" style={{ margin: 0 }}>
                            分析结果将显示在此区域
                          </Paragraph>
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
                        <div
                          style={{
                            backgroundColor: '#fafafa',
                            padding: '12px',
                            borderRadius: '8px',
                            minHeight: '80px',
                            border: '1px dashed #d9d9d9',
                          }}
                        >
                          <Paragraph type="secondary" style={{ margin: 0 }}>
                            历史分析结果将显示在此区域
                          </Paragraph>
                        </div>
                      </div>
                    ),
                  },
                ]}
                tabBarStyle={{ marginBottom: 0 }}
              />
            </div>
          </Card>
        </div>
      </section>

      {/* 第三屏：智能建议 */}
      <section
        ref={suggestionSectionRef}
        style={{
          height: '100vh',
          boxSizing: 'border-box',
          padding: '32px 24px 24px',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#fafafa',
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: '1200px',
            margin: '0 auto',
          }}
        >
          <Card
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
                <span style={{ fontSize: '20px' }}>🚀</span>
                <span>智能建议</span>
                <Tag color="green" style={{ borderRadius: 999 }}>
                  AI Tips
                </Tag>
              </div>
            }
            style={{
              ...darkCardFrame,
              padding: '24px',
            }}
            bodyStyle={{ paddingTop: 16 }}
          >
            <div style={cardInnerScroll}>
              <div style={{ padding: '16px 0' }}>
                <Paragraph strong>基于工作内容的智能建议</Paragraph>
                <Paragraph type="secondary">
                  系统根据您的工作模式和内容提供相关建议。
                </Paragraph>

                <div style={{ marginTop: '16px', display: 'grid', gap: 12 }}>
                  <Card type="inner" title="今日工作建议" style={{ borderRadius: 10 }}>
                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                      <li style={{ marginBottom: '8px' }}>优先完成高优先级任务：完成项目规划</li>
                      <li style={{ marginBottom: '8px' }}>建议在上午10点前准备好会议材料</li>
                      <li>考虑更新项目文档以保持信息同步</li>
                    </ul>
                  </Card>

                  <Card type="inner" title="效率提示" style={{ borderRadius: 10 }}>
                    <Paragraph type="secondary">
                      根据您的工作习惯，建议在每天下午 3 点进行工作回顾和明日计划安排。
                    </Paragraph>
                    <Button type="link" style={{ padding: 0 }}>
                      查看更多建议
                    </Button>
                  </Card>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
