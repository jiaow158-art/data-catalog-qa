from __future__ import annotations
import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse, ReportListResponse
from app.services import metadata_service as svc

router = APIRouter(prefix="/reports", tags=["报表"])


@router.post("", response_model=ReportResponse, status_code=201)
def create(data: ReportCreate, db: Session = DBSession):
    return svc.create_report(db, data)


@router.get("", response_model=ReportListResponse)
def list_(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = DBSession,
):
    items, total = svc.list_reports(db, search=search, page=page, size=size)
    return ReportListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get(report_id: UUID, db: Session = DBSession):
    obj = svc.get_report(db, report_id)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")
    return obj


@router.put("/{report_id}", response_model=ReportResponse)
def update(report_id: UUID, data: ReportUpdate, db: Session = DBSession):
    obj = svc.update_report(db, report_id, data)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")
    return obj


@router.delete("/{report_id}", status_code=204)
def delete(report_id: UUID, db: Session = DBSession):
    ok = svc.delete_report(db, report_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")
