from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.schemas.table import TableResponse
from app.schemas.column import ColumnResponse
from app.schemas.schedule import ScheduleResponse
from app.services import metadata_service as svc

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("")
def search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    type: Optional[str] = Query(None, description="table/column/task"),
    size: int = Query(20, ge=1, le=50),
    db: Session = DBSession,
):
    """全局搜索，支持表名、字段名、任务名"""
    results = svc.search(db, q=q, entity_type=type, size=size)
    return {
        "tables": [TableResponse.model_validate(t) for t in results.get("tables", [])],
        "columns": [ColumnResponse.model_validate(c) for c in results.get("columns", [])],
        "tasks": [ScheduleResponse.model_validate(s) for s in results.get("tasks", [])],
    }
