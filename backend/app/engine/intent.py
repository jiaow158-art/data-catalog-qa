"""Intent classification — rule-based keyword matching."""

from enum import Enum
import re


class Intent(str, Enum):
    LIST_DATABASES = "list_databases"
    LIST_TABLES = "list_tables"
    TABLE_DETAIL = "table_detail"
    TABLE_COLUMNS = "table_columns"
    TABLE_LINEAGE = "table_lineage"
    TABLE_SCHEDULES = "table_schedules"
    SEARCH = "search"


# (pattern, intent, weight)
# Higher weight = more specific, checked first
RULES: list[tuple[str, Intent, int]] = [
    # database listing (require "数据库" not just "库" to avoid matching "ods库有哪些表")
    ("有哪些.*数据库", Intent.LIST_DATABASES, 10),
    ("多少.*数据库", Intent.LIST_DATABASES, 10),
    ("数据库.*(有哪些|列表|概览)", Intent.LIST_DATABASES, 10),
    ("(所有|全部).*数据库", Intent.LIST_DATABASES, 9),
    # lineage
    ("(上游|下游|来源|去向|血缘|依赖)", Intent.TABLE_LINEAGE, 10),
    ("(从哪|到哪|数据.*源|产出.*表)", Intent.TABLE_LINEAGE, 8),
    # schedules
    ("(调度|任务|定时|cron|更新|同步|执行|调度)", Intent.TABLE_SCHEDULES, 10),
    ("(什么时候|几点|多久).*(跑|更新|同步)", Intent.TABLE_SCHEDULES, 9),
    # columns
    ("(字段|列|属性|schema|结构|有哪些.*字段|有哪些.*列)", Intent.TABLE_COLUMNS, 10),
    ("(字段.*含义|字段.*意思|字段.*是什么|字段.*说明)", Intent.TABLE_COLUMNS, 9),
    ("(包含|有什么|有哪些).*(字段|列|信息)", Intent.TABLE_COLUMNS, 9),
    ("(怎么算|计算规则|计算逻辑)", Intent.TABLE_COLUMNS, 9),
    # table detail (single table info)
    ("(描述|说明|用途|是什么|是什么意思)", Intent.TABLE_DETAIL, 7),
    ("(负责|owner|谁.*管)", Intent.TABLE_DETAIL, 6),
    ("(分区|partition|多少.*行|数据量)", Intent.TABLE_DETAIL, 6),
    # table listing (must be after column/table_detail to avoid over-matching)
    ("(有哪些|多少).*(表|table)", Intent.LIST_TABLES, 10),
    ("(表|table).*(有哪些|列表|都有)", Intent.LIST_TABLES, 9),
    ("(ods|dwd|dim|ads).*(表|库|层)", Intent.LIST_TABLES, 8),
    ("(fact|dim|dwd|dws|ads).*(表)", Intent.LIST_TABLES, 8),
]


def classify(question: str) -> tuple[Intent, float]:
    """Return (intent, confidence) for a question."""
    q = question.lower().strip()
    best_intent = Intent.SEARCH
    best_weight = 0

    for pattern, intent, weight in RULES:
        if re.search(pattern, q):
            if weight > best_weight:
                best_weight = weight
                best_intent = intent

    confidence = min(best_weight / 10.0, 1.0)
    return best_intent, confidence
