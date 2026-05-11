"""Initial tables

Revision ID: 001
Revises:
Create Date: 2026-05-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension (for future use)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # --- databases ---
    op.create_table(
        "databases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("display_name", sa.String(500)),
        sa.Column("description", sa.Text),
        sa.Column("db_type", sa.String(50)),
        sa.Column("host", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- tables ---
    op.create_table(
        "tables",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("database_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("databases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("table_name", sa.String(500), nullable=False, index=True),
        sa.Column("display_name", sa.String(500)),
        sa.Column("description", sa.Text),
        sa.Column("table_type", sa.String(50)),
        sa.Column("partition_key", sa.String(200)),
        sa.Column("partition_freq", sa.String(50)),
        sa.Column("primary_keys", sa.Text),
        sa.Column("owner", sa.String(200)),
        sa.Column("tags", sa.Text),
        sa.Column("business_scenarios", sa.Text),
        sa.Column("usage_notes", sa.Text),
        sa.Column("row_count_estimate", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- columns ---
    op.create_table(
        "columns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("table_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tables.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("column_name", sa.String(500), nullable=False),
        sa.Column("display_name", sa.String(500)),
        sa.Column("data_type", sa.String(100)),
        sa.Column("description", sa.Text),
        sa.Column("is_primary_key", sa.Boolean, default=False),
        sa.Column("is_nullable", sa.Boolean, default=True),
        sa.Column("default_value", sa.String(500)),
        sa.Column("enum_values", sa.Text),
        sa.Column("calculation_rule", sa.Text),
        sa.Column("source_info", sa.Text),
        sa.Column("null_rate", sa.Float),
        sa.Column("distinct_count", sa.Integer),
        sa.Column("sort_order", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- schedules ---
    op.create_table(
        "schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_name", sa.String(500), unique=True, nullable=False, index=True),
        sa.Column("task_type", sa.String(50)),
        sa.Column("schedule_cron", sa.String(100)),
        sa.Column("schedule_desc", sa.String(500)),
        sa.Column("owner", sa.String(200)),
        sa.Column("last_success_time", sa.DateTime(timezone=True)),
        sa.Column("last_failure_time", sa.DateTime(timezone=True)),
        sa.Column("last_duration_sec", sa.Integer),
        sa.Column("status", sa.String(50)),
        sa.Column("task_config", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- table_schedules ---
    op.create_table(
        "table_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("table_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tables.id", ondelete="CASCADE"), nullable=False),
        sa.Column("schedule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation_type", sa.String(50), default="produces"),
    )

    # --- table_lineage ---
    op.create_table(
        "table_lineage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("upstream_table_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tables.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("downstream_table_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tables.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("relation_desc", sa.String(500)),
    )

    # --- column_lineage ---
    op.create_table(
        "column_lineage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("upstream_column_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("columns.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("downstream_column_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("columns.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("transform_rule", sa.Text),
        sa.Column("relation_desc", sa.String(500)),
    )

    # --- reports ---
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_name", sa.String(500), unique=True, nullable=False, index=True),
        sa.Column("report_url", sa.String(1000)),
        sa.Column("bi_tool", sa.String(50)),
        sa.Column("description", sa.Text),
        sa.Column("owner", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- report_tables ---
    op.create_table(
        "report_tables",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("table_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tables.id", ondelete="CASCADE"), nullable=False),
    )

    # --- documents ---
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text),
        sa.Column("doc_type", sa.String(50)),
        sa.Column("related_table_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tables.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- qa_logs ---
    op.create_table(
        "qa_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("intent", sa.String(100)),
        sa.Column("matched_tables", sa.Text),
        sa.Column("answer", sa.Text),
        sa.Column("sources", sa.Text),
        sa.Column("user_feedback", sa.SmallInteger, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("qa_logs")
    op.drop_table("documents")
    op.drop_table("report_tables")
    op.drop_table("reports")
    op.drop_table("column_lineage")
    op.drop_table("table_lineage")
    op.drop_table("table_schedules")
    op.drop_table("schedules")
    op.drop_table("columns")
    op.drop_table("tables")
    op.drop_table("databases")
