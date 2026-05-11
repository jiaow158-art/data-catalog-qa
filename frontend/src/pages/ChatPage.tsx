import { useState, useRef, useEffect } from 'react'
import { Input, Button, Card, Typography, Tag, Space, Spin, Switch, Modal, Form, message } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined, ClearOutlined, SettingOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { qaApi, type QaResponse } from '../api/client'
import type { LLMConfig } from '../types'

interface Message {
  role: 'user' | 'assistant'
  content: string
  intent?: string
  confidence?: number
  entities?: Record<string, string | null>
  used_llm?: boolean
}

const suggestedQuestions = [
  '有哪些数据库？',
  'ods 库有哪些表？',
  'dwd_order_detail 的上游是什么？',
  '订单原始表有哪些字段？',
  '有哪些调度任务失败了？',
]

const intentLabels: Record<string, string> = {
  list_databases: '查库',
  list_tables: '查表',
  table_detail: '表详情',
  table_columns: '查字段',
  table_lineage: '血缘',
  table_schedules: '调度',
  search: '搜索',
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [useLlm, setUseLlm] = useState(false)
  const [llmAvailable, setLlmAvailable] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [llmConfig, setLlmConfig] = useState<LLMConfig | null>(null)
  const [savingConfig, setSavingConfig] = useState(false)
  const [testingConn, setTestingConn] = useState(false)
  const [settingsForm] = Form.useForm()
  const bottomRef = useRef<HTMLDivElement>(null)

  // Fetch LLM config on mount
  useEffect(() => {
    qaApi.getConfig()
      .then((cfg) => {
        setLlmConfig(cfg)
        setLlmAvailable(cfg.api_key_configured)
      })
      .catch(() => {})
  }, [])

  // Refresh config after settings change
  const refreshConfig = async () => {
    try {
      const cfg = await qaApi.getConfig()
      setLlmConfig(cfg)
      setLlmAvailable(cfg.api_key_configured)
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (text?: string) => {
    const question = (text || input).trim()
    if (!question || loading) return

    const userMsg: Message = { role: 'user', content: question }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const data = await qaApi.ask(question, useLlm)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          intent: data.intent,
          confidence: data.confidence,
          entities: data.entities,
          used_llm: data.used_llm,
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '抱歉，请求失败了，请检查后端服务是否在运行。' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => setMessages([])

  const openSettings = () => {
    if (llmConfig) {
      settingsForm.setFieldsValue({
        model: llmConfig.model,
        base_url: llmConfig.base_url,
        api_key: '',
      })
    }
    setSettingsOpen(true)
  }

  const handleSaveConfig = async () => {
    try {
      const values = await settingsForm.validateFields()
      setSavingConfig(true)
      const payload: Record<string, string> = {}
      if (values.model) payload.model = values.model
      if (values.base_url) payload.base_url = values.base_url
      if (values.api_key) payload.api_key = values.api_key
      await qaApi.updateConfig(payload)
      await refreshConfig()
      message.success('配置已更新')
      setSettingsOpen(false)
    } catch (err: any) {
      if (err?.errorFields) return
      message.error(err?.message || '保存失败')
    } finally {
      setSavingConfig(false)
    }
  }

  const handleTestConfig = async () => {
    try {
      const values = settingsForm.getFieldsValue()
      setTestingConn(true)
      const result = await qaApi.testConfig({
        api_key: values.api_key || undefined,
        base_url: values.base_url || undefined,
        model: values.model || undefined,
      })
      if (result.ok) {
        message.success(`连接成功 | ${result.model} | 延迟 ${result.latency_ms}ms`)
      } else {
        message.error(result.message)
      }
    } catch (err: any) {
      message.error(err?.message || '测试失败')
    } finally {
      setTestingConn(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>
          <RobotOutlined /> 智能问答
        </Typography.Title>
        <Space>
          <Space size={4}>
            <ThunderboltOutlined style={{ color: useLlm ? '#1677ff' : '#bfbfbf' }} />
            <Switch
              checked={useLlm}
              onChange={(v) => setUseLlm(v)}
              disabled={!llmAvailable}
              size="small"
            />
            <Typography.Text
              type={useLlm ? 'success' : 'secondary'}
              style={{ fontSize: 12, whiteSpace: 'nowrap' }}
            >
              {useLlm ? 'AI 增强' : '模板回答'}
            </Typography.Text>
          </Space>
          <Button
            icon={<SettingOutlined />}
            onClick={openSettings}
            size="small"
            title="LLM 设置"
          />
          <Button icon={<ClearOutlined />} onClick={clearChat} disabled={!messages.length} size="small">
            清空
          </Button>
        </Space>
      </div>

      {messages.length === 0 ? (
        <Card style={{ marginBottom: 16, textAlign: 'center' }}>
          <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
            试试问我这些问题：
          </Typography.Text>
          <Space wrap>
            {suggestedQuestions.map((q) => (
              <Button key={q} size="small" onClick={() => handleSend(q)}>
                {q}
              </Button>
            ))}
          </Space>
        </Card>
      ) : (
        <div style={{ marginBottom: 16 }}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                marginBottom: 16,
                display: 'flex',
                gap: 12,
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              {msg.role === 'assistant' && (
                <RobotOutlined style={{ fontSize: 24, color: '#1677ff', marginTop: 8 }} />
              )}
              <div style={{ maxWidth: '85%' }}>
                <div
                  style={{
                    padding: '12px 16px',
                    borderRadius: 12,
                    background: msg.role === 'user' ? '#1677ff' : '#f5f5f5',
                    color: msg.role === 'user' ? '#fff' : '#000',
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.7,
                  }}
                  dangerouslySetInnerHTML={{
                    __html: msg.content
                      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                      .replace(/`(.*?)`/g, '<code>$1</code>')
                      .replace(/\n/g, '<br/>'),
                  }}
                />
                <div style={{ marginTop: 4 }}>
                  {msg.intent && (
                    <Tag color="blue">{intentLabels[msg.intent] || msg.intent}</Tag>
                  )}
                  {msg.entities?.table_name && (
                    <Tag color="green">{msg.entities.table_name}</Tag>
                  )}
                  {msg.entities?.database_name && (
                    <Tag color="orange">{msg.entities.database_name}</Tag>
                  )}
                  {msg.used_llm && (
                    <Tag color="purple"><ThunderboltOutlined /> AI 增强</Tag>
                  )}
                </div>
              </div>
              {msg.role === 'user' && (
                <UserOutlined style={{ fontSize: 24, color: '#1677ff', marginTop: 8 }} />
              )}
            </div>
          ))}
          {loading && (
            <div style={{ marginBottom: 16, display: 'flex', gap: 12 }}>
              <RobotOutlined style={{ fontSize: 24, color: '#1677ff' }} />
              <Spin size="small" />
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}

      <div style={{ display: 'flex', gap: 8 }}>
        <Input.TextArea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={(e) => {
            if (!e.shiftKey) {
              e.preventDefault()
              handleSend()
            }
          }}
          placeholder={
            useLlm
              ? '输入问题，AI 会根据元数据回答…'
              : '输入问题，例如：ods 库有哪些表？'
          }
          autoSize={{ minRows: 2, maxRows: 4 }}
          disabled={loading}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={() => handleSend()}
          loading={loading}
          style={{ height: 'auto' }}
        >
          发送
        </Button>
      </div>

      {/* LLM Settings Modal */}
      <Modal
        title="LLM 模型设置"
        open={settingsOpen}
        onOk={handleSaveConfig}
        onCancel={() => setSettingsOpen(false)}
        confirmLoading={savingConfig}
        destroyOnClose
        width={480}
      >
        <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          配置兼容 OpenAI API 的模型（OpenAI / DeepSeek / vLLM / Ollama 等）。修改后立即生效。
        </Typography.Text>
        <Form form={settingsForm} layout="vertical">
          <Form.Item name="model" label="模型名称">
            <Input placeholder="例: gpt-4o-mini / deepseek-chat / qwen2.5" />
          </Form.Item>
          <Form.Item name="base_url" label="API 地址 (Base URL)" extra="留空使用 OpenAI 官方地址">
            <Input placeholder="例: https://api.deepseek.com/v1 或 http://localhost:11434/v1" />
          </Form.Item>
          <Form.Item name="api_key" label="API Key" extra="留空则不修改已有的 Key">
            <Input.Password placeholder="sk-xxx" />
          </Form.Item>
        </Form>
        <Button
          onClick={handleTestConfig}
          loading={testingConn}
          size="small"
          style={{ marginBottom: 12 }}
        >
          测试连接
        </Button>
        {llmConfig && (
          <div style={{ fontSize: 12, color: '#888' }}>
            当前配置：{llmConfig.model}
            {llmConfig.base_url ? ` | ${llmConfig.base_url}` : ' | OpenAI 官方'}
            {' | '}Key: {llmConfig.api_key_configured ? '已配置' : '未配置'}
          </div>
        )}
        {!llmConfig?.api_key_configured && (
          <Typography.Text type="warning" style={{ fontSize: 12 }}>
            尚未配置 API Key，AI 增强模式不可用
          </Typography.Text>
        )}
      </Modal>
    </div>
  )
}
