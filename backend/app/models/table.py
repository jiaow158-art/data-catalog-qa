from __future__ import annotations
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Table(Base):
    __tablename__ = "tables"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    database_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("databases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    table_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    table_type: Mapped[Optional[str]] = mapped_column(String(50))
    partition_key: Mapped[Optional[str]] = mapped_column(String(200))
    partition_freq: Mapped[Optional[str]] = mapped_column(String(50))
    primary_keys: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    owner: Mapped[Optional[str]] = mapped_column(String(200))
    tags: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    business_scenarios: Mapped[Optional[str]] = mapped_column(Text)
    usage_notes: Mapped[Optional[str]] = mapped_column(Text)
    row_count_estimate: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    database: Mapped["DatabaseModel"] = relationship("DatabaseModel", back_populates="tables")
    columns: Mapped[list["Column"]] = relationship(
        "Column", back_populates="table", cascade="all, delete-orphan", order_by="Column.sort_order"
    )
    table_schedules: Mapped[list["TableSchedule"]] = relationship(
        "TableSchedule", back_populates="table", cascade="all, delete-orphan"
    )
