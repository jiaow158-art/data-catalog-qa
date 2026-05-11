import { useState } from 'react'
import {
  Card,
  Input,
  Select,
  Button,
  Typography,
  Spin,
  Empty,
  Space,
  Tag,
  Table,
  Form,
  message,
  Popconfirm,
  Alert,
} from 'antd'
import { SearchOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import { lineageApi, tablesApi } from '../api/client'
import LineageGraph from '../components/LineageGraph'
import type { LineageGraphData, DirectLineage, TableItem } from '../types'

const { Title } = Typography

export default function LineagePage() {
  const [searchVal, setSearchVal] = useState('')
  const [searchResults, setSearchResults] = useState<TableItem[]>([])
  const [searching, setSearching] = useState(false)
  const [selectedTable, setSelectedTable] = useState<TableItem | null>(null)
  const [graphData, setGraphData] = useState<LineageGraphData | null>(null)
  const [directLineage, setDirectLineage] = useState<DirectLineage | null>(null)
  const [loadingGraph, setLoadingGraph] = useState(false)
  const [depth, setDepth] = useState(3)
  const [direction, setDirection] = useState<string>('both')

  // Create edge form state
  const [edgeFormOpen, setEdgeFormOpen] = useState(false)
  const [upstreamSearch, setUpstreamSearch] = useState('')
  const [downstreamSearch, setDownstreamSearch] = useState('')
  const [upstreamResults, setUpstreamResults] = useState<TableItem[]>([])
  const [downstreamResults, setDownstreamResults] = useState<TableItem[]>([])
  const [upstreamTable, setUpstreamTable] = useState<TableItem | null>(null)
  const [downstreamTable, setDownstreamTable] = useState<TableItem | null>(null)
  const [relationDesc, setRelationDesc] = useState('')
  const [creatingEdge, setCreatingEdge] = useState(false)

  const handleSearch = async () => {
    if (!searchVal.trim()) return
    setSearching(true)
    try {
      const res = await tablesApi.list({ search: searchVal, size: 10 })
      setSearchResults(res.items)
    } finally {
      setSearching(false)
    }
  }

  const loadGraph = async (table: TableItem) => {
    setSelectedTable(table)
    setLoadingGraph(true)
    try {
      const [graph, direct] = await Promise.all([
        lineageApi.getGraph(table.id, depth, direction),
        lineageApi.getDirect(table.id),
      ])
      setGraphData(graph)
      setDirectLineage(direct)
    } catch (err: any) {
      message.error(err?.message || '加载血缘失败')
    } finally {
      setLoadingGraph(false)
    }
  }

  const handleDeleteEdge = async (edgeId: string) => {
    try {
      await lineageApi.deleteTableEdge(edgeId)
      message.success('血缘关系已删除')
      if (selectedTable) loadGraph(selectedTable)
    } catch (err: any) {
      message.error(err?.message || '删除失败')
    }
  }

  const handleCreateEdge = async () => {
    if (!upstreamTable || !downstreamTable) {
      message.warning('请选择上下游表')
      return
    }
    setCreatingEdge(true)
    try {
      await lineageApi.createTableEdge({
        upstream_table_id: upstreamTable.id,
        downstream_table_id: downstreamTable.id,
        relation_desc: relationDesc || undefined,
      })
      message.success('血缘关系已创建')
      setEdgeFormOpen(false)
      setUpstreamTable(null)
      setDownstreamTable(null)
      setRelationDesc('')
      if (selectedTable) loadGraph(selectedTable)
    } catch (err: any) {
      message.error(err?.message || '创建失败')
    } finally {
      setCreatingEdge(false)
    }
  }

  const searchTableForField = async (q: string, setter: (v: TableItem[]) => void) => {
    if (!q.trim()) { setter([]); return }
    try {
      const res = await tablesApi.list({ search: q, size: 8 })
      setter(res.items)
    } catch {
      setter([])
    }
  }

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>血缘图谱</Title>

      {/* Search & controls */}
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Input.Search
              placeholder="搜索表名，然后选择要查看血缘的表"
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
              onSearch={handleSearch}
              enterButton={<><SearchOutlined /> 搜索</>}
              loading={searching}
              style={{ width: 400 }}
            />
            <Select
              value={depth}
              onChange={(v) => setDepth(v)}
              style={{ width: 120 }}
              options={[
                { value: 1, label: '深度 1' },
                { value: 2, label: '深度 2' },
                { value: 3, label: '深度 3' },
                { value: 4, label: '深度 4' },
                { value: 5, label: '深度 5' },
              ]}
            />
            <Select
              value={direction}
              onChange={(v) => {
                setDirection(v)
                if (selectedTable) {
                  lineageApi.getGraph(selectedTable.id, depth, v).then(setGraphData)
                }
              }}
              style={{ width: 130 }}
              options={[
                { value: 'both', label: '上下游' },
                { value: 'upstream', label: '仅上游' },
                { value: 'downstream', label: '仅下游' },
              ]}
            />
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setEdgeFormOpen(!edgeFormOpen)}
            >
              添加血缘
            </Button>
          </Space>

          {searchResults.length > 0 && (
            <div>
              <Typography.Text type="secondary" style={{ marginBottom: 4, display: 'block' }}>
                搜索结果，点击加载血缘：
              </Typography.Text>
              <Space wrap>
                {searchResults.map((t) => (
                  <Tag
                    key={t.id}
                    style={{ cursor: 'pointer' }}
                    color={selectedTable?.id === t.id ? 'blue' : 'default'}
                    onClick={() => {
                      loadGraph(t)
                      setSearchResults([])
                      setSearchVal('')
                    }}
                  >
                    {t.display_name || t.table_name}
                  </Tag>
                ))}
              </Space>
            </div>
          )}
        </Space>
      </Card>

      {/* Edge creation form */}
      {edgeFormOpen && (
        <Card title="添加血缘关系" size="small" style={{ marginBottom: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ display: 'flex', gap: 16 }}>
              <div style={{ flex: 1 }}>
                <Typography.Text strong>上游表</Typography.Text>
                <Input.Search
                  placeholder="搜索上游表"
                  value={upstreamSearch}
                  onChange={(e) => {
                    setUpstreamSearch(e.target.value)
                    searchTableForField(e.target.value, setUpstreamResults)
                  }}
                  style={{ marginTop: 4 }}
                />
                {upstreamResults.length > 0 && (
                  <div style={{ marginTop: 4 }}>
                    {upstreamResults.map((t) => (
                      <Tag
                        key={t.id}
                        style={{ cursor: 'pointer' }}
                        color={upstreamTable?.id === t.id ? 'blue' : 'default'}
                        onClick={() => {
                          setUpstreamTable(t)
                          setUpstreamResults([])
                          setUpstreamSearch(t.display_name || t.table_name)
                        }}
                      >
                        {t.display_name || t.table_name}
                      </Tag>
                    ))}
                  </div>
                )}
                {upstreamTable && (
                  <Alert
                    type="info"
                    message={`已选: ${upstreamTable.display_name || upstreamTable.table_name}`}
                    style={{ marginTop: 4 }}
                    closable
                    onClose={() => { setUpstreamTable(null); setUpstreamSearch('') }}
                  />
                )}
              </div>
              <div style={{ flex: 1 }}>
                <Typography.Text strong>下游表</Typography.Text>
                <Input.Search
                  placeholder="搜索下游表"
                  value={downstreamSearch}
                  onChange={(e) => {
                    setDownstreamSearch(e.target.value)
                    searchTableForField(e.target.value, setDownstreamResults)
                  }}
                  style={{ marginTop: 4 }}
                />
                {downstreamResults.length > 0 && (
                  <div style={{ marginTop: 4 }}>
                    {downstreamResults.map((t) => (
                      <Tag
                        key={t.id}
                        style={{ cursor: 'pointer' }}
                        color={downstreamTable?.id === t.id ? 'blue' : 'default'}
                        onClick={() => {
                          setDownstreamTable(t)
                          setDownstreamResults([])
                          setDownstreamSearch(t.display_name || t.table_name)
                        }}
                      >
                        {t.display_name || t.table_name}
                      </Tag>
                    ))}
                  </div>
                )}
                {downstreamTable && (
                  <Alert
                    type="info"
                    message={`已选: ${downstreamTable.display_name || downstreamTable.table_name}`}
                    style={{ marginTop: 4 }}
                    closable
                    onClose={() => { setDownstreamTable(null); setDownstreamSearch('') }}
                  />
                )}
              </div>
            </div>
            <Input
              placeholder="关系描述（可选）"
              value={relationDesc}
              onChange={(e) => setRelationDesc(e.target.value)}
            />
            <Space>
              <Button type="primary" loading={creatingEdge} onClick={handleCreateEdge}>
                确认添加
              </Button>
              <Button onClick={() => setEdgeFormOpen(false)}>取消</Button>
            </Space>
          </Space>
        </Card>
      )}

      {/* Lineage graph */}
      {loadingGraph ? (
        <Spin style={{ display: 'block', marginTop: 48 }} />
      ) : graphData && graphData.nodes.length > 0 ? (
        <>
          <Card
            title={selectedTable ? `${selectedTable.display_name || selectedTable.table_name} 血缘图` : '血缘图'}
            style={{ marginBottom: 16 }}
            extra={
              selectedTable ? (
                <Space>
                  <Tag color="orange">焦点</Tag>
                  <Typography.Text type="secondary">
                    节点 {graphData.nodes.length} / 边 {graphData.edges.length}
                  </Typography.Text>
                </Space>
              ) : null
            }
          >
            <div style={{ height: 520 }}>
              <LineageGraph nodes={graphData.nodes} edges={graphData.edges} />
            </div>
          </Card>

          {/* Edge list */}
          {directLineage && directLineage.edges.length > 0 && (
            <Card title="血缘关系列表" size="small">
              <Table
                dataSource={directLineage.edges}
                rowKey="id"
                size="small"
                pagination={false}
                columns={[
                  {
                    title: '关系描述',
                    dataIndex: 'relation_desc',
                    key: 'relation_desc',
                    render: (v: string | null) => v || '-',
                  },
                  {
                    title: '操作',
                    key: 'actions',
                    width: 80,
                    render: (_: unknown, r: { id: string }) => (
                      <Popconfirm
                        title="确定删除此血缘关系？"
                        onConfirm={() => handleDeleteEdge(r.id)}
                      >
                        <DeleteOutlined style={{ cursor: 'pointer', color: '#ff4d4f' }} />
                      </Popconfirm>
                    ),
                  },
                ]}
              />
            </Card>
          )}
        </>
      ) : (
        <Card>
          <Empty description="请搜索并选择一个表来查看血缘关系" />
        </Card>
      )}
    </div>
  )
}
