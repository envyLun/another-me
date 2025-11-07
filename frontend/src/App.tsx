import { Layout, Menu } from 'antd';
import {
  HomeOutlined,
  MessageOutlined,
  BookOutlined,
  ClockCircleOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  HeartOutlined,
} from '@ant-design/icons';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import KnowledgePage from './pages/KnowledgePage';
import MemoryPage from './pages/MemoryPage';
import ConfigPage from './pages/ConfigPage';
import WorkPage from './pages/WorkPage';
import LifePage from './pages/LifePage';

const { Header, Content, Sider } = Layout;

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { key: '/', icon: <HomeOutlined />, label: '首页' },
    { 
      key: 'modes',
      label: '场景模式',
      children: [
        { key: '/work', icon: <ThunderboltOutlined />, label: '💼 工作模式' },
        { key: '/life', icon: <HeartOutlined />, label: '🏡 生活模式' },
      ],
    },
    { key: '/chat', icon: <MessageOutlined />, label: 'MEM 对话' },
    { key: '/knowledge', icon: <BookOutlined />, label: 'RAG 知识库' },
    { key: '/memory', icon: <ClockCircleOutlined />, label: '记忆管理' },
    { key: '/config', icon: <SettingOutlined />, label: '配置' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          Another Me
        </div>
      </Header>
      <Layout>
        <Sider width={200} theme="light">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
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
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/work" element={<WorkPage />} />
              <Route path="/life" element={<LifePage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/knowledge" element={<KnowledgePage />} />
              <Route path="/memory" element={<MemoryPage />} />
              <Route path="/config" element={<ConfigPage />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App;
