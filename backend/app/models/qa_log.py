from __future__ import annotations
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import String, Text, SmallInteger, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QALog(Base):
    __tablename__ = "qa_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[Optional[str]] = mapped_column(String(100))
    matched_tables: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    answer: Mapped[Optional[str]] = mapped_column(Text)
    sources: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    user_feedback: Mapped[int] = mapped_column(SmallInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
