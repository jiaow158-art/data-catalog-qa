from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


# ── Table Lineage ──────────────────────────────────────────────

class TableLineageCreate(BaseModel):
    upstream_table_id: UUID
    downstream_table_id: UUID
    relation_desc: Optional[str] = Field(None, max_length=500)


class TableLineageResponse(BaseModel):
    id: UUID
    upstream_table_id: UUID
    downstream_table_id: UUID
    relation_desc: Optional[str]

    model_config = {"from_attributes": True}


# ── Column Lineage ─────────────────────────────────────────────

class ColumnLineageCreate(BaseModel):
    upstream_column_id: UUID
    downstream_column_id: UUID
    transform_rule: Optional[str] = None
    relation_desc: Optional[str] = Field(None, max_length=500)


class ColumnLineageResponse(BaseModel):
    id: UUID
    upstream_column_id: UUID
    downstream_column_id: UUID
    transform_rule: Optional[str]
    relation_desc: Optional[str]

    model_config = {"from_attributes": True}


# ── Lineage Graph (DAG) ────────────────────────────────────────

class GraphNode(BaseModel):
    id: str
    table_name: str
    display_name: str
    table_type: str
    owner: str
    is_focus: bool = False
    depth: int = 0


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str = ""


class LineageGraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# ── Direct Lineage ─────────────────────────────────────────────

class TableBrief(BaseModel):
    id: UUID
    table_name: str
    display_name: Optional[str]
    table_type: Optional[str]
    owner: Optional[str]

    model_config = {"from_attributes": True}


class DirectLineageResponse(BaseModel):
    upstream: list[TableBrief]
    downstream: list[TableBrief]
    edges: list[TableLineageResponse]
