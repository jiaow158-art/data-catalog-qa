from __future__ import annotations
from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    task_name: str = Field(..., max_length=500)
    task_type: Optional[str] = Field(None, max_length=50, description="spark/hive_sql/python")
    schedule_cron: Optional[str] = Field(None, max_length=100)
    schedule_desc: Optional[str] = Field(None, max_length=500)
    owner: Optional[str] = Field(None, max_length=200)
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    last_duration_sec: Optional[int] = None
    status: Optional[str] = Field(None, max_length=50)
    task_config: Optional[str] = None


class ScheduleUpdate(BaseModel):
    task_type: Optional[str] = Field(None, max_length=50)
    schedule_cron: Optional[str] = Field(None, max_length=100)
    schedule_desc: Optional[str] = Field(None, max_length=500)
    owner: Optional[str] = Field(None, max_length=200)
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    last_duration_sec: Optional[int] = None
    status: Optional[str] = Field(None, max_length=50)
    task_config: Optional[str] = None


class ScheduleResponse(BaseModel):
    id: UUID
    task_name: str
    task_type: Optional[str]
    schedule_cron: Optional[str]
    schedule_desc: Optional[str]
    owner: Optional[str]
    last_success_time: Optional[datetime]
    last_failure_time: Optional[datetime]
    last_duration_sec: Optional[int]
    status: Optional[str]
    task_config: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TableScheduleCreate(BaseModel):
    table_id: UUID
    schedule_id: UUID
    relation_type: str = "produces"


class TableScheduleResponse(BaseModel):
    id: UUID
    table_id: UUID
    schedule_id: UUID
    relation_type: str

    model_config = {"from_attributes": True}


class ScheduleListResponse(BaseModel):
    items: list[ScheduleResponse]
    total: int
    page: int
    size: int
    pages: int
