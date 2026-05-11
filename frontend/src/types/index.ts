export interface Database {
  id: string
  name: string
  display_name: string | null
  description: string | null
  db_type: string | null
  host: string | null
  created_at: string
  updated_at: string | null
}

export interface DatabaseCreate {
  name: string
  display_name?: string
  description?: string
  db_type?: string
  host?: string
}

export interface TableItem {
  id: string
  database_id: string
  table_name: string
  display_name: string | null
  description: string | null
  table_type: string | null
  partition_key: string | null
  partition_freq: string | null
  primary_keys: string | null
  owner: string | null
  tags: string | null
  business_scenarios: string | null
  usage_notes: string | null
  row_count_estimate: number | null
  created_at: string
  updated_at: string | null
}

export interface ColumnBrief {
  id: string
  column_name: string
  display_name: string | null
  data_type: string | null
  description: string | null
  is_primary_key: boolean
  calculation_rule: string | null
  enum_values: string | null
  sort_order: number
}

export interface ScheduleBrief {
  id: string
  task_name: string
  schedule_desc: string | null
  last_success_time: string | null
  status: string | null
}

export interface LineageBrief {
  id: string
  table_name: string
  display_name: string | null
}

export interface TableDetail extends TableItem {
  columns: ColumnBrief[]
  schedules: ScheduleBrief[]
  upstream_tables: LineageBrief[]
  downstream_tables: LineageBrief[]
}

export interface TableCreate {
  database_id: string
  table_name: string
  display_name?: string
  description?: string
  table_type?: string
  partition_key?: string
  partition_freq?: string
  primary_keys?: string
  owner?: string
  tags?: string
  business_scenarios?: string
  usage_notes?: string
  row_count_estimate?: number
}

export interface ColumnItem {
  id: string
  table_id: string
  column_name: string
  display_name: string | null
  data_type: string | null
  description: string | null
  is_primary_key: boolean
  is_nullable: boolean
  default_value: string | null
  enum_values: string | null
  calculation_rule: string | null
  source_info: string | null
  null_rate: number | null
  distinct_count: number | null
  sort_order: number
}

export interface ColumnCreate {
  table_id: string
  column_name: string
  display_name?: string
  data_type?: string
  description?: string
  is_primary_key?: boolean
  is_nullable?: boolean
  default_value?: string
  enum_values?: string
  calculation_rule?: string
  source_info?: string
  null_rate?: number
  distinct_count?: number
  sort_order?: number
}

export interface Schedule {
  id: string
  task_name: string
  task_type: string | null
  schedule_cron: string | null
  schedule_desc: string | null
  owner: string | null
  last_success_time: string | null
  last_failure_time: string | null
  last_duration_sec: number | null
  status: string | null
  task_config: string | null
  created_at: string
  updated_at: string | null
}

export interface ScheduleCreate {
  task_name: string
  task_type?: string
  schedule_cron?: string
  schedule_desc?: string
  owner?: string
  status?: string
  task_config?: string
}

export interface Report {
  id: string
  report_name: string
  report_url: string | null
  bi_tool: string | null
  description: string | null
  owner: string | null
  created_at: string
  updated_at: string | null
}

export interface ReportCreate {
  report_name: string
  report_url?: string
  bi_tool?: string
  description?: string
  owner?: string
}

export interface DirectLineage {
  upstream: { id: string; table_name: string; display_name: string | null; table_type: string | null; owner: string | null }[]
  downstream: { id: string; table_name: string; display_name: string | null; table_type: string | null; owner: string | null }[]
  edges: { id: string; upstream_table_id: string; downstream_table_id: string; relation_desc: string | null }[]
}

export interface ColumnLineage {
  upstream: { id: string; column_name: string; display_name: string | null; table_name: string }[]
  downstream: { id: string; column_name: string; display_name: string | null; table_name: string }[]
  edges: { id: string; upstream_column_id: string; downstream_column_id: string; transform_rule: string | null; relation_desc: string | null }[]
}

export interface LLMConfig {
  provider: string
  model: string
  base_url: string
  api_key_configured: boolean
  max_tokens: number
  temperature: number
}

export interface SearchResult {
  tables?: TableItem[]
  columns?: ColumnBrief[]
  tasks?: { id: string; task_name: string; schedule_desc: string | null; status: string | null }[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
