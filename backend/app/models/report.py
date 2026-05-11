from __future__ import annotations
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    report_name: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    report_url: Mapped[Optional[str]] = mapped_column(String(1000))
    bi_tool: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    report_tables: Mapped[list["ReportTable"]] = relationship(
        "ReportTable", back_populates="report", cascade="all, delete-orphan"
    )


class ReportTable(Base):
    __tablename__ = "report_tables"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )

    report: Mapped["Report"] = relationship("Report", back_populates="report_tables")
    table: Mapped["Table"] = relationship("Table")
