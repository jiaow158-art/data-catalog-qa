const BASE = '/api/v1'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

import type {
  Database,
  DatabaseCreate,
  TableItem,
  TableCreate,
  TableDetail,
  ColumnItem,
  ColumnCreate,
  Schedule,
  ScheduleCreate,
  Report,
  ReportCreate,
  SearchResult,
  PaginatedResponse,
  DirectLineage,
  ColumnLineage,
  LLMConfig,
} from '../types'

// Databases
export const databasesApi = {
  list: (params?: { search?: string; db_type?: string; page?: number; size?: number }) => {
    const sp = new URLSearchParams()
    if (params?.search) sp.set('search', params.search)
    if (params?.db_type) sp.set('db_type', params.db_type)
    if (params?.page) sp.set('page', String(params.page))
    if (params?.size) sp.set('size', String(params.size))
    const qs = sp.toString()
    return request<PaginatedResponse<Database>>(`/databases${qs ? `?${qs}` : ''}`)
  },
  get: (id: string) => request<Database>(`/databases/${id}`),
  create: (data: DatabaseCreate) =>
    request<Database>('/databases', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<DatabaseCreate>) =>
    request<Database>(`/databases/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/databases/${id}`, { method: 'DELETE' }),
}

// Tables
export const tablesApi = {
  list: (params?: {
    database_id?: string
    search?: string
    table_type?: string
    page?: number
    size?: number
  }) => {
    const sp = new URLSearchParams()
    if (params?.database_id) sp.set('database_id', params.database_id)
    if (params?.search) sp.set('search', params.search)
    if (params?.table_type) sp.set('table_type', params.table_type)
    if (params?.page) sp.set('page', String(params.page))
    if (params?.size) sp.set('size', String(params.size))
    const qs = sp.toString()
    return request<PaginatedResponse<TableItem>>(`/tables${qs ? `?${qs}` : ''}`)
  },
  getDetail: (id: string) => request<TableDetail>(`/tables/${id}`),
  create: (data: TableCreate) =>
    request<TableItem>('/tables', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<TableCreate>) =>
    request<TableItem>(`/tables/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/tables/${id}`, { method: 'DELETE' }),
}

// Columns
export const columnsApi = {
  list: (tableId: string) =>
    request<PaginatedResponse<ColumnItem>>(`/columns?table_id=${tableId}&size=100`),
  get: (id: string) => request<ColumnItem>(`/columns/${id}`),
  create: (data: ColumnCreate) =>
    request<ColumnItem>('/columns', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<ColumnCreate>) =>
    request<ColumnItem>(`/columns/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/columns/${id}`, { method: 'DELETE' }),
}

// Lineage
export interface LineageGraphData {
  nodes: { id: string; table_name: string; display_name: string; table_type: string; owner: string; is_focus: boolean; depth: number }[]
  edges: { id: string; source: string; target: string; label: string }[]
}

export const lineageApi = {
  getGraph: (tableId: string, depth = 3, direction = 'both') =>
    request<LineageGraphData>(`/lineage/tables/${tableId}/graph?depth=${depth}&direction=${direction}`),
  getDirect: (tableId: string) =>
    request<DirectLineage>(`/lineage/tables/${tableId}`),
  createTableEdge: (data: { upstream_table_id: string; downstream_table_id: string; relation_desc?: string }) =>
    request<{ id: string; upstream_table_id: string; downstream_table_id: string; relation_desc: string | null }>(
      '/lineage/tables', { method: 'POST', body: JSON.stringify(data) }
    ),
  deleteTableEdge: (id: string) => request<void>(`/lineage/tables/${id}`, { method: 'DELETE' }),
  getColumnLineage: (columnId: string) =>
    request<ColumnLineage>(`/lineage/columns/${columnId}`),
}

// Import
export interface ImportPreview {
  preview_id: string
  entity_type: string
  filename: string
  total_rows: number
  valid_rows: number
  error_rows: number
  columns: string[]
  preview_data: Record<string, string | null>[]
  errors: { row: number; messages: string[] }[]
}

export interface ImportResult {
  entity_type: string
  created: number
  updated: number
  skipped: number
  errors: { row: Record<string, string>; error: string }[]
}

export const importApi = {
  upload: async (file: File, entity_type: string): Promise<ImportPreview> => {
    const form = new FormData()
    form.append('file', file)
    form.append('entity_type', entity_type)
    const res = await fetch(`${BASE}/import/upload`, { method: 'POST', body: form })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    return res.json()
  },
  confirm: async (preview_id: string): Promise<ImportResult> => {
    const form = new FormData()
    form.append('preview_id', preview_id)
    const res = await fetch(`${BASE}/import/confirm`, { method: 'POST', body: form })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    return res.json()
  },
}

// Schedules
export const schedulesApi = {
  list: (params?: { search?: string; page?: number; size?: number }) => {
    const sp = new URLSearchParams()
    if (params?.search) sp.set('search', params.search)
    if (params?.page) sp.set('page', String(params.page))
    if (params?.size) sp.set('size', String(params.size))
    const qs = sp.toString()
    return request<PaginatedResponse<Schedule>>(`/schedules${qs ? `?${qs}` : ''}`)
  },
  get: (id: string) => request<Schedule>(`/schedules/${id}`),
  create: (data: ScheduleCreate) =>
    request<Schedule>('/schedules', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<ScheduleCreate>) =>
    request<Schedule>(`/schedules/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/schedules/${id}`, { method: 'DELETE' }),
}

// Reports
export const reportsApi = {
  list: (params?: { search?: string; page?: number; size?: number }) => {
    const sp = new URLSearchParams()
    if (params?.search) sp.set('search', params.search)
    if (params?.page) sp.set('page', String(params.page))
    if (params?.size) sp.set('size', String(params.size))
    const qs = sp.toString()
    return request<PaginatedResponse<Report>>(`/reports${qs ? `?${qs}` : ''}`)
  },
  get: (id: string) => request<Report>(`/reports/${id}`),
  create: (data: ReportCreate) =>
    request<Report>('/reports', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<ReportCreate>) =>
    request<Report>(`/reports/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/reports/${id}`, { method: 'DELETE' }),
}

// QA
export interface QaResponse {
  question: string
  answer: string
  intent: string
  confidence: number
  entities: Record<string, string | null>
  used_llm: boolean
}

export interface LLMTestResult {
  ok: boolean
  message: string
  model: string
  latency_ms: number
}

export const qaApi = {
  ask: (question: string, use_llm: boolean) =>
    request<QaResponse>('/qa/ask', {
      method: 'POST',
      body: JSON.stringify({ question, use_llm }),
    }),
  getConfig: () => request<LLMConfig>('/qa/config'),
  updateConfig: (data: { api_key?: string; base_url?: string; model?: string }) =>
    request<{ ok: boolean }>('/qa/config', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  testConfig: (data?: { api_key?: string; base_url?: string; model?: string }) =>
    request<LLMTestResult>('/qa/config/test', {
      method: 'POST',
      body: JSON.stringify(data || {}),
    }),
}

// Search
export const searchApi = {
  search: (q: string, entity_type?: string, size?: number) => {
    const sp = new URLSearchParams()
    sp.set('q', q)
    if (entity_type) sp.set('entity_type', entity_type)
    if (size) sp.set('size', String(size))
    return request<SearchResult>(`/search?${sp.toString()}`)
  },
}
