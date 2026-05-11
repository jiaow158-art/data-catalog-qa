import { useEffect } from 'react'
import { Modal, Form, Input, Select, InputNumber, Switch, message } from 'antd'
import { columnsApi } from '../api/client'
import type { ColumnItem } from '../types'

interface Props {
  open: boolean
  editing: ColumnItem | null
  tableId: string
  maxSortOrder: number
  onClose: () => void
  onSuccess: () => void
}

export default function ColumnForm({ open, editing, tableId, maxSortOrder, onClose, onSuccess }: Props) {
  const [form] = Form.useForm()
  const isEdit = !!editing

  useEffect(() => {
    if (open) {
      if (editing) {
        form.setFieldsValue(editing)
      } else {
        form.resetFields()
        form.setFieldsValue({
          table_id: tableId,
          sort_order: maxSortOrder + 1,
          is_primary_key: false,
          is_nullable: true,
        })
      }
    }
  }, [open, editing, tableId, maxSortOrder, form])

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (isEdit && editing) {
        const { table_id, ...rest } = values
        await columnsApi.update(editing.id, rest)
        message.success('字段已更新')
      } else {
        await columnsApi.create(values)
        message.success('字段已创建')
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
      title={isEdit ? '编辑字段' : '添加字段'}
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      destroyOnClose
      width={560}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item name="table_id" hidden><Input /></Form.Item>
        <Form.Item name="column_name" label="字段名" rules={[{ required: true, message: '请输入字段名' }]}>
          <Input placeholder="例: user_id" />
        </Form.Item>
        <Form.Item name="display_name" label="显示名称">
          <Input placeholder="例: 用户ID" />
        </Form.Item>
        <Form.Item name="data_type" label="数据类型">
          <Select
            allowClear
            placeholder="选择类型"
            options={[
              { value: 'string', label: 'string' },
              { value: 'bigint', label: 'bigint' },
              { value: 'int', label: 'int' },
              { value: 'decimal', label: 'decimal' },
              { value: 'boolean', label: 'boolean' },
              { value: 'date', label: 'date' },
              { value: 'timestamp', label: 'timestamp' },
            ]}
          />
        </Form.Item>
        <Form.Item name="description" label="说明">
          <Input placeholder="字段含义" />
        </Form.Item>
        <Form.Item name="calculation_rule" label="计算规则">
          <Input placeholder="例: original_price - discount_amount" />
        </Form.Item>
        <div style={{ display: 'flex', gap: 16 }}>
          <Form.Item name="is_primary_key" label="主键" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="is_nullable" label="可为空" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="sort_order" label="排序号">
            <InputNumber min={0} style={{ width: 80 }} />
          </Form.Item>
        </div>
      </Form>
    </Modal>
  )
}
