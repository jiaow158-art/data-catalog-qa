import { useEffect } from 'react'
import { Modal, Form, Input, Select, message } from 'antd'
import { databasesApi } from '../api/client'
import type { Database } from '../types'

interface Props {
  open: boolean
  editing: Database | null
  onClose: () => void
  onSuccess: () => void
}

export default function DatabaseForm({ open, editing, onClose, onSuccess }: Props) {
  const [form] = Form.useForm()
  const isEdit = !!editing

  useEffect(() => {
    if (open) {
      if (editing) {
        form.setFieldsValue(editing)
      } else {
        form.resetFields()
      }
    }
  }, [open, editing, form])

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (isEdit && editing) {
        await databasesApi.update(editing.id, values)
        message.success('数据库已更新')
      } else {
        await databasesApi.create(values)
        message.success('数据库已创建')
      }
      onSuccess()
      onClose()
    } catch (err: any) {
      if (err?.errorFields) return // form validation error
      message.error(err?.message || '操作失败')
    }
  }

  return (
    <Modal
      title={isEdit ? '编辑数据库' : '创建数据库'}
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      destroyOnClose
      width={520}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item name="name" label="库名" rules={[{ required: true, message: '请输入库名' }]}>
          <Input placeholder="例: ods, dwd, dim, ads" />
        </Form.Item>
        <Form.Item name="display_name" label="显示名称">
          <Input placeholder="例: 原始数据层" />
        </Form.Item>
        <Form.Item name="db_type" label="数据库类型">
          <Select
            allowClear
            placeholder="选择类型"
            options={[
              { value: 'hive', label: 'Hive' },
              { value: 'mysql', label: 'MySQL' },
              { value: 'clickhouse', label: 'ClickHouse' },
              { value: 'postgresql', label: 'PostgreSQL' },
            ]}
          />
        </Form.Item>
        <Form.Item name="host" label="主机地址">
          <Input placeholder="例: hive-prod-01:10000" />
        </Form.Item>
        <Form.Item name="description" label="描述">
          <Input.TextArea rows={3} placeholder="数据库用途说明" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
