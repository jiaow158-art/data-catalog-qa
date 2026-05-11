"""Lineage service — CRUD + graph traversal."""

from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Table, TableLineage, Column, ColumnLineage


# ---------------------------------------------------------------------------
# Table Lineage CRUD
# ---------------------------------------------------------------------------

def create_table_lineage(
    db: Session,
    upstream_table_id: UUID,
    downstream_table_id: UUID,
    relation_desc: Optional[str] = None,
) -> TableLineage:
    obj = TableLineage(
        upstream_table_id=upstream_table_id,
        downstream_table_id=downstream_table_id,
        relation_desc=relation_desc,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete_table_lineage(db: Session, lineage_id: UUID) -> bool:
    obj = db.get(TableLineage, lineage_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def get_direct_lineage(db: Session, table_id: UUID) -> dict:
    """Get direct upstream and downstream tables."""
    upstream = (
        db.query(Table)
        .join(TableLineage, Table.id == TableLineage.upstream_table_id)
        .filter(TableLineage.downstream_table_id == table_id)
        .all()
    )
    downstream = (
        db.query(Table)
        .join(TableLineage, Table.id == TableLineage.downstream_table_id)
        .filter(TableLineage.upstream_table_id == table_id)
        .all()
    )
    edges = (
        db.query(TableLineage)
        .filter(
            (TableLineage.upstream_table_id == table_id)
            | (TableLineage.downstream_table_id == table_id)
        )
        .all()
    )
    return {
        "upstream": upstream,
        "downstream": downstream,
        "edges": edges,
    }


def get_lineage_graph(
    db: Session,
    table_id: UUID,
    depth: int = 3,
    direction: str = "both",
) -> dict:
    """
    BFS traversal to build N-hop lineage graph.
    Returns {nodes: [...], edges: [...]} suitable for DAG rendering.
    """
    # Cache all tables and lineage edges to avoid N+1 queries
    all_tables = {t.id: t for t in db.query(Table).all()}
    all_edges = db.query(TableLineage).all()

    # Build adjacency index
    upstream_of: dict[UUID, list[TableLineage]] = {}  # downstream -> [edges where it's downstream]
    downstream_of: dict[UUID, list[TableLineage]] = {}  # upstream -> [edges where it's upstream]

    for edge in all_edges:
        up_id = edge.upstream_table_id
        down_id = edge.downstream_table_id
        if down_id not in upstream_of:
            upstream_of[down_id] = []
        upstream_of[down_id].append(edge)
        if up_id not in downstream_of:
            downstream_of[up_id] = []
        downstream_of[up_id].append(edge)

    visited_nodes: set[UUID] = set()
    visited_edges: set[UUID] = set()
    nodes: list[dict] = []
    edges: list[dict] = []

    # Add starting node
    start_table = all_tables.get(table_id)
    if start_table:
        visited_nodes.add(table_id)
        nodes.append(_table_node(start_table, is_focus=True))

    # BFS
    queue: list[tuple[UUID, int]] = [(table_id, 0)]

    while queue:
        current_id, current_depth = queue.pop(0)
        if current_depth >= depth:
            continue

        # Upstream: current is downstream of some upstream tables
        if direction in ("upstream", "both"):
            for edge in upstream_of.get(current_id, []):
                up_id = edge.upstream_table_id
                if edge.id not in visited_edges:
                    visited_edges.add(edge.id)
                    edges.append({
                        "id": str(edge.id),
                        "source": str(up_id),
                        "target": str(current_id),
                        "label": edge.relation_desc or "",
                    })
                if up_id not in visited_nodes:
                    visited_nodes.add(up_id)
                    tbl = all_tables.get(up_id)
                    if tbl:
                        nodes.append(_table_node(tbl, depth=current_depth + 1))
                    queue.append((up_id, current_depth + 1))

        # Downstream: current is upstream of some downstream tables
        if direction in ("downstream", "both"):
            for edge in downstream_of.get(current_id, []):
                down_id = edge.downstream_table_id
                if edge.id not in visited_edges:
                    visited_edges.add(edge.id)
                    edges.append({
                        "id": str(edge.id),
                        "source": str(current_id),
                        "target": str(down_id),
                        "label": edge.relation_desc or "",
                    })
                if down_id not in visited_nodes:
                    visited_nodes.add(down_id)
                    tbl = all_tables.get(down_id)
                    if tbl:
                        nodes.append(_table_node(tbl, depth=current_depth + 1))
                    queue.append((down_id, current_depth + 1))

    return {"nodes": nodes, "edges": edges}


def _table_node(table: Table, is_focus: bool = False, depth: int = 0) -> dict:
    return {
        "id": str(table.id),
        "table_name": table.table_name,
        "display_name": table.display_name or table.table_name,
        "table_type": table.table_type or "",
        "owner": table.owner or "",
        "is_focus": is_focus,
        "depth": depth,
    }


# ---------------------------------------------------------------------------
# Column Lineage CRUD
# ---------------------------------------------------------------------------

def create_column_lineage(
    db: Session,
    upstream_column_id: UUID,
    downstream_column_id: UUID,
    transform_rule: Optional[str] = None,
    relation_desc: Optional[str] = None,
) -> ColumnLineage:
    obj = ColumnLineage(
        upstream_column_id=upstream_column_id,
        downstream_column_id=downstream_column_id,
        transform_rule=transform_rule,
        relation_desc=relation_desc,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete_column_lineage(db: Session, lineage_id: UUID) -> bool:
    obj = db.get(ColumnLineage, lineage_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def get_column_lineage(db: Session, column_id: UUID) -> dict:
    upstream = (
        db.query(Column)
        .join(ColumnLineage, Column.id == ColumnLineage.upstream_column_id)
        .filter(ColumnLineage.downstream_column_id == column_id)
        .all()
    )
    downstream = (
        db.query(Column)
        .join(ColumnLineage, Column.id == ColumnLineage.downstream_column_id)
        .filter(ColumnLineage.upstream_column_id == column_id)
        .all()
    )
    return {"upstream": upstream, "downstream": downstream}
