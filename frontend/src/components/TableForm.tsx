import { useEffect, useState } from 'react'
import { Modal, Form, Input, Select, InputNumber, message } from 'antd'
import { tablesApi, databasesApi } from '../api/client'
import type { TableItem, Database } from '../types'

interface Props {
  open: boolean
  editing: TableItem | null
  databaseId?: string
  onClose: () => void
  onSuccess: () => void
}

export default function TableForm({ open, editing, databaseId, onClose, onSuccess }: Props) {
  const [form] = Form.useForm()
  const [dbs, setDbs] = useState<Database[]>([])
  const isEdit = !!editing

  useEffect(() => {
    databasesApi.list({ size: 100 }).then((res) => setDbs(res.items))
  }, [])

  useEffect(() => {
    if (open) {
      if (editing) {
        form.setFieldsValue(editing)
      } else {
        form.resetFields()
        if (databaseId) form.setFieldValue('database_id', databaseId)
      }
    }
  }, [open, editing, databaseId, form])

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (isEdit && editing) {
        // Don't send database_id on update
        const { database_id, ...rest } = values
        await tablesApi.update(editing.id, rest)
        message.success('表已更新')
      } else {
        await tablesApi.create(values)
        message.success('表已创建')
      }
      onSuccess()
      onClose()
    } catch (err: any) {
      if (err?.errorFields) return
      message.error(err?.message || '操作失败')
    }
  }

  return (
    <Modal
      title={isEdit ? '编辑表' : '创建表'}
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      destroyOnClose
      width={600}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        {!isEdit && (
          <Form.Item
            name="database_id"
            label="所属数据库"
            rules={[{ required: true, message: '请选择数据库' }]}
          >
            <Select
              placeholder="选择数据库"
              options={dbs.map((d) => ({ value: d.id, label: `${d.display_name || d.name} (${d.name})` }))}
            />
          </Form.Item>
        )}
        <Form.Item name="table_name" label="表名" rules={[{ required: true, message: '请输入表名' }]}>
          <Input placeholder="例: ods_order_info" />
        </Form.Item>
        <Form.Item name="display_name" label="显示名称">
          <Input placeholder="例: 订单原始表" />
        </Form.Item>
        <Form.Item name="table_type" label="表类型">
          <Select
            allowClear
            placeholder="选择类型"
            options={[
              { value: 'fact', label: 'fact' },
              { value: 'dim', label: 'dim' },
              { value: 'dwd', label: 'dwd' },
              { value: 'dws', label: 'dws' },
              { value: 'ads', label: 'ads' },
            ]}
          />
        </Form.Item>
        <Form.Item name="owner" label="负责人">
          <Input placeholder="例: 张三" />
        </Form.Item>
        <Form.Item name="partition_key" label="分区键">
          <Input placeholder="例: dt" />
        </Form.Item>
        <Form.Item name="partition_freq" label="分区频率">
          <Select
            allowClear
            placeholder="选择频率"
            options={[
              { value: 'hourly', label: '每小时' },
              { value: 'daily', label: '每天' },
              { value: 'monthly', label: '每月' },
              { value: 'yearly', label: '每年' },
            ]}
          />
        </Form.Item>
        <Form.Item name="row_count_estimate" label="预估行数">
          <InputNumber style={{ width: '100%' }} placeholder="例: 500000000" />
        </Form.Item>
        <Form.Item name="description" label="描述">
          <Input.TextArea rows={2} placeholder="表用途说明" />
        </Form.Item>
        <Form.Item name="usage_notes" label="使用说明">
          <Input.TextArea rows={2} placeholder="查询注意事项" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
