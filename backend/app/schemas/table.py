from __future__ import annotations
from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class TableCreate(BaseModel):
    database_id: UUID
    table_name: str = Field(..., max_length=500)
    display_name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    table_type: Optional[str] = Field(None, max_length=50, description="fact/dim/dwd/dws/ads")
    partition_key: Optional[str] = Field(None, max_length=200)
    partition_freq: Optional[str] = Field(None, max_length=50, description="daily/hourly/monthly")
    primary_keys: Optional[str] = None  # JSON array string
    owner: Optional[str] = Field(None, max_length=200)
    tags: Optional[str] = None  # JSON array string
    business_scenarios: Optional[str] = None
    usage_notes: Optional[str] = None
    row_count_estimate: Optional[int] = None


class TableUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    table_type: Optional[str] = Field(None, max_length=50)
    partition_key: Optional[str] = Field(None, max_length=200)
    partition_freq: Optional[str] = Field(None, max_length=50)
    primary_keys: Optional[str] = None
    owner: Optional[str] = Field(None, max_length=200)
    tags: Optional[str] = None
    business_scenarios: Optional[str] = None
    usage_notes: Optional[str] = None
    row_count_estimate: Optional[int] = None


class TableResponse(BaseModel):
    id: UUID
    database_id: UUID
    table_name: str
    display_name: Optional[str]
    description: Optional[str]
    table_type: Optional[str]
    partition_key: Optional[str]
    partition_freq: Optional[str]
    primary_keys: Optional[str]
    owner: Optional[str]
    tags: Optional[str]
    business_scenarios: Optional[str]
    usage_notes: Optional[str]
    row_count_estimate: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TableListResponse(BaseModel):
    items: list[TableResponse]
    total: int
    page: int
    size: int
    pages: int


class ColumnBrief(BaseModel):
    id: UUID
    column_name: str
    display_name: Optional[str]
    data_type: Optional[str]
    description: Optional[str]
    is_primary_key: bool
    calculation_rule: Optional[str]
    enum_values: Optional[str]
    sort_order: int

    model_config = {"from_attributes": True}


class ScheduleBrief(BaseModel):
    id: UUID
    task_name: str
    schedule_desc: Optional[str]
    last_success_time: Optional[datetime]
    status: Optional[str]

    model_config = {"from_attributes": True}


class LineageBrief(BaseModel):
    id: UUID
    table_name: str
    display_name: Optional[str]

    model_config = {"from_attributes": True}


class TableDetail(BaseModel):
    id: UUID
    database_id: UUID
    table_name: str
    display_name: Optional[str]
    description: Optional[str]
    table_type: Optional[str]
    partition_key: Optional[str]
    partition_freq: Optional[str]
    primary_keys: Optional[str]
    owner: Optional[str]
    tags: Optional[str]
    business_scenarios: Optional[str]
    usage_notes: Optional[str]
    row_count_estimate: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    columns: list[ColumnBrief]
    schedules: list[ScheduleBrief]
    upstream_tables: list[LineageBrief]
    downstream_tables: list[LineageBrief]

    model_config = {"from_attributes": True}
