from __future__ import annotations
import math
from typing import Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models import (
    DatabaseModel,
    Table,
    Column,
    Schedule,
    TableSchedule,
    TableLineage,
    ColumnLineage,
    Report,
    ReportTable,
)
from app.schemas.database import DatabaseCreate, DatabaseUpdate
from app.schemas.table import TableCreate, TableUpdate, TableDetail
from app.schemas.column import ColumnCreate, ColumnUpdate
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.schemas.report import ReportCreate, ReportUpdate


# ---------------------------------------------------------------------------
# Database CRUD
# ---------------------------------------------------------------------------

def create_database(db: Session, data: DatabaseCreate) -> DatabaseModel:
    obj = DatabaseModel(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_database(db: Session, db_id: UUID) -> Optional[DatabaseModel]:
    return db.get(DatabaseModel, db_id)


def list_databases(
    db: Session, search: Optional[str] = None, db_type: Optional[str] = None, page: int = 1, size: int = 20
) -> tuple[list[DatabaseModel], int]:
    q = db.query(DatabaseModel)
    if search:
        q = q.filter(
            or_(
                DatabaseModel.name.ilike(f"%{search}%"),
                DatabaseModel.display_name.ilike(f"%{search}%"),
            )
        )
    if db_type:
        q = q.filter(DatabaseModel.db_type == db_type)
    total = q.count()
    items = q.order_by(DatabaseModel.name).offset((page - 1) * size).limit(size).all()
    return items, total


def update_database(db: Session, db_id: UUID, data: DatabaseUpdate) -> Optional[DatabaseModel]:
    obj = db.get(DatabaseModel, db_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_database(db: Session, db_id: UUID) -> bool:
    obj = db.get(DatabaseModel, db_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Table CRUD
# ---------------------------------------------------------------------------

def create_table(db: Session, data: TableCreate) -> Table:
    obj = Table(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_table(db: Session, table_id: UUID) -> Optional[Table]:
    return db.get(Table, table_id)


def get_table_detail(db: Session, table_id: UUID) -> Optional[TableDetail]:
    table = (
        db.query(Table)
        .options(
            joinedload(Table.columns),
            joinedload(Table.table_schedules).joinedload(TableSchedule.schedule),
        )
        .filter(Table.id == table_id)
        .first()
    )
    if not table:
        return None

    # upstream tables
    up_stmt = (
        db.query(TableLineage.upstream_table_id)
        .filter(TableLineage.downstream_table_id == table_id)
    )
    upstream = db.query(Table).filter(Table.id.in_(up_stmt.scalar_subquery())).all()

    # downstream tables
    down_stmt = (
        db.query(TableLineage.downstream_table_id)
        .filter(TableLineage.upstream_table_id == table_id)
    )
    downstream = db.query(Table).filter(Table.id.in_(down_stmt.scalar_subquery())).all()

    return TableDetail(
        id=table.id,
        database_id=table.database_id,
        table_name=table.table_name,
        display_name=table.display_name,
        description=table.description,
        table_type=table.table_type,
        partition_key=table.partition_key,
        partition_freq=table.partition_freq,
        primary_keys=table.primary_keys,
        owner=table.owner,
        tags=table.tags,
        business_scenarios=table.business_scenarios,
        usage_notes=table.usage_notes,
        row_count_estimate=table.row_count_estimate,
        created_at=table.created_at,
        updated_at=table.updated_at,
        columns=[c for c in table.columns],
        schedules=[ts.schedule for ts in table.table_schedules],
        upstream_tables=upstream,
        downstream_tables=downstream,
    )


def list_tables(
    db: Session,
    database_id: Optional[UUID] = None,
    search: Optional[str] = None,
    table_type: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Table], int]:
    q = db.query(Table)
    if database_id:
        q = q.filter(Table.database_id == database_id)
    if search:
        q = q.filter(
            or_(
                Table.table_name.ilike(f"%{search}%"),
                Table.display_name.ilike(f"%{search}%"),
                Table.description.ilike(f"%{search}%"),
            )
        )
    if table_type:
        q = q.filter(Table.table_type == table_type)
    total = q.count()
    items = q.order_by(Table.table_name).offset((page - 1) * size).limit(size).all()
    return items, total


def update_table(db: Session, table_id: UUID, data: TableUpdate) -> Optional[Table]:
    obj = db.get(Table, table_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_table(db: Session, table_id: UUID) -> bool:
    obj = db.get(Table, table_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Column CRUD
# ---------------------------------------------------------------------------

def create_column(db: Session, data: ColumnCreate) -> Column:
    obj = Column(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_column(db: Session, column_id: UUID) -> Optional[Column]:
    return db.get(Column, column_id)


def list_columns(
    db: Session,
    table_id: Optional[UUID] = None,
    search: Optional[str] = None,
    page: int = 1,
    size: int = 50,
) -> tuple[list[Column], int]:
    q = db.query(Column)
    if table_id:
        q = q.filter(Column.table_id == table_id)
    if search:
        q = q.filter(
            or_(
                Column.column_name.ilike(f"%{search}%"),
                Column.display_name.ilike(f"%{search}%"),
                Column.description.ilike(f"%{search}%"),
            )
        )
    total = q.count()
    items = q.order_by(Column.sort_order, Column.column_name).offset((page - 1) * size).limit(size).all()
    return items, total


def update_column(db: Session, column_id: UUID, data: ColumnUpdate) -> Optional[Column]:
    obj = db.get(Column, column_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_column(db: Session, column_id: UUID) -> bool:
    obj = db.get(Column, column_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Schedule CRUD
# ---------------------------------------------------------------------------

def create_schedule(db: Session, data: ScheduleCreate) -> Schedule:
    obj = Schedule(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_schedule(db: Session, schedule_id: UUID) -> Optional[Schedule]:
    return db.get(Schedule, schedule_id)


def list_schedules(
    db: Session, search: Optional[str] = None, page: int = 1, size: int = 20
) -> tuple[list[Schedule], int]:
    q = db.query(Schedule)
    if search:
        q = q.filter(
            or_(
                Schedule.task_name.ilike(f"%{search}%"),
                Schedule.schedule_desc.ilike(f"%{search}%"),
            )
        )
    total = q.count()
    items = q.order_by(Schedule.task_name).offset((page - 1) * size).limit(size).all()
    return items, total


def update_schedule(db: Session, schedule_id: UUID, data: ScheduleUpdate) -> Optional[Schedule]:
    obj = db.get(Schedule, schedule_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_schedule(db: Session, schedule_id: UUID) -> bool:
    obj = db.get(Schedule, schedule_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Table-Schedule association
# ---------------------------------------------------------------------------

def link_table_schedule(db: Session, table_id: UUID, schedule_id: UUID, relation_type: str = "produces") -> TableSchedule:
    obj = TableSchedule(table_id=table_id, schedule_id=schedule_id, relation_type=relation_type)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def unlink_table_schedule(db: Session, table_id: UUID, schedule_id: UUID) -> bool:
    obj = (
        db.query(TableSchedule)
        .filter(TableSchedule.table_id == table_id, TableSchedule.schedule_id == schedule_id)
        .first()
    )
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Report CRUD
# ---------------------------------------------------------------------------

def create_report(db: Session, data: ReportCreate) -> Report:
    obj = Report(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_report(db: Session, report_id: UUID) -> Optional[Report]:
    return db.get(Report, report_id)


def list_reports(
    db: Session, search: Optional[str] = None, page: int = 1, size: int = 20
) -> tuple[list[Report], int]:
    q = db.query(Report)
    if search:
        q = q.filter(
            or_(
                Report.report_name.ilike(f"%{search}%"),
                Report.description.ilike(f"%{search}%"),
            )
        )
    total = q.count()
    items = q.order_by(Report.report_name).offset((page - 1) * size).limit(size).all()
    return items, total


def update_report(db: Session, report_id: UUID, data: ReportUpdate) -> Optional[Report]:
    obj = db.get(Report, report_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_report(db: Session, report_id: UUID) -> bool:
    obj = db.get(Report, report_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(
    db: Session, q: str, entity_type: Optional[str] = None, size: int = 20
) -> dict[str, list]:
    result: dict[str, list] = {}

    if not entity_type or entity_type == "table":
        tables = (
            db.query(Table)
            .filter(
                or_(
                    Table.table_name.ilike(f"%{q}%"),
                    Table.display_name.ilike(f"%{q}%"),
                    Table.description.ilike(f"%{q}%"),
                )
            )
            .limit(size)
            .all()
        )
        result["tables"] = tables

    if not entity_type or entity_type == "column":
        columns = (
            db.query(Column)
            .filter(
                or_(
                    Column.column_name.ilike(f"%{q}%"),
                    Column.display_name.ilike(f"%{q}%"),
                    Column.description.ilike(f"%{q}%"),
                )
            )
            .limit(size)
            .all()
        )
        result["columns"] = columns

    if not entity_type or entity_type == "task":
        tasks = (
            db.query(Schedule)
            .filter(
                or_(
                    Schedule.task_name.ilike(f"%{q}%"),
                    Schedule.schedule_desc.ilike(f"%{q}%"),
                )
            )
            .limit(size)
            .all()
        )
        result["tasks"] = tasks

    return result
