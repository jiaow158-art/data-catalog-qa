from __future__ import annotations
from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    report_name: str = Field(..., max_length=500)
    report_url: Optional[str] = Field(None, max_length=1000)
    bi_tool: Optional[str] = Field(None, max_length=50, description="metabase/superset/tableau")
    description: Optional[str] = None
    owner: Optional[str] = Field(None, max_length=200)


class ReportUpdate(BaseModel):
    report_name: Optional[str] = Field(None, max_length=500)
    report_url: Optional[str] = Field(None, max_length=1000)
    bi_tool: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    owner: Optional[str] = Field(None, max_length=200)


class ReportResponse(BaseModel):
    id: UUID
    report_name: str
    report_url: Optional[str]
    bi_tool: Optional[str]
    description: Optional[str]
    owner: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int
    page: int
    size: int
    pages: int
