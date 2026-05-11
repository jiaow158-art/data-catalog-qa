import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Descriptions,
  Table,
  Tag,
  Tabs,
  Spin,
  Typography,
  Button,
  Space,
  Card,
  Empty,
  Popconfirm,
  message,
} from 'antd'
import { ArrowLeftOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { tablesApi, columnsApi, lineageApi, type LineageGraphData } from '../api/client'
import ColumnForm from '../components/ColumnForm'
import LineageGraph from '../components/LineageGraph'
import type { TableDetail, ColumnItem } from '../types'

const typeColor: Record<string, string> = {
  fact: 'red',
  dim: 'blue',
  dwd: 'purple',
  dws: 'geekblue',
  ads: 'green',
}

const statusColor: Record<string, string> = {
  success: 'green',
  running: 'blue',
  failed: 'red',
}

export default function TableDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<TableDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [colFormOpen, setColFormOpen] = useState(false)
  const [editingCol, setEditingCol] = useState<ColumnItem | null>(null)
  const [graphData, setGraphData] = useState<LineageGraphData | null>(null)

  const fetchData = useCallback(() => {
    if (!id) return
    setLoading(true)
    Promise.all([
      tablesApi.getDetail(id),
      lineageApi.getGraph(id, 3, 'both').catch(() => null),
    ])
      .then(([table, graph]) => {
        setData(table)
        setGraphData(graph)
      })
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => { fetchData() }, [fetchData])

  const handleDeleteCol = async (colId: string) => {
    try {
      await columnsApi.delete(colId)
      message.success('字段已删除')
      fetchData()
    } catch (err: any) {
      message.error(err?.message || '删除失败')
    }
  }

  if (loading) return <Spin style={{ display: 'block', marginTop: 80 }} size="large" />
  if (!data) return <Empty description="表不存在" style={{ marginTop: 80 }} />

  const columnColumns = [
    { title: '#', dataIndex: 'sort_order', key: 'sort_order', width: 50 },
    {
      title: '字段名',
      dataIndex: 'column_name',
      key: 'column_name',
      width: 180,
      render: (v: string, r: ColumnItem) => (
        <span>
          {r.is_primary_key && <Tag color="gold" style={{ marginRight: 4 }}>PK</Tag>}
          <a onClick={() => navigate(`/columns/${r.id}`)}>{r.display_name || v}</a>
        </span>
      ),
    },
    { title: '类型', dataIndex: 'data_type', key: 'data_type', width: 100, render: (v: string | null) => v || '-' },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (v: string | null) => v || '-',
    },
    {
      title: '计算规则',
      dataIndex: 'calculation_rule',
      key: 'calculation_rule',
      ellipsis: true,
      width: 200,
      render: (v: string | null) => v || '-',
    },
    {
      title: '操作',
      key: 'actions',
      width: 90,
      render: (_: unknown, r: ColumnItem) => (
        <Space>
          <EditOutlined
            style={{ cursor: 'pointer', color: '#1677ff' }}
            onClick={() => { setEditingCol(r); setColFormOpen(true) }}
          />
          <Popconfirm title="删除此字段？" onConfirm={() => handleDeleteCol(r.id)}>
            <DeleteOutlined style={{ cursor: 'pointer', color: '#ff4d4f' }} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const scheduleColumns = [
    { title: '任务名', dataIndex: 'task_name', key: 'task_name' },
    { title: '描述', dataIndex: 'schedule_desc', key: 'schedule_desc', ellipsis: true },
    { title: '最近成功', dataIndex: 'last_success_time', key: 'last_success_time', width: 170,
      render: (v: string | null) => (v ? new Date(v).toLocaleString() : '-') },
    { title: '状态', dataIndex: 'status', key: 'status', width: 80,
      render: (v: string | null) => v ? <Tag color={statusColor[v] || 'default'}>{v}</Tag> : '-' },
  ]

  const lineageColumns = [
    { title: '表名', dataIndex: 'table_name', key: 'table_name',
      render: (v: string, r: any) => r.display_name || v },
  ]

  const tabItems = [
    {
      key: 'columns',
      label: `字段 (${data.columns.length})`,
      children: (
        <div>
          <div style={{ marginBottom: 12 }}>
            <Button
              type="primary"
              size="small"
              icon={<PlusOutlined />}
              onClick={() => { setEditingCol(null); setColFormOpen(true) }}
            >
              添加字段
            </Button>
          </div>
          <Table
            columns={columnColumns}
            dataSource={data.columns}
            rowKey="id"
            pagination={false}
            size="middle"
          />
        </div>
      ),
    },
    {
      key: 'schedules',
      label: `调度任务 (${data.schedules.length})`,
      children: data.schedules.length ? (
        <Table columns={scheduleColumns} dataSource={data.schedules} rowKey="id" pagination={false} size="middle" />
      ) : (
        <Empty description="暂无关联调度任务" />
      ),
    },
    {
      key: 'lineage',
      label: `血缘 (${graphData ? graphData.nodes.length - 1 : data.upstream_tables.length + data.downstream_tables.length})`,
      children: graphData && graphData.nodes.length > 0 ? (
        <div>
          <div style={{ marginBottom: 8, display: 'flex', gap: 12, alignItems: 'center' }}>
            <Tag color="red">fact</Tag><Tag color="blue">dim</Tag>
            <Tag color="purple">dwd</Tag><Tag color="geekblue">dws</Tag>
            <Tag color="green">ads</Tag>
            <span style={{ color: '#888', fontSize: 12, marginLeft: 8 }}>
              共 {graphData.nodes.length} 个节点 · {graphData.edges.length} 条边 · 深度 3 跳 · 点击节点跳转详情
            </span>
          </div>
          <LineageGraph nodes={graphData.nodes} edges={graphData.edges} />
        </div>
      ) : !data.upstream_tables.length && !data.downstream_tables.length ? (
        <Empty description="暂无血缘数据" />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <Card title={`上游表 (${data.upstream_tables.length})`} size="small">
            {data.upstream_tables.length ? (
              <Table columns={lineageColumns} dataSource={data.upstream_tables} rowKey="id" pagination={false} size="small" />
            ) : (
              <Empty description="无上游依赖" />
            )}
          </Card>
          <Card title={`下游表 (${data.downstream_tables.length})`} size="small">
            {data.downstream_tables.length ? (
              <Table columns={lineageColumns} dataSource={data.downstream_tables} rowKey="id" pagination={false} size="small" />
            ) : (
              <Empty description="无下游依赖" />
            )}
          </Card>
        </div>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>返回</Button>
        <Typography.Title level={4} style={{ margin: 0 }}>
          {data.display_name || data.table_name}
        </Typography.Title>
        {data.table_type && <Tag color={typeColor[data.table_type] || 'default'}>{data.table_type}</Tag>}
      </Space>
      <Descriptions bordered column={2} size="small" style={{ marginBottom: 24 }}>
        <Descriptions.Item label="表名">{data.table_name}</Descriptions.Item>
        <Descriptions.Item label="负责人">{data.owner || '-'}</Descriptions.Item>
        <Descriptions.Item label="分区键">{data.partition_key || '-'}</Descriptions.Item>
        <Descriptions.Item label="分区频率">{data.partition_freq || '-'}</Descriptions.Item>
        <Descriptions.Item label="预估行数">
          {data.row_count_estimate ? data.row_count_estimate.toLocaleString() : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="主键">{data.primary_keys || '-'}</Descriptions.Item>
        <Descriptions.Item label="标签">{data.tags || '-'}</Descriptions.Item>
        <Descriptions.Item label="业务场景">{data.business_scenarios || '-'}</Descriptions.Item>
        <Descriptions.Item label="描述" span={2}>{data.description || '-'}</Descriptions.Item>
        <Descriptions.Item label="使用说明" span={2}>{data.usage_notes || '-'}</Descriptions.Item>
      </Descriptions>
      <Tabs items={tabItems} />
      <ColumnForm
        open={colFormOpen}
        editing={editingCol}
        tableId={id!}
        maxSortOrder={data.columns.length}
        onClose={() => setColFormOpen(false)}
        onSuccess={fetchData}
      />
    </div>
  )
}
