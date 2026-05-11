# 数仓元数据智能问答平台

数据仓库元数据管理与智能问答平台，支持元数据 CRUD、血缘图谱、调度管理、报表管理，以及基于 LLM 的自然语言查询。

## 技术栈

| 层 | 技术 |
|---|------|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 16 + pgvector |
| 前端 | React 18 / TypeScript / Vite / Ant Design 5 |
| LLM | OpenAI 兼容接口 (GPT-4o-mini / DeepSeek / Ollama 等) |
| 迁移 | Alembic |

## 快速启动

### 1. 启动数据库

```bash
docker compose up -d
```

### 2. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写 LLM_API_KEY 等信息

# 执行数据库迁移
alembic upgrade head

# 导入种子数据（可选）
python seed_data.py

# 启动
uvicorn app.main:app --reload
```

后端运行在 http://localhost:8000，Swagger 文档在 http://localhost:8000/docs

### 3. 前端

```bash
cd frontend

npm install
npm run dev
```

前端运行在 http://localhost:5173

## 功能模块

| 模块 | 说明 |
|------|------|
| 数据库管理 | 数据源实例的增删改查 |
| 表元数据 | 表信息管理，含分区、主键、标签、业务场景等 |
| 字段元数据 | 字段详情，含数据类型、计算规则、枚举值等 |
| 调度任务 | ETL 任务管理，支持关联到表 |
| 血缘图谱 | 表级血缘可视化，支持上下游追溯 |
| 报表管理 | BI 报表信息管理 |
| 数据导入 | CSV 批量导入元数据 |
| 智能问答 | 自然语言查询元数据，LLM 理解意图并生成回答 |

## API 概览

```
POST   /api/v1/qa/ask          # 智能问答
GET    /api/v1/databases       # 数据库列表
POST   /api/v1/databases       # 创建数据库
GET    /api/v1/tables          # 表列表
GET    /api/v1/tables/:id      # 表详情（含字段/调度/血缘）
GET    /api/v1/columns         # 字段列表
GET    /api/v1/schedules       # 调度列表
GET    /api/v1/reports         # 报表列表
GET    /api/v1/search?q=       # 全局搜索
GET    /api/v1/lineage/tables/:id/graph  # 血缘图谱数据
POST   /api/v1/import/upload   # CSV 导入
```

## 数据模型

```
databases ──< tables ──< columns
                ││
                │└── table_schedules ──> schedules
                │
                └─── table_lineage (上游/下游)
                         │
                         └── column_lineage (字段级)
reports ──< report_tables
documents
qa_logs
```
