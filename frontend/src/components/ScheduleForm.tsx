import { useEffect } from 'react'
import { Modal, Form, Input, Select, message } from 'antd'
import { schedulesApi } from '../api/client'
import type { Schedule } from '../types'

interface Props {
  open: boolean
  editing: Schedule | null
  onClose: () => void
  onSuccess: () => void
}

export default function ScheduleForm({ open, editing, onClose, onSuccess }: Props) {
  const [form] = Form.useForm()
  const isEdit = !!editing

  useEffect(() => {
    if (open) {
      if (editing) {
        form.setFieldsValue({
          task_name: editing.task_name,
          task_type: editing.task_type,
          schedule_cron: editing.schedule_cron,
          schedule_desc: editing.schedule_desc,
          owner: editing.owner,
          status: editing.status,
          task_config: editing.task_config,
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
        const { task_name, ...rest } = values
        await schedulesApi.update(editing.id, rest)
        message.success('任务已更新')
      } else {
        await schedulesApi.create(values)
        message.success('任务已创建')
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
      title={isEdit ? '编辑调度任务' : '创建调度任务'}
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      destroyOnClose
      width={560}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item name="task_name" label="任务名" rules={[{ required: true, message: '请输入任务名' }]}>
          <Input placeholder="例: dwd_order_info_daily" disabled={isEdit} />
        </Form.Item>
        <Form.Item name="task_type" label="任务类型">
          <Select
            allowClear
            placeholder="选择类型"
            options={[
              { value: 'spark', label: 'Spark' },
              { value: 'hive_sql', label: 'Hive SQL' },
              { value: 'python', label: 'Python' },
              { value: 'shell', label: 'Shell' },
            ]}
          />
        </Form.Item>
        <Form.Item name="schedule_cron" label="Cron 表达式">
          <Input placeholder="例: 0 6 * * *" />
        </Form.Item>
        <Form.Item name="schedule_desc" label="调度说明">
          <Input placeholder="例: 每天凌晨6点执行" />
        </Form.Item>
        <Form.Item name="owner" label="负责人">
          <Input placeholder="例: 张三" />
        </Form.Item>
        <Form.Item name="status" label="状态">
          <Select
            allowClear
            placeholder="选择状态"
            options={[
              { value: 'running', label: '运行中' },
              { value: 'success', label: '成功' },
              { value: 'failed', label: '失败' },
              { value: 'paused', label: '已暂停' },
            ]}
          />
        </Form.Item>
        <Form.Item name="task_config" label="任务配置 (JSON)">
          <Input.TextArea rows={2} placeholder='{"spark.executor.memory": "4g"}' />
        </Form.Item>
      </Form>
    </Modal>
  )
}
