from __future__ import annotations
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_name: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    task_type: Mapped[Optional[str]] = mapped_column(String(50))
    schedule_cron: Mapped[Optional[str]] = mapped_column(String(100))
    schedule_desc: Mapped[Optional[str]] = mapped_column(String(500))
    owner: Mapped[Optional[str]] = mapped_column(String(200))
    last_success_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_failure_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_duration_sec: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    task_config: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    table_schedules: Mapped[list["TableSchedule"]] = relationship(
        "TableSchedule", back_populates="schedule", cascade="all, delete-orphan"
    )


class TableSchedule(Base):
    __tablename__ = "table_schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String(50), default="produces")

    table: Mapped["Table"] = relationship("Table", back_populates="table_schedules")
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="table_schedules")
