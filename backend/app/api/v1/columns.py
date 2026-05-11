from __future__ import annotations

from typing import Optional
import math
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.schemas.column import ColumnCreate, ColumnUpdate, ColumnResponse, ColumnListResponse
from app.services import metadata_service as svc

router = APIRouter(prefix="/columns", tags=["字段元数据"])


@router.post("", response_model=ColumnResponse, status_code=201)
def create(data: ColumnCreate, db: Session = DBSession):
    return svc.create_column(db, data)


@router.get("", response_model=ColumnListResponse)
def list_(
    table_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = DBSession,
):
    items, total = svc.list_columns(db, table_id=table_id, search=search, page=page, size=size)
    return ColumnListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@router.get("/{column_id}", response_model=ColumnResponse)
def get(column_id: UUID, db: Session = DBSession):
    obj = svc.get_column(db, column_id)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Column not found")
    return obj


@router.put("/{column_id}", response_model=ColumnResponse)
def update(column_id: UUID, data: ColumnUpdate, db: Session = DBSession):
    obj = svc.update_column(db, column_id, data)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Column not found")
    return obj


@router.delete("/{column_id}", status_code=204)
def delete(column_id: UUID, db: Session = DBSession):
    ok = svc.delete_column(db, column_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Column not found")
