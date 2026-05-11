"""Metadata retriever — fetch data based on intent + entities."""

from __future__ import annotations
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.engine.intent import Intent
from app.services import metadata_service as svc


def _to_uuid(s: Optional[str]) -> Optional[UUID]:
    if s is None:
        return None
    try:
        return UUID(s)
    except (ValueError, AttributeError):
        return None


def retrieve(
    db: Session,
    intent: Intent,
    entities: dict[str, Optional[str]],
    question: str,
) -> dict:
    """Retrieve metadata relevant to the intent and entities."""
    result: dict = {"intent": intent.value, "data": None}

    table_id = _to_uuid(entities.get("table_id"))
    database_id = _to_uuid(entities.get("database_id"))

    if intent == Intent.LIST_DATABASES:
        items, total = svc.list_databases(db, size=50)
        result["data"] = {"databases": items, "total": total}

    elif intent == Intent.LIST_TABLES:
        items, total = svc.list_tables(
            db, database_id=database_id, size=50
        )
        result["data"] = {"tables": items, "total": total}

    elif intent == Intent.TABLE_DETAIL:
        if table_id:
            detail = svc.get_table_detail(db, table_id)
            result["data"] = {"table": detail}
        else:
            # search for matching tables
            items, total = svc.list_tables(db, search=question, size=5)
            result["data"] = {"tables": items, "total": total, "fallback": True}

    elif intent == Intent.TABLE_COLUMNS:
        if table_id:
            detail = svc.get_table_detail(db, table_id)
            result["data"] = {"table": detail, "show_columns": True}
        else:
            # try column search
            cols, total = svc.list_columns(db, search=question, size=10)
            result["data"] = {"columns": cols, "total": total, "fallback": True}

    elif intent == Intent.TABLE_LINEAGE:
        if table_id:
            detail = svc.get_table_detail(db, table_id)
            result["data"] = {"table": detail, "show_lineage": True}
        else:
            items, _ = svc.list_tables(db, search=question, size=5)
            result["data"] = {"tables": items, "fallback": True}

    elif intent == Intent.TABLE_SCHEDULES:
        if table_id:
            detail = svc.get_table_detail(db, table_id)
            result["data"] = {"table": detail, "show_schedules": True}
        else:
            items, _ = svc.list_tables(db, search=question, size=5)
            result["data"] = {"tables": items, "fallback": True}

    else:  # SEARCH — general fallback
        search_result = svc.search(db, question, size=20)
        result["data"] = search_result

    return result
