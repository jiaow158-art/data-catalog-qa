import { useState } from 'react'
import {
  Card,
  Radio,
  Upload,
  Button,
  Table,
  Tag,
  Alert,
  Space,
  Typography,
  Statistic,
  Row,
  Col,
  Spin,
  message,
} from 'antd'
import { InboxOutlined, CheckCircleOutlined } from '@ant-design/icons'
import type { UploadProps } from 'antd'
import { importApi, type ImportPreview, type ImportResult } from '../api/client'

const { Dragger } = Upload
const { Title } = Typography

const ENTITY_OPTIONS = [
  { label: '表元数据', value: 'tables' },
  { label: '字段元数据', value: 'columns' },
  { label: '调度任务', value: 'schedules' },
  { label: '表级血缘', value: 'table_lineage' },
]

const ENTITY_LABELS: Record<string, string> = {
  tables: '表元数据',
  columns: '字段元数据',
  schedules: '调度任务',
  table_lineage: '表级血缘',
}

// CSV template download links
const TEMPLATE_LINKS: Record<string, { url: string; name: string }> = {
  tables: { url: '/import-templates/tables.csv', name: 'tables.csv' },
  columns: { url: '/import-templates/columns.csv', name: 'columns.csv' },
  schedules: { url: '/import-templates/schedules.csv', name: 'schedules.csv' },
  table_lineage: { url: '/import-templates/table_lineage.csv', name: 'table_lineage.csv' },
}

export default function ImportPage() {
  const [entityType, setEntityType] = useState('tables')
  const [uploading, setUploading] = useState(false)
  const [preview, setPreview] = useState<ImportPreview | null>(null)
  const [confirming, setConfirming] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)

  const handleUpload: UploadProps['customRequest'] = async (options) => {
    const file = options.file as File
    setUploading(true)
    setResult(null)
    setPreview(null)
    try {
      const p = await importApi.upload(file, entityType)
      setPreview(p)
      if (p.valid_rows === 0) {
        message.warning('没有有效数据行，请检查文件内容')
      } else {
        message.success(`解析完成：${p.total_rows} 行，${p.valid_rows} 行有效`)
      }
    } catch (err: any) {
      message.error(err?.message || '解析失败')
    } finally {
      setUploading(false)
    }
  }

  const handleConfirm = async () => {
    if (!preview) return
    setConfirming(true)
    try {
      const r = await importApi.confirm(preview.preview_id)
      setResult(r)
      if (r.created > 0 || r.updated > 0) {
        message.success(`导入完成：新增 ${r.created}，更新 ${r.updated}，跳过 ${r.skipped}`)
      } else {
        message.warning(`导入完成但无数据变更：跳过 ${r.skipped} 条`)
      }
      setPreview(null)
    } catch (err: any) {
      message.error(err?.message || '导入失败')
    } finally {
      setConfirming(false)
    }
  }

  const previewColumns = preview
    ? preview.columns.map((col) => ({
        title: col,
        dataIndex: col,
        key: col,
        ellipsis: true,
        width: 150,
        render: (v: string | null) => (v !== null && v !== undefined ? String(v) : '-'),
      }))
    : []

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>数据导入</Title>

      {/* Entity type selector */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <span style={{ marginRight: 12, fontWeight: 500 }}>导入实体类型：</span>
            <Radio.Group
              options={ENTITY_OPTIONS}
              value={entityType}
              onChange={(e) => {
                setEntityType(e.target.value)
                setPreview(null)
                setResult(null)
              }}
              optionType="button"
              buttonStyle="solid"
            />
          </div>
          <div style={{ color: '#888', fontSize: 12 }}>
            下载 CSV 模板：
            {ENTITY_OPTIONS.map((opt) => {
              const tpl = TEMPLATE_LINKS[opt.value]
              return tpl ? (
                <a
                  key={opt.value}
                  href={tpl.url}
                  download={tpl.name}
                  style={{ marginLeft: 12 }}
                >
                  {tpl.name}
                </a>
              ) : null
            })}
          </div>
        </Space>
      </Card>

      {/* Upload area */}
      {!preview && (
        <Card style={{ marginBottom: 16 }}>
          <Dragger
            customRequest={handleUpload}
            showUploadList={false}
            accept=".csv,.xlsx,.xls"
            disabled={uploading}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽 CSV/Excel 文件到此区域</p>
            <p className="ant-upload-hint">
              当前选择的是 <Tag>{ENTITY_LABELS[entityType]}</Tag>，请确认实体类型与文件内容匹配
            </p>
          </Dragger>
          {uploading && <Spin style={{ display: 'block', marginTop: 16 }} />}
        </Card>
      )}

      {/* Preview */}
      {preview && (
        <Card
          title={`预览：${preview.filename}`}
          style={{ marginBottom: 16 }}
          extra={
            <Space>
              <Button onClick={() => { setPreview(null); setResult(null) }}>
                重新上传
              </Button>
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={handleConfirm}
                loading={confirming}
                disabled={preview.valid_rows === 0}
              >
                确认导入 ({preview.valid_rows} 行)
              </Button>
            </Space>
          }
        >
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Statistic title="总行数" value={preview.total_rows} />
            </Col>
            <Col span={6}>
              <Statistic title="有效行" value={preview.valid_rows} valueStyle={{ color: '#3f8600' }} />
            </Col>
            <Col span={6}>
              <Statistic title="错误行" value={preview.error_rows} valueStyle={{ color: preview.error_rows > 0 ? '#cf1322' : undefined }} />
            </Col>
            <Col span={6}>
              <Tag color="blue">{ENTITY_LABELS[preview.entity_type]}</Tag>
            </Col>
          </Row>

          {preview.errors.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              {preview.errors.map((err, i) => (
                <Alert
                  key={i}
                  type="error"
                  message={`第 ${err.row} 行`}
                  description={err.messages.join('；')}
                  style={{ marginBottom: 4 }}
                  showIcon
                />
              ))}
            </div>
          )}

          <Table
            columns={previewColumns}
            dataSource={preview.preview_data.map((row, i) => ({ ...row, _key: i }))}
            rowKey="_key"
            scroll={{ x: 'max-content' }}
            size="small"
            pagination={false}
          />
        </Card>
      )}

      {/* Result */}
      {result && (
        <Card title="导入结果">
          <Row gutter={16}>
            <Col span={6}>
              <Statistic title="新增" value={result.created} valueStyle={{ color: '#3f8600' }} />
            </Col>
            <Col span={6}>
              <Statistic title="更新" value={result.updated} valueStyle={{ color: '#1677ff' }} />
            </Col>
            <Col span={6}>
              <Statistic title="跳过" value={result.skipped} />
            </Col>
            <Col span={6}>
              <Statistic title="错误" value={result.errors.length} valueStyle={{ color: result.errors.length > 0 ? '#cf1322' : undefined }} />
            </Col>
          </Row>
          {result.errors.length > 0 && (
            <div style={{ marginTop: 16 }}>
              {result.errors.map((err, i) => (
                <Alert
                  key={i}
                  type="error"
                  message={`${JSON.stringify(err.row)}`}
                  description={err.error}
                  style={{ marginBottom: 4 }}
                  showIcon
                />
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
