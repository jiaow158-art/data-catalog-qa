import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Input, theme } from 'antd'
import { DatabaseOutlined, TableOutlined, SearchOutlined, RobotOutlined, ImportOutlined, ScheduleOutlined, NodeIndexOutlined, BarChartOutlined } from '@ant-design/icons'

const { Header, Sider, Content } = Layout

export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchValue, setSearchValue] = useState('')

  const currentPath = (() => {
    if (location.pathname.startsWith('/tables/')) return '/tables'
    if (location.pathname.startsWith('/columns/')) return '/tables'
    return location.pathname
  })()

  const menuItems = [

    { key: '/', icon: <DatabaseOutlined />, label: '数据库' },
    { key: '/tables', icon: <TableOutlined />, label: '表元数据' },
    { key: '/schedules', icon: <ScheduleOutlined />, label: '调度任务' },
    { key: '/lineage', icon: <NodeIndexOutlined />, label: '血缘图谱' },
    { key: '/reports', icon: <BarChartOutlined />, label: '报表管理' },
    { key: '/chat', icon: <RobotOutlined />, label: '智能问答' },
    { key: '/import', icon: <ImportOutlined />, label: '数据导入' },
  ]

  const handleSearch = (value: string) => {
    if (value.trim()) {
      navigate(`/tables?search=${encodeURIComponent(value.trim())}`)
    }
  }

  const {
    token: { colorBgContainer },
  } = theme.useToken()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={220}
        style={{ background: colorBgContainer }}
        breakpoint="lg"
        collapsedWidth="0"
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: 16,
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          元数据平台
        </div>
        <Menu
          mode="inline"
          selectedKeys={[currentPath]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            padding: '0 24px',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <Input.Search
            placeholder="全局搜索表名、字段名、任务名…"
            allowClear
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            onSearch={handleSearch}
            style={{ maxWidth: 480 }}
            prefix={<SearchOutlined />}
          />
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
