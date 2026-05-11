import { useCallback, useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Table, Tag, Input, Select, Typography, Button, Popconfirm, message, Space } from 'antd'
import { SearchOutlined, ReloadOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { tablesApi } from '../api/client'
import TableForm from '../components/TableForm'
import type { TableItem } from '../types'

const typeColor: Record<string, string> = {
  fact: 'red',
  dim: 'blue',
  dwd: 'purple',
  dws: 'geekblue',
  ads: 'green',
}

export default function TablesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [data, setData] = useState<TableItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<TableItem | null>(null)
  const navigate = useNavigate()

  const databaseId = searchParams.get('database_id') || undefined
  const search = searchParams.get('search') || undefined
  const tableType = searchParams.get('table_type') || undefined

  const fetchData = useCallback(
    async (p: number) => {
      setLoading(true)
      try {
        const res = await tablesApi.list({
          database_id: databaseId,
          search,
          table_type: tableType,
          page: p,
          size: 20,
        })
        setData(res.items)
        setTotal(res.total)
      } finally {
        setLoading(false)
      }
    },
    [databaseId, search, tableType],
  )

  useEffect(() => {
    setPage(1)
    fetchData(1)
  }, [fetchData])

  const updateFilter = (key: string, value: string | undefined) => {
    const sp = new URLSearchParams(searchParams)
    if (value) sp.set(key, value)
    else sp.delete(key)
    setSearchParams(sp)
  }

  const handleDelete = async (id: string) => {
    try {
      await tablesApi.delete(id)
      message.success('已删除')
      fetchData(page)
    } catch (err: any) {
      message.error(err?.message || '删除失败')
    }
  }

  const columns = [
    {
      title: '表名',
      dataIndex: 'table_name',
      key: 'table_name',
      render: (_: string, r: TableItem) => (
        <a onClick={() => navigate(`/tables/${r.id}`)} style={{ fontWeight: 500 }}>
          {r.display_name || r.table_name}
        </a>
      ),
    },
    {
      title: '类型',
      dataIndex: 'table_type',
      key: 'table_type',
      width: 80,
      render: (v: string | null) => v ? <Tag color={typeColor[v] || 'default'}>{v}</Tag> : '-',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (v: string | null) => v || '-',
    },
    {
      title: '分区频率',
      dataIndex: 'partition_freq',
      key: 'partition_freq',
      width: 100,
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
      render: (_: unknown, r: TableItem) => (
        <Space>
          <EditOutlined
            style={{ cursor: 'pointer', color: '#1677ff' }}
            onClick={() => { setEditing(r); setFormOpen(true) }}
          />
          <Popconfirm
            title="确定删除此表？"
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
          表元数据 ({total})
        </Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => fetchData(page)}>刷新</Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => { setEditing(null); setFormOpen(true) }}
          >
            创建表
          </Button>
        </Space>
      </div>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索表名/描述"
          prefix={<SearchOutlined />}
          allowClear
          value={search || ''}
          onChange={(e) => updateFilter('search', e.target.value || undefined)}
          style={{ width: 240 }}
        />
        <Select
          placeholder="表类型"
          allowClear
          value={tableType}
          onChange={(v) => updateFilter('table_type', v)}
          style={{ width: 120 }}
          options={[
            { value: 'fact', label: 'fact' },
            { value: 'dim', label: 'dim' },
            { value: 'dwd', label: 'dwd' },
            { value: 'dws', label: 'dws' },
            { value: 'ads', label: 'ads' },
          ]}
        />
      </Space>
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
      <TableForm
        open={formOpen}
        editing={editing}
        databaseId={databaseId}
        onClose={() => setFormOpen(false)}
        onSuccess={() => fetchData(page)}
      />
    </div>
  )
}
