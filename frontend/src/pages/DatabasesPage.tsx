import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Spin, Tag, Typography, Empty, Button, Popconfirm, message, Space } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, DatabaseOutlined } from '@ant-design/icons'
import { databasesApi } from '../api/client'
import DatabaseForm from '../components/DatabaseForm'
import type { Database } from '../types'

const typeColor: Record<string, string> = {
  hive: 'orange',
  mysql: 'blue',
  clickhouse: 'green',
  postgresql: 'cyan',
}

export default function DatabasesPage() {
  const [databases, setDatabases] = useState<Database[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Database | null>(null)
  const navigate = useNavigate()

  const fetchData = useCallback(() => {
    setLoading(true)
    databasesApi
      .list({ size: 100 })
      .then((res) => setDatabases(res.items))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const handleDelete = async (id: string) => {
    try {
      await databasesApi.delete(id)
      message.success('已删除')
      fetchData()
    } catch (err: any) {
      message.error(err?.message || '删除失败')
    }
  }

  if (loading) return <Spin style={{ display: 'block', marginTop: 80 }} size="large" />

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>
          数据库实例 ({databases.length})
        </Typography.Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => { setEditing(null); setFormOpen(true) }}
        >
          创建数据库
        </Button>
      </div>
      {!databases.length ? (
        <Empty description="暂无数据库，点击上方按钮创建" style={{ marginTop: 80 }} />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
          {databases.map((db) => (
            <Card
              key={db.id}
              hoverable
              onClick={() => navigate(`/tables?database_id=${db.id}`)}
              actions={[
                <EditOutlined
                  key="edit"
                  onClick={(e) => {
                    e.stopPropagation()
                    setEditing(db)
                    setFormOpen(true)
                  }}
                />,
                <Popconfirm
                  key="delete"
                  title="确定删除此数据库？"
                  description="关联的表和字段将一并删除"
                  onConfirm={(e) => {
                    e?.stopPropagation()
                    handleDelete(db.id)
                  }}
                  onCancel={(e) => e?.stopPropagation()}
                >
                  <DeleteOutlined onClick={(e) => e.stopPropagation()} />
                </Popconfirm>,
              ]}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <DatabaseOutlined style={{ fontSize: 28, color: '#1677ff' }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: 15 }}>{db.display_name || db.name}</div>
                  <div style={{ color: '#888', fontSize: 12 }}>{db.name}</div>
                </div>
                {db.db_type && <Tag color={typeColor[db.db_type] || 'default'}>{db.db_type}</Tag>}
              </div>
              {db.description && (
                <div style={{ marginTop: 12, color: '#666', fontSize: 13, lineHeight: 1.5 }}>
                  {db.description}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
      <DatabaseForm
        open={formOpen}
        editing={editing}
        onClose={() => setFormOpen(false)}
        onSuccess={fetchData}
      />
    </div>
  )
}
