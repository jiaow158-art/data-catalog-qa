from __future__ import annotations
import io
import json
import uuid as uuid_lib
from datetime import datetime
from typing import Optional
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from app.models import (
    DatabaseModel,
    Table,
    Column,
    Schedule,
    TableSchedule,
    TableLineage,
)

# In-memory preview store (MVP — survives until confirm or restart)
_previews: dict[str, dict] = {}

ENTITY_CONFIG = {
    "tables": {
        "required": ["database_name", "table_name"],
        "optional": [
            "display_name", "description", "table_type", "partition_key",
            "partition_freq", "primary_keys", "owner", "tags", "business_scenarios",
        ],
    },
    "columns": {
        "required": ["table_name", "column_name"],
        "optional": [
            "display_name", "data_type", "description", "is_primary_key",
            "is_nullable", "enum_values", "calculation_rule", "source_info",
            "sort_order",
        ],
    },
    "schedules": {
        "required": ["task_name"],
        "optional": [
            "task_type", "schedule_cron", "schedule_desc", "owner",
            "last_success_time", "status", "target_tables",
        ],
    },
    "table_lineage": {
        "required": ["upstream_table", "downstream_table"],
        "optional": ["relation_desc"],
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_dataframe(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse CSV or Excel bytes into a DataFrame."""
    if filename.lower().endswith(".csv"):
        return pd.read_csv(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
    elif filename.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(file_bytes), dtype=str)
    else:
        raise ValueError(f"不支持的文件类型: {filename}")


def _truthy(val) -> bool:
    """Normalise boolean-ish values from CSV strings."""
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return str(val).strip().upper() in ("TRUE", "YES", "1", "Y", "是")


def _strip(val) -> Optional[str]:
    """Strip a value; return None for empty strings."""
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _parse_datetime(val) -> Optional[datetime]:
    """Parse ISO-ish datetime strings into Python datetime objects."""
    s = _strip(val)
    if not s:
        return None
    # Try common ISO formats
    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # Last resort: try pandas
    try:
        return pd.to_datetime(s).to_pydatetime()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Validation per entity type
# ---------------------------------------------------------------------------

def _validate_table_row(row: dict, db: Session, errors: list[str]):
    table_name = row.get("table_name", "")
    if not table_name or len(table_name) > 500:
        errors.append(f"表名无效或过长")

    # JSON fields
    for field in ["primary_keys", "tags"]:
        v = row.get(field)
        if v:
            try:
                json.loads(v)
            except (json.JSONDecodeError, TypeError):
                errors.append(f"{field} 不是有效 JSON")


def _validate_column_row(row: dict, db: Session, errors: list[str]):
    table_name = row.get("table_name", "")
    table = db.query(Table).filter(Table.table_name == table_name).first()
    if not table:
        errors.append(f"目标表不存在: {table_name}")

    ev = row.get("enum_values")
    if ev:
        try:
            json.loads(ev)
        except (json.JSONDecodeError, TypeError):
            errors.append("enum_values 不是有效 JSON")


def _validate_schedule_row(row: dict, db: Session, errors: list[str]):
    task_name = row.get("task_name", "")
    if not task_name or len(task_name) > 500:
        errors.append("任务名无效或过长")

    target_tables = row.get("target_tables", "")
    if target_tables:
        for t_name in target_tables.split(";"):
            t_name = t_name.strip()
            if t_name:
                tbl = db.query(Table).filter(Table.table_name == t_name).first()
                if not tbl:
                    errors.append(f"目标表不存在: {t_name}")


def _validate_lineage_row(row: dict, db: Session, errors: list[str]):
    upstream = row.get("upstream_table", "")
    downstream = row.get("downstream_table", "")

    if upstream == downstream:
        errors.append("上下游表不能相同")

    if not db.query(Table).filter(Table.table_name == upstream).first():
        errors.append(f"上游表不存在: {upstream}")
    if not db.query(Table).filter(Table.table_name == downstream).first():
        errors.append(f"下游表不存在: {downstream}")


def validate_and_prepare(
    df: pd.DataFrame, entity_type: str, db: Session
) -> tuple[list[dict], list[dict]]:
    """Validate every row. Returns (valid_rows, errors)."""
    config = ENTITY_CONFIG[entity_type]
    errors: list[dict] = []
    valid_rows: list[dict] = []

    for idx in range(len(df)):
        row_num = idx + 2  # 1-indexed + header
        row_errors: list[str] = []

        raw = {col: _strip(df.iloc[idx].get(col)) for col in df.columns}

        # Required fields
        for col in config["required"]:
            if not raw.get(col):
                row_errors.append(f"缺少必填字段: {col}")

        if row_errors:
            errors.append({"row": row_num, "messages": row_errors})
            continue

        # Entity-specific checks
        if entity_type == "tables":
            _validate_table_row(raw, db, row_errors)
        elif entity_type == "columns":
            _validate_column_row(raw, db, row_errors)
        elif entity_type == "schedules":
            _validate_schedule_row(raw, db, row_errors)
        elif entity_type == "table_lineage":
            _validate_lineage_row(raw, db, row_errors)

        if row_errors:
            errors.append({"row": row_num, "messages": row_errors})
        else:
            valid_rows.append(raw)

    return valid_rows, errors


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------

def create_preview(
    db: Session, file_bytes: bytes, filename: str, entity_type: str
) -> dict:
    """Parse uploaded file and return a preview with a preview_id."""
    if entity_type not in ENTITY_CONFIG:
        raise ValueError(f"不支持的实体类型: {entity_type}")

    df = parse_dataframe(file_bytes, filename)
    valid_rows, errors = validate_and_prepare(df, entity_type, db)

    preview_id = uuid_lib.uuid4().hex

    # Build safe preview rows (first 20)
    preview_data = []
    for idx in range(min(len(df), 20)):
        row = {}
        for col in df.columns:
            v = df.iloc[idx].get(col)
            if pd.isna(v) or v is None or str(v).strip() == "":
                row[col] = None
            else:
                row[col] = str(v).strip()
        preview_data.append(row)

    entry = {
        "preview_id": preview_id,
        "entity_type": entity_type,
        "filename": filename,
        "total_rows": len(df),
        "valid_rows": len(valid_rows),
        "error_rows": len(errors),
        "columns": df.columns.tolist(),
        "preview_data": preview_data,
        "errors": errors[:50],
    }

    _previews[preview_id] = {
        **entry,
        "_valid_rows": valid_rows,
    }

    return entry


# ---------------------------------------------------------------------------
# Confirm & execute import
# ---------------------------------------------------------------------------

def confirm_import(db: Session, preview_id: str) -> dict:
    """Execute the import from a previously-created preview."""
    entry = _previews.pop(preview_id, None)
    if not entry:
        raise ValueError(f"预览不存在或已过期: {preview_id}")

    entity_type = entry["entity_type"]
    valid_rows = entry["_valid_rows"]

    created = 0
    updated = 0
    skipped = 0
    detail_errors: list[dict] = []

    for row in valid_rows:
        try:
            if entity_type == "tables":
                result = _import_table(db, row)
            elif entity_type == "columns":
                result = _import_column(db, row)
            elif entity_type == "schedules":
                result = _import_schedule(db, row)
            elif entity_type == "table_lineage":
                result = _import_lineage(db, row)
            else:
                raise ValueError(f"Unknown entity_type: {entity_type}")

            if result == "created":
                created += 1
            elif result == "updated":
                updated += 1
            elif result == "skipped":
                skipped += 1
        except Exception as exc:
            detail_errors.append({"row": row, "error": str(exc)})
            skipped += 1

    db.commit()

    return {
        "entity_type": entity_type,
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": detail_errors[:20],
    }


# ---------------------------------------------------------------------------
# Per-entity import helpers
# ---------------------------------------------------------------------------

def _import_table(db: Session, row: dict) -> str:
    db_name = row["database_name"]

    db_obj = db.query(DatabaseModel).filter(DatabaseModel.name == db_name).first()
    if not db_obj:
        db_obj = DatabaseModel(name=db_name, display_name=db_name)
        db.add(db_obj)
        db.flush()

    table_name = row["table_name"]
    existing = db.query(Table).filter(Table.table_name == table_name).first()

    payload = {
        "database_id": db_obj.id,
        "table_name": table_name,
        "display_name": row.get("display_name"),
        "description": row.get("description"),
        "table_type": row.get("table_type"),
        "partition_key": row.get("partition_key"),
        "partition_freq": row.get("partition_freq"),
        "primary_keys": row.get("primary_keys"),
        "owner": row.get("owner"),
        "tags": row.get("tags"),
        "business_scenarios": row.get("business_scenarios"),
    }

    if existing:
        for k, v in payload.items():
            if v is not None:
                setattr(existing, k, v)
        return "updated"

    obj = Table(**payload)
    db.add(obj)
    return "created"


def _import_column(db: Session, row: dict) -> str:
    table_name = row["table_name"]
    table = db.query(Table).filter(Table.table_name == table_name).first()
    if not table:
        return "skipped"

    col_name = row["column_name"]
    existing = (
        db.query(Column)
        .filter(Column.table_id == table.id, Column.column_name == col_name)
        .first()
    )

    sort_order = row.get("sort_order")
    try:
        sort_order = int(sort_order) if sort_order else 0
    except (ValueError, TypeError):
        sort_order = 0

    payload = {
        "table_id": table.id,
        "column_name": col_name,
        "display_name": row.get("display_name"),
        "data_type": row.get("data_type"),
        "description": row.get("description"),
        "is_primary_key": _truthy(row.get("is_primary_key")),
        "is_nullable": _truthy(row.get("is_nullable", True)),
        "enum_values": row.get("enum_values"),
        "calculation_rule": row.get("calculation_rule"),
        "source_info": row.get("source_info"),
        "sort_order": sort_order,
    }

    if existing:
        for k, v in payload.items():
            if v is not None:
                setattr(existing, k, v)
        return "updated"

    obj = Column(**payload)
    db.add(obj)
    return "created"


def _import_schedule(db: Session, row: dict) -> str:
    task_name = row["task_name"]
    existing = db.query(Schedule).filter(Schedule.task_name == task_name).first()

    last_success = row.get("last_success_time")
    if last_success:
        try:
            last_success = datetime.strptime(last_success, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            try:
                last_success = datetime.strptime(last_success, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                last_success = None

    payload = {
        "task_name": task_name,
        "task_type": row.get("task_type"),
        "schedule_cron": row.get("schedule_cron"),
        "schedule_desc": row.get("schedule_desc"),
        "owner": row.get("owner"),
        "last_success_time": last_success,
        "status": row.get("status"),
    }

    if existing:
        for k, v in payload.items():
            if v is not None:
                setattr(existing, k, v)
        sched = existing
        result = "updated"
    else:
        sched = Schedule(**payload)
        db.add(sched)
        db.flush()
        result = "created"

    # Link target tables
    target_tables = row.get("target_tables", "")
    if target_tables:
        for t_name in target_tables.split(";"):
            t_name = t_name.strip()
            if t_name:
                tbl = db.query(Table).filter(Table.table_name == t_name).first()
                if tbl:
                    link_exists = (
                        db.query(TableSchedule)
                        .filter(
                            TableSchedule.table_id == tbl.id,
                            TableSchedule.schedule_id == sched.id,
                        )
                        .first()
                    )
                    if not link_exists:
                        db.add(TableSchedule(
                            table_id=tbl.id,
                            schedule_id=sched.id,
                            relation_type="produces",
                        ))

    return result


def _import_lineage(db: Session, row: dict) -> str:
    up = db.query(Table).filter(Table.table_name == row["upstream_table"]).first()
    down = db.query(Table).filter(Table.table_name == row["downstream_table"]).first()

    if not up or not down:
        return "skipped"

    existing = (
        db.query(TableLineage)
        .filter(
            TableLineage.upstream_table_id == up.id,
            TableLineage.downstream_table_id == down.id,
        )
        .first()
    )

    rd = row.get("relation_desc")
    if existing:
        if rd:
            existing.relation_desc = rd
        return "updated"

    obj = TableLineage(
        upstream_table_id=up.id,
        downstream_table_id=down.id,
        relation_desc=rd,
    )
    db.add(obj)
    return "created"
