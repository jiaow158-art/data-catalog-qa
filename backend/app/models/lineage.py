from __future__ import annotations
import uuid
from typing import Optional

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TableLineage(Base):
    __tablename__ = "table_lineage"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    upstream_table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False, index=True
    )
    downstream_table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relation_desc: Mapped[Optional[str]] = mapped_column(String(500))

    upstream_table: Mapped["Table"] = relationship(
        "Table", foreign_keys=[upstream_table_id], backref="downstream_lineages"
    )
    downstream_table: Mapped["Table"] = relationship(
        "Table", foreign_keys=[downstream_table_id], backref="upstream_lineages"
    )


class ColumnLineage(Base):
    __tablename__ = "column_lineage"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    upstream_column_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("columns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    downstream_column_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("columns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transform_rule: Mapped[Optional[str]] = mapped_column(Text)
    relation_desc: Mapped[Optional[str]] = mapped_column(String(500))

    upstream_column: Mapped["Column"] = relationship(
        "Column", foreign_keys=[upstream_column_id], backref="downstream_column_lineages"
    )
    downstream_column: Mapped["Column"] = relationship(
        "Column", foreign_keys=[downstream_column_id], backref="upstream_column_lineages"
    )
