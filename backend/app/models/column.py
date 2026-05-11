from __future__ import annotations
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Column(Base):
    __tablename__ = "columns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False, index=True
    )
    column_name: Mapped[str] = mapped_column(String(500), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(500))
    data_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_primary_key: Mapped[bool] = mapped_column(Boolean, default=False)
    is_nullable: Mapped[bool] = mapped_column(Boolean, default=True)
    default_value: Mapped[Optional[str]] = mapped_column(String(500))
    enum_values: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    calculation_rule: Mapped[Optional[str]] = mapped_column(Text)
    source_info: Mapped[Optional[str]] = mapped_column(Text)
    null_rate: Mapped[Optional[float]] = mapped_column(Float)
    distinct_count: Mapped[Optional[int]] = mapped_column(Integer)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    table: Mapped["Table"] = relationship("Table", back_populates="columns")
