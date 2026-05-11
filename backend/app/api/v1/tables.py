from __future__ import annotations
import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.schemas.table import (
    TableCreate,
    TableUpdate,
    TableResponse,
    TableListResponse,
    TableDetail,
)
from app.services import metadata_service as svc

router = APIRouter(prefix="/tables", tags=["表元数据"])


@router.post("", response_model=TableResponse, status_code=201)
def create(data: TableCreate, db: Session = DBSession):
    return svc.create_table(db, data)


@router.get("", response_model=TableListResponse)
def list_(
    database_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    table_type: Optional[str] = Query(None, description="fact/dim/dwd/dws/ads"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = DBSession,
):
    items, total = svc.list_tables(
        db, database_id=database_id, search=search, table_type=table_type, page=page, size=size
    )
    return TableListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@router.get("/{table_id}", response_model=TableDetail)
def get(table_id: UUID, db: Session = DBSession):
    obj = svc.get_table_detail(db, table_id)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Table not found")
    return obj


@router.put("/{table_id}", response_model=TableResponse)
def update(table_id: UUID, data: TableUpdate, db: Session = DBSession):
    obj = svc.update_table(db, table_id, data)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Table not found")
    return obj


@router.delete("/{table_id}", status_code=204)
def delete(table_id: UUID, db: Session = DBSession):
    ok = svc.delete_table(db, table_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Table not found")


@router.post("/{table_id}/schedules/{schedule_id}", status_code=201)
def link_schedule(
    table_id: UUID,
    schedule_id: UUID,
    relation_type: str = "produces",
    db: Session = DBSession,
):
    return svc.link_table_schedule(db, table_id, schedule_id, relation_type)


@router.delete("/{table_id}/schedules/{schedule_id}", status_code=204)
def unlink_schedule(table_id: UUID, schedule_id: UUID, db: Session = DBSession):
    ok = svc.unlink_table_schedule(db, table_id, schedule_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Link not found")
