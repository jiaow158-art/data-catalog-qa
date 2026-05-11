from __future__ import annotations
from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class ColumnCreate(BaseModel):
    table_id: UUID
    column_name: str = Field(..., max_length=500)
    display_name: Optional[str] = Field(None, max_length=500)
    data_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_primary_key: bool = False
    is_nullable: bool = True
    default_value: Optional[str] = Field(None, max_length=500)
    enum_values: Optional[str] = None  # JSON array string
    calculation_rule: Optional[str] = None
    source_info: Optional[str] = None
    null_rate: Optional[float] = None
    distinct_count: Optional[int] = None
    sort_order: int = 0


class ColumnUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=500)
    data_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_primary_key: Optional[bool] = None
    is_nullable: Optional[bool] = None
    default_value: Optional[str] = Field(None, max_length=500)
    enum_values: Optional[str] = None
    calculation_rule: Optional[str] = None
    source_info: Optional[str] = None
    null_rate: Optional[float] = None
    distinct_count: Optional[int] = None
    sort_order: Optional[int] = None


class ColumnResponse(BaseModel):
    id: UUID
    table_id: UUID
    column_name: str
    display_name: Optional[str]
    data_type: Optional[str]
    description: Optional[str]
    is_primary_key: bool
    is_nullable: bool
    default_value: Optional[str]
    enum_values: Optional[str]
    calculation_rule: Optional[str]
    source_info: Optional[str]
    null_rate: Optional[float]
    distinct_count: Optional[int]
    sort_order: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ColumnListResponse(BaseModel):
    items: list[ColumnResponse]
    total: int
    page: int
    size: int
    pages: int
