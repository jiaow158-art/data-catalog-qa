from __future__ import annotations

from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class DatabaseCreate(BaseModel):
    name: str = Field(..., max_length=255, description="库名，如 dw, ods, dim")
    display_name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    db_type: Optional[str] = Field(None, max_length=50, description="hive/mysql/clickhouse")
    host: Optional[str] = Field(None, max_length=255)


class DatabaseUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    db_type: Optional[str] = Field(None, max_length=50)
    host: Optional[str] = Field(None, max_length=255)


class DatabaseResponse(BaseModel):
    id: UUID
    name: str
    display_name: Optional[str]
    description: Optional[str]
    db_type: Optional[str]
    host: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DatabaseListResponse(BaseModel):
    items: list[DatabaseResponse]
    total: int
    page: int
    size: int
    pages: int
