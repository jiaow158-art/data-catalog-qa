import { useCallback, useEffect, useState } from 'react'
import { Table, Tag, Input, Typography, Button, Popconfirm, message, Space } from 'antd'
import { SearchOutlined, ReloadOutlined, PlusOutlined, EditOutlined, DeleteOutlined, LinkOutlined } from '@ant-design/icons'
import { reportsApi } from '../api/client'
import ReportForm from '../components/ReportForm'
import type { Report } from '../types'

const biColor: Record<string, string> = {
  metabase: 'blue',
  superset: 'purple',
  tableau: 'cyan',
  finebi: 'green',
}

export default function ReportsPage() {
  const [data, setData] = useState<Report[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Report | null>(null)

  const fetchData = useCallback(
    async (p: number) => {
      setLoading(true)
      try {
        const res = await reportsApi.list({
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
      await reportsApi.delete(id)
      message.success('已删除')
      fetchData(page)
    } catch (err: any) {
      message.error(err?.message || '删除失败')
    }
  }

  const columns = [
    {
      title: '报表名称',
      dataIndex: 'report_name',
      key: 'report_name',
      render: (v: string, r: Report) => (
        <span>
          <span style={{ fontWeight: 500 }}>{v}</span>
          {r.report_url && (
            <a href={r.report_url} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 8 }}>
              <LinkOutlined />
            </a>
          )}
        </span>
      ),
    },
    {
      title: 'BI 工具',
      dataIndex: 'bi_tool',
      key: 'bi_tool',
      width: 120,
      render: (v: string | null) => v ? <Tag color={biColor[v] || 'default'}>{v}</Tag> : '-',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (v: string | null) => v || '-',
    },
    {
      title: '负责人',
      dataIndex: 'owner',
      key: 'owner',
      width: 100,
      render: (v: string | null) => v || '-',
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_: unknown, r: Report) => (
        <Space>
          <EditOutlined
            style={{ cursor: 'pointer', color: '#1677ff' }}
            onClick={() => { setEditing(r); setFormOpen(true) }}
          />
          <Popconfirm
            title="确定删除此报表？"
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
          报表管理 ({total})
        </Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => fetchData(page)}>刷新</Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => { setEditing(null); setFormOpen(true) }}
          >
            创建报表
          </Button>
        </Space>
      </div>
      <Input
        placeholder="搜索报表名称/描述"
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
      <ReportForm
        open={formOpen}
        editing={editing}
        onClose={() => setFormOpen(false)}
        onSuccess={() => fetchData(page)}
      />
    </div>
  )
}
