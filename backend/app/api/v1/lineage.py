from __future__ import annotations
from uuid import UUID

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.schemas.lineage import (
    TableLineageCreate,
    TableLineageResponse,
    ColumnLineageCreate,
    ColumnLineageResponse,
    LineageGraphResponse,
    DirectLineageResponse,
)
from app.services import lineage_service

router = APIRouter(prefix="/lineage", tags=["血缘管理"])


# ── Table Lineage ──────────────────────────────────────────────

@router.get("/tables/{table_id}", response_model=DirectLineageResponse)
def get_table_lineage(table_id: UUID, db: Session = DBSession):
    return lineage_service.get_direct_lineage(db, table_id)


@router.get("/tables/{table_id}/graph", response_model=LineageGraphResponse)
def get_table_lineage_graph(
    table_id: UUID,
    depth: int = Query(3, ge=1, le=5, description="递归深度"),
    direction: str = Query("both", description="upstream/downstream/both"),
    db: Session = DBSession,
):
    return lineage_service.get_lineage_graph(db, table_id, depth=depth, direction=direction)


@router.post("/tables", response_model=TableLineageResponse, status_code=201)
def create_table_lineage(data: TableLineageCreate, db: Session = DBSession):
    return lineage_service.create_table_lineage(
        db,
        upstream_table_id=data.upstream_table_id,
        downstream_table_id=data.downstream_table_id,
        relation_desc=data.relation_desc,
    )


@router.delete("/tables/{lineage_id}", status_code=204)
def delete_table_lineage(lineage_id: UUID, db: Session = DBSession):
    ok = lineage_service.delete_table_lineage(db, lineage_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Lineage not found")


# ── Column Lineage ─────────────────────────────────────────────

@router.get("/columns/{column_id}", response_model=dict)
def get_column_lineage(column_id: UUID, db: Session = DBSession):
    return lineage_service.get_column_lineage(db, column_id)


@router.post("/columns", response_model=ColumnLineageResponse, status_code=201)
def create_column_lineage(data: ColumnLineageCreate, db: Session = DBSession):
    return lineage_service.create_column_lineage(
        db,
        upstream_column_id=data.upstream_column_id,
        downstream_column_id=data.downstream_column_id,
        transform_rule=data.transform_rule,
        relation_desc=data.relation_desc,
    )


@router.delete("/columns/{lineage_id}", status_code=204)
def delete_column_lineage(lineage_id: UUID, db: Session = DBSession):
    ok = lineage_service.delete_column_lineage(db, lineage_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Lineage not found")
