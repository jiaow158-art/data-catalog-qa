import { useCallback, useEffect, useState } from 'react'
import { Table, Tag, Input, Typography, Button, Popconfirm, message, Space } from 'antd'
import { SearchOutlined, ReloadOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { schedulesApi } from '../api/client'
import ScheduleForm from '../components/ScheduleForm'
import type { Schedule } from '../types'

const statusColor: Record<string, string> = {
  running: 'blue',
  success: 'green',
  failed: 'red',
  paused: 'orange',
}

const typeColor: Record<string, string> = {
  spark: 'purple',
  hive_sql: 'geekblue',
  python: 'cyan',
  shell: 'default',
}

export default function SchedulesPage() {
  const [data, setData] = useState<Schedule[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Schedule | null>(null)

  const fetchData = useCallback(
    async (p: number) => {
      setLoading(true)
      try {
        const res = await schedulesApi.list({
          search: search || undefined,
          page: p,
          size: 20,
        })
        setData(res.items)
        setTotal(res.total)
      } finally {
        setLoading(false)
      }
    },
    [search],
  )

  useEffect(() => {
    setPage(1)
    fetchData(1)
  }, [fetchData])

  const handleDelete = async (id: string) => {
    try {
      await schedulesApi.delete(id)
      message.success('已删除')
      fetchData(page)
    } catch (err: any) {
      message.error(err?.message || '删除失败')
    }
  }

  const columns = [
    {
      title: '任务名',
      dataIndex: 'task_name',
      key: 'task_name',
      render: (v: string) => <span style={{ fontWeight: 500 }}>{v}</span>,
    },
    {
      title: '类型',
      dataIndex: 'task_type',
      key: 'task_type',
      width: 100,
      render: (v: string | null) => v ? <Tag color={typeColor[v] || 'default'}>{v}</Tag> : '-',
    },
    {
      title: '调度说明',
      dataIndex: 'schedule_desc',
      key: 'schedule_desc',
      ellipsis: true,
      render: (v: string | null) => v || '-',
    },
    {
      title: 'Cron',
      dataIndex: 'schedule_cron',
      key: 'schedule_cron',
      width: 130,
      render: (v: string | null) => v ? <code>{v}</code> : '-',
    },
    {
      title: '负责人',
      dataIndex: 'owner',
      key: 'owner',
      width: 100,
      render: (v: string | null) => v || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      render: (v: string | null) => v ? <Tag color={statusColor[v] || 'default'}>{v}</Tag> : '-',
    },
    {
      title: '上次成功',
      dataIndex: 'last_success_time',
      key: 'last_success_time',
      width: 170,
      render: (v: string | null) => v || '-',
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_: unknown, r: Schedule) => (
        <Space>
          <EditOutlined
            style={{ cursor: 'pointer', color: '#1677ff' }}
            onClick={() => { setEditing(r); setFormOpen(true) }}
          />
          <Popconfirm
            title="确定删除此任务？"
            onConfirm={() => handleDelete(r.id)}
          >
            <DeleteOutlined style={{ cursor: 'pointer', color: '#ff4d4f' }} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>
          调度任务 ({total})
        </Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => fetchData(page)}>刷新</Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => { setEditing(null); setFormOpen(true) }}
          >
            创建任务
          </Button>
        </Space>
      </div>
      <Input
        placeholder="搜索任务名/说明"
        prefix={<SearchOutlined />}
        allowClear
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ width: 280, marginBottom: 16 }}
      />
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          total,
          pageSize: 20,
          showTotal: (t) => `共 ${t} 条`,
          onChange: (p) => {
            setPage(p)
            fetchData(p)
          },
        }}
      />
      <ScheduleForm
        open={formOpen}
        editing={editing}
        onClose={() => setFormOpen(false)}
        onSuccess={() => fetchData(page)}
      />
    </div>
  )
}
