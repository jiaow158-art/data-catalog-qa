from __future__ import annotations
from datetime import datetime
from typing import Generic, TypeVar, Optional
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}


class TimestampMixin(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
