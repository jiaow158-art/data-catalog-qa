from __future__ import annotations
import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleListResponse
from app.services import metadata_service as svc

router = APIRouter(prefix="/schedules", tags=["调度任务"])


@router.post("", response_model=ScheduleResponse, status_code=201)
def create(data: ScheduleCreate, db: Session = DBSession):
    return svc.create_schedule(db, data)


@router.get("", response_model=ScheduleListResponse)
def list_(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = DBSession,
):
    items, total = svc.list_schedules(db, search=search, page=page, size=size)
    return ScheduleListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get(schedule_id: UUID, db: Session = DBSession):
    obj = svc.get_schedule(db, schedule_id)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Schedule not found")
    return obj


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update(schedule_id: UUID, data: ScheduleUpdate, db: Session = DBSession):
    obj = svc.update_schedule(db, schedule_id, data)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Schedule not found")
    return obj


@router.delete("/{schedule_id}", status_code=204)
def delete(schedule_id: UUID, db: Session = DBSession):
    ok = svc.delete_schedule(db, schedule_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Schedule not found")
