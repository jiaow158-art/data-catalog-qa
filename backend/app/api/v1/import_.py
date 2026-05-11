from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.services import import_service as svc

router = APIRouter(prefix="/import", tags=["数据导入"])


@router.post("/upload")
def upload(
    file: UploadFile = File(...),
    entity_type: str = Form(..., description="tables / columns / schedules / table_lineage"),
    db: Session = DBSession,
):
    """Upload a CSV or Excel file and return a preview."""
    if entity_type not in svc.ENTITY_CONFIG:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的实体类型: {entity_type}，可选: {', '.join(svc.ENTITY_CONFIG)}",
        )

    try:
        content = file.file.read()
        return svc.create_preview(db, content, file.filename, entity_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {e}")


@router.post("/confirm")
def confirm(
    preview_id: str = Form(..., description="预览 ID，从 /upload 返回"),
    db: Session = DBSession,
):
    """Confirm and execute the import for a previously-uploaded preview."""
    try:
        return svc.confirm_import(db, preview_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
