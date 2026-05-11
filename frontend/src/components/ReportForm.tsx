import { useEffect } from 'react'
import { Modal, Form, Input, Select, message } from 'antd'
import { reportsApi } from '../api/client'
import type { Report } from '../types'

interface Props {
  open: boolean
  editing: Report | null
  onClose: () => void
  onSuccess: () => void
}

export default function ReportForm({ open, editing, onClose, onSuccess }: Props) {
  const [form] = Form.useForm()
  const isEdit = !!editing

  useEffect(() => {
    if (open) {
      if (editing) {
        form.setFieldsValue({
          report_name: editing.report_name,
          report_url: editing.report_url,
          bi_tool: editing.bi_tool,
          description: editing.description,
          owner: editing.owner,
        })
      } else {
        form.resetFields()
      }
    }
  }, [open, editing, form])

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (isEdit && editing) {
        await reportsApi.update(editing.id, values)
        message.success('报表已更新')
      } else {
        await reportsApi.create(values)
        message.success('报表已创建')
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
      title={isEdit ? '编辑报表' : '创建报表'}
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      destroyOnClose
      width={520}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item name="report_name" label="报表名称" rules={[{ required: true, message: '请输入报表名称' }]}>
          <Input placeholder="例: 日销售额看板" />
        </Form.Item>
        <Form.Item name="bi_tool" label="BI 工具">
          <Select
            allowClear
            placeholder="选择 BI 工具"
            options={[
              { value: 'metabase', label: 'Metabase' },
              { value: 'superset', label: 'Superset' },
              { value: 'tableau', label: 'Tableau' },
              { value: 'finebi', label: 'FineBI' },
            ]}
          />
        </Form.Item>
        <Form.Item name="report_url" label="报表链接">
          <Input placeholder="例: https://metabase.internal/dashboard/42" />
        </Form.Item>
        <Form.Item name="owner" label="负责人">
          <Input placeholder="例: 张三" />
        </Form.Item>
        <Form.Item name="description" label="描述">
          <Input.TextArea rows={2} placeholder="报表用途说明" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
