import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Descriptions, Tag, Typography, Table, Spin, Alert, Button, Space } from 'antd'
import { ArrowLeftOutlined, TableOutlined } from '@ant-design/icons'
import { columnsApi, lineageApi } from '../api/client'
import type { ColumnItem, ColumnLineage } from '../types'

const { Title } = Typography

export default function ColumnDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [column, setColumn] = useState<ColumnItem | null>(null)
  const [lineage, setLineage] = useState<ColumnLineage | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([
      columnsApi.get(id),
      lineageApi.getColumnLineage(id).catch(() => null),
    ])
      .then(([col, lin]) => {
        setColumn(col)
        setLineage(lin)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <Spin style={{ display: 'block', marginTop: 48 }} />
  if (error) return <Alert type="error" message={error} />
  if (!column) return <Alert type="warning" message="字段不存在" />

  const enumValues = (() => {
    if (!column.enum_values) return null
    try {
      const arr = JSON.parse(column.enum_values)
      return Array.isArray(arr) ? arr : null
    } catch {
      return null
    }
  })()

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>返回</Button>
      </Space>

      <Card style={{ marginBottom: 16 }}>
        <Title level={4} style={{ marginBottom: 16 }}>
          <TableOutlined style={{ marginRight: 8 }} />
          {column.display_name || column.column_name}
        </Title>
        <Descriptions bordered column={{ xs: 1, sm: 2 }}>
          <Descriptions.Item label="字段名">{column.column_name}</Descriptions.Item>
          <Descriptions.Item label="显示名称">{column.display_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="数据类型">
            {column.data_type ? <code>{column.data_type}</code> : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="排序号">{column.sort_order}</Descriptions.Item>
          <Descriptions.Item label="主键">
            <Tag color={column.is_primary_key ? 'red' : 'default'}>
              {column.is_primary_key ? '是' : '否'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="可为空">
            <Tag color={column.is_nullable ? 'blue' : 'default'}>
              {column.is_nullable ? '是' : '否'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="默认值">{column.default_value || '-'}</Descriptions.Item>
          <Descriptions.Item label="空值率">
            {column.null_rate != null ? `${(column.null_rate * 100).toFixed(1)}%` : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="唯一值数量">{column.distinct_count ?? '-'}</Descriptions.Item>
          <Descriptions.Item label="枚举值" span={2}>
            {enumValues ? (
              <Space wrap>
                {enumValues.map((v: string, i: number) => (
                  <Tag key={i}>{v}</Tag>
                ))}
              </Space>
            ) : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="计算规则" span={2}>
            {column.calculation_rule ? <code>{column.calculation_rule}</code> : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="来源信息" span={2}>
            {column.source_info || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="描述" span={2}>
            {column.description || '-'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Column-level lineage */}
      {lineage && (lineage.upstream.length > 0 || lineage.downstream.length > 0) && (
        <Card title="字段级血缘" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', gap: 24 }}>
            <div style={{ flex: 1 }}>
              <Title level={5}>上游字段</Title>
              {lineage.upstream.length > 0 ? (
                <Table
                  dataSource={lineage.upstream}
                  rowKey="id"
                  size="small"
                  pagination={false}
                  columns={[
                    { title: '字段名', dataIndex: 'column_name', key: 'column_name' },
                    { title: '显示名称', dataIndex: 'display_name', key: 'display_name' },
                    { title: '所属表', dataIndex: 'table_name', key: 'table_name' },
                  ]}
                />
              ) : (
                <Typography.Text type="secondary">无上游字段</Typography.Text>
              )}
            </div>
            <div style={{ flex: 1 }}>
              <Title level={5}>下游字段</Title>
              {lineage.downstream.length > 0 ? (
                <Table
                  dataSource={lineage.downstream}
                  rowKey="id"
                  size="small"
                  pagination={false}
                  columns={[
                    { title: '字段名', dataIndex: 'column_name', key: 'column_name' },
                    { title: '显示名称', dataIndex: 'display_name', key: 'display_name' },
                    { title: '所属表', dataIndex: 'table_name', key: 'table_name' },
                  ]}
                />
              ) : (
                <Typography.Text type="secondary">无下游字段</Typography.Text>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
