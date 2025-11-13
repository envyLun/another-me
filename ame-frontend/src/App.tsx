import { Layout, Menu } from 'antd';
import {
  HomeOutlined,
  BookOutlined,
  ClockCircleOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  ApartmentOutlined,
  SmileOutlined,
} from '@ant-design/icons';
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import KnowledgePage from './pages/KnowledgePage';
import MemoryPage from './pages/MemoryPage';
import ConfigPage from './pages/ConfigPage';
import WorkPage from './pages/WorkPage';
import GraphPage from './pages/GraphPage';
import CompanionPage from './pages/CompanionPage';
import { ErrorBoundary } from './components/common';

const { Header, Content, Sider } = Layout;

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { key: '/', icon: <HomeOutlined />, label: '首页' },
    { key: '/work', icon: <ThunderboltOutlined />, label: '💼 工作模式' },
    { key: '/life', icon: <SmileOutlined />, label: '🏠 生活模式' },
    { key: '/knowledge', icon: <BookOutlined />, label: 'RAG 知识库' },
    { key: '/graph', icon: <ApartmentOutlined />, label: '知识图谱' },
    { key: '/memory', icon: <ClockCircleOutlined />, label: '记忆管理' },
    { key: '/config', icon: <SettingOutlined />, label: '配置' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <img 
            src="/logo.png" 
            alt="Another Me Logo" 
            style={{ height: '120px', width: 'auto' }}
            onError={(e) => {
              // 如果 logo 加载失败，隐藏图片
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
          <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
            Another Me
          </div>
        </div>
      </Header>
      <Layout>
        <Sider width={200} theme="light">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key, item }) => {
              // 确保key是有效路径才导航
              if (key && typeof key === 'string' && key.startsWith('/')) {
                navigate(key);
              }
            }}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: '#fff',
              borderRadius: 8,
            }}
          >
            <ErrorBoundary>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/work" element={<WorkPage />} />
                <Route path="/life" element={<CompanionPage />} />
                <Route path="/knowledge" element={<KnowledgePage />} />
                <Route path="/graph" element={<GraphPage />} />
                <Route path="/memory" element={<MemoryPage />} />
                <Route path="/config" element={<ConfigPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </ErrorBoundary>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App;
