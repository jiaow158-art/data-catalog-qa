from __future__ import annotations

from typing import Optional
import math
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.schemas.database import DatabaseCreate, DatabaseUpdate, DatabaseResponse, DatabaseListResponse
from app.services import metadata_service as svc

router = APIRouter(prefix="/databases", tags=["数据库实例"])


@router.post("", response_model=DatabaseResponse, status_code=201)
def create(data: DatabaseCreate, db: Session = DBSession):
    return svc.create_database(db, data)


@router.get("", response_model=DatabaseListResponse)
def list_(
    search: Optional[str] = Query(None, description="按名称搜索"),
    db_type: Optional[str] = Query(None, description="数据库类型"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = DBSession,
):
    items, total = svc.list_databases(db, search=search, db_type=db_type, page=page, size=size)
    return DatabaseListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@router.get("/{db_id}", response_model=DatabaseResponse)
def get(db_id: UUID, db: Session = DBSession):
    obj = svc.get_database(db, db_id)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Database not found")
    return obj


@router.put("/{db_id}", response_model=DatabaseResponse)
def update(db_id: UUID, data: DatabaseUpdate, db: Session = DBSession):
    obj = svc.update_database(db, db_id, data)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Database not found")
    return obj


@router.delete("/{db_id}", status_code=204)
def delete(db_id: UUID, db: Session = DBSession):
    ok = svc.delete_database(db, db_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Database not found")
