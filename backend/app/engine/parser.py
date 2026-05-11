"""Entity recognition — extract table/column/db names from questions."""

from __future__ import annotations
import re
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import DatabaseModel, Table, Column


def extract_entities(
    db: Session, question: str
) -> dict[str, Optional[str]]:
    """
    Extract database_id, table_id, column_id from a question
    by fuzzy-matching against stored metadata names.
    Returns string values suitable for JSON serialization.
    """
    # Internal storage with UUID objects for database queries
    _db_id: Optional[UUID] = None
    _db_name: Optional[str] = None
    _table_id: Optional[UUID] = None
    _table_name: Optional[str] = None
    _col_id: Optional[UUID] = None
    _col_name: Optional[str] = None

    # 1. Try exact/substring match on table names (most specific first)
    tables = db.query(Table).all()
    for table in tables:
        # Check display_name first (Chinese), then table_name
        if table.display_name and table.display_name in question:
            _table_id = table.id
            _table_name = table.table_name
            _db_id = table.database_id
            break
        if table.table_name in question:
            _table_id = table.id
            _table_name = table.table_name
            _db_id = table.database_id
            break

    # Fuzzy match: extract Chinese character sequences from the question,
    # and check if any of them appear in table display_name or table_name
    if not _table_id:
        # Split question by common question words to extract candidate entity names
        import re as _re
        question_words = _re.split(
            r"(有哪些|多少|是什么|是什么意思|列表|.*怎么样|在哪里|是谁|的|什么|哪些|哪个|几个|查询|帮我|我要|我想|查看)",
            question,
        )
        candidates = [w.strip() for w in question_words if w.strip() and len(w.strip()) >= 2]
        # Also try removing common suffixes
        bare_candidates = []
        for c in candidates:
            stripped = c
            for sfx in ["表", "字段", "列", "库", "数据库", "的"]:
                if stripped.endswith(sfx):
                    stripped = stripped[:-len(sfx)]
            if stripped and len(stripped) >= 2:
                bare_candidates.append(stripped)

        all_candidates = candidates + bare_candidates
        for table in tables:
            matched = False
            for cand in all_candidates:
                if (table.display_name and cand in table.display_name) or cand in table.table_name:
                    matched = True
                    break
                # Check if display_name contains candidate as a subsequence
                # e.g., "订单表" is a subsequence of "订单原始表"? No, but "订单" is.
                # Check if table display_name starts with the candidate
                if table.display_name and table.display_name.startswith(cand):
                    matched = True
                    break
            if matched:
                _table_id = table.id
                _table_name = table.table_name
                _db_id = table.database_id
                break

    # If no table matched by name, try LIKE search on question keywords
    if not _table_id:
        keywords = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", question)
        for kw in keywords:
            match = db.query(Table).filter(Table.table_name.ilike(f"%{kw}%")).first()
            if match:
                _table_id = match.id
                _table_name = match.table_name
                _db_id = match.database_id
                break

    # 2. Try to match database name
    dbs = db.query(DatabaseModel).all()
    for d in dbs:
        if d.name in question.lower():
            _db_id = d.id
            _db_name = d.name
            break

    # 3. Try to match column name (if we found a table, search within it)
    if _table_id:
        cols = (
            db.query(Column)
            .filter(Column.table_id == _table_id)
            .all()
        )
        for col in cols:
            if col.column_name in question or (col.display_name and col.display_name in question):
                _col_id = col.id
                _col_name = col.column_name
                break

    return {
        "database_id": str(_db_id) if _db_id else None,
        "database_name": _db_name,
        "table_id": str(_table_id) if _table_id else None,
        "table_name": _table_name,
        "column_id": str(_col_id) if _col_id else None,
        "column_name": _col_name,
    }
