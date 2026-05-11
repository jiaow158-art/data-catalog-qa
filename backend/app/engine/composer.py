"""Answer composer — template-based + optional LLM."""

from __future__ import annotations
from typing import Optional

from app.engine.intent import Intent


def compose_template(retrieval_result: dict) -> str:
    """Generate a human-readable Chinese answer from structured retrieval data."""
    intent = retrieval_result.get("intent", "")
    data = retrieval_result.get("data") or {}

    if intent == Intent.LIST_DATABASES.value:
        dbs = data.get("databases", [])
        if not dbs:
            return "没有找到数据库实例。"
        lines = [f"共有 **{len(dbs)}** 个数据库：\n"]
        for d in dbs:
            db_type = d.db_type or "unknown"
            desc = d.description or ""
            lines.append(f"- **{d.display_name or d.name}** (`{d.name}`) — {db_type}")
            if desc:
                lines.append(f"  {desc}")
        return "\n".join(lines)

    elif intent == Intent.LIST_TABLES.value:
        tables = data.get("tables", [])
        if not tables:
            return "没有找到匹配的表。"
        lines = [f"找到 **{len(tables)}** 张表：\n"]
        for t in tables:
            ttype = f" [{t.table_type}]" if t.table_type else ""
            owner = f" — 负责人: {t.owner}" if t.owner else ""
            desc = f"\n  {t.description}" if t.description else ""
            lines.append(f"- **{t.display_name or t.table_name}** (`{t.table_name}`){ttype}{owner}{desc}")
        return "\n".join(lines)

    elif intent == Intent.TABLE_DETAIL.value:
        table = data.get("table")
        if not table:
            tables = data.get("tables", [])
            if tables:
                lines = ["你可能想查的是这些表：\n"]
                for t in tables:
                    lines.append(f"- **{t.display_name or t.table_name}** (`{t.table_name}`)")
                return "\n".join(lines)
            return "没有找到匹配的表信息。"
        return _format_table_detail(table)

    elif intent == Intent.TABLE_COLUMNS.value:
        table = data.get("table")
        if table and data.get("show_columns"):
            lines = [f"## {table.display_name or table.table_name} 的字段列表\n"]
            lines.append("| # | 字段名 | 类型 | 说明 |")
            lines.append("|---|--------|------|------|")
            for c in table.columns:
                desc = c.description or "-"
                pk = "PK " if c.is_primary_key else ""
                rule = f" [计算: {c.calculation_rule}]" if c.calculation_rule else ""
                lines.append(f"| {c.sort_order} | {pk}`{c.column_name}` | {c.data_type or '-'} | {desc}{rule} |")
            return "\n".join(lines)
        cols = data.get("columns", [])
        if cols:
            lines = [f"找到 **{len(cols)}** 个匹配字段：\n"]
            for c in cols[:10]:
                lines.append(f"- `{c.column_name}` ({c.data_type or '-'}) — {c.display_name or c.description or '-'}")
            return "\n".join(lines)
        return "没有找到匹配的字段信息。"

    elif intent == Intent.TABLE_LINEAGE.value:
        table = data.get("table")
        if table and data.get("show_lineage"):
            return _format_lineage(table)
        tables = data.get("tables", [])
        if tables:
            lines = ["请指定要查血缘的表，以下是匹配的表：\n"]
            for t in tables:
                lines.append(f"- **{t.display_name or t.table_name}** (`{t.table_name}`)")
            return "\n".join(lines)
        return "没有找到血缘信息。"

    elif intent == Intent.TABLE_SCHEDULES.value:
        table = data.get("table")
        if table and data.get("show_schedules"):
            lines = [f"## {table.display_name or table.table_name} 的调度任务\n"]
            if not table.schedules:
                lines.append("暂无关联调度任务。")
            else:
                for s in table.schedules:
                    status = s.status or "unknown"
                    cron = s.schedule_cron or "-"
                    last = s.last_success_time.strftime("%Y-%m-%d %H:%M") if s.last_success_time else "-"
                    lines.append(f"- **{s.task_name}**")
                    lines.append(f"  Cron: `{cron}` | 状态: {status} | 最近成功: {last}")
                    if s.schedule_desc:
                        lines.append(f"  描述: {s.schedule_desc}")
            return "\n".join(lines)
        return "没有找到匹配的调度任务。"

    else:  # SEARCH
        parts = []
        tables = data.get("tables", [])
        columns = data.get("columns", [])
        tasks = data.get("tasks", [])
        if tables:
            parts.append(f"**表** ({len(tables)})：")
            for t in tables[:5]:
                parts.append(f"- {t.display_name or t.table_name} (`{t.table_name}`)")
        if columns:
            parts.append(f"\n**字段** ({len(columns)})：")
            for c in columns[:5]:
                parts.append(f"- `{c.column_name}` ({c.data_type or '-'})")
        if tasks:
            parts.append(f"\n**任务** ({len(tasks)})：")
            for tk in tasks[:5]:
                parts.append(f"- {tk.task_name}")
        if not parts:
            return "没有找到匹配的元数据。试试换个关键词？"
        return "\n".join(parts)


def _format_table_detail(table) -> str:
    lines = [f"## {table.display_name or table.table_name}\n"]
    lines.append(f"- **表名**: `{table.table_name}`")
    if table.table_type:
        lines.append(f"- **类型**: {table.table_type}")
    if table.owner:
        lines.append(f"- **负责人**: {table.owner}")
    if table.partition_key:
        lines.append(f"- **分区键**: `{table.partition_key}` ({table.partition_freq or '-'})")
    if table.primary_keys:
        lines.append(f"- **主键**: {table.primary_keys}")
    if table.row_count_estimate:
        lines.append(f"- **预估行数**: {table.row_count_estimate:,}")
    if table.tags:
        lines.append(f"- **标签**: {table.tags}")
    if table.description:
        lines.append(f"- **描述**: {table.description}")
    if table.business_scenarios:
        lines.append(f"- **业务场景**: {table.business_scenarios}")
    if table.usage_notes:
        lines.append(f"- **使用说明**: {table.usage_notes}")
    lines.append(f"\n字段数: {len(table.columns)} | 调度任务: {len(table.schedules)} | 上游: {len(table.upstream_tables)} | 下游: {len(table.downstream_tables)}")
    return "\n".join(lines)


def _format_lineage(table) -> str:
    lines = [f"## {table.display_name or table.table_name} 的血缘关系\n"]
    if table.upstream_tables:
        lines.append("### 上游表（数据来源）")
        for t in table.upstream_tables:
            lines.append(f"- **{t.display_name or t.table_name}** (`{t.table_name}`)")
    else:
        lines.append("### 上游表\n(无，即为源表)")
    lines.append("")
    if table.downstream_tables:
        lines.append("### 下游表（数据去向）")
        for t in table.downstream_tables:
            lines.append(f"- **{t.display_name or t.table_name}** (`{t.table_name}`)")
    else:
        lines.append("### 下游表\n(无)")
    return "\n".join(lines)
