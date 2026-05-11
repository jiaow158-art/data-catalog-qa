"""Q&A orchestration service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.engine.intent import classify
from app.engine.parser import extract_entities
from app.engine.retriever import retrieve
from app.engine.composer import compose_template
from app.engine.llm.base import BaseLLM, NoOpLLM
from app.engine.llm.openai_llm import OpenAILLM


QA_SYSTEM_PROMPT = """你是一个数据仓库元数据查询助手。根据提供的元数据信息，用中文回答用户的问题。
- 回答要简洁、准确、结构化
- 如果元数据不足，如实告知
- 使用 Markdown 格式

提供的元数据：
{context}"""


def _get_llm(use_llm: bool) -> BaseLLM:
    if not use_llm:
        return NoOpLLM()
    return OpenAILLM()


def ask(db: Session, question: str, use_llm: bool = False) -> dict:
    """Main Q&A pipeline."""
    # Step 1: Intent classification
    intent, confidence = classify(question)

    # Step 2: Entity recognition
    entities = extract_entities(db, question)

    # Step 3: Metadata retrieval
    retrieval_result = retrieve(db, intent, entities, question)

    # Step 4: Compose answer (template-based)
    template_answer = compose_template(retrieval_result)

    # Step 5: LLM enhancement (optional)
    llm = _get_llm(use_llm)
    llm_answer = ""
    if use_llm:
        context = _serialize_context(retrieval_result)
        llm_answer = llm.generate(
            system_prompt=QA_SYSTEM_PROMPT.format(context=context),
            user_prompt=question,
        )

    final_answer = llm_answer if llm_answer else template_answer

    return {
        "question": question,
        "answer": final_answer,
        "intent": intent.value,
        "confidence": confidence,
        "entities": entities,
        "used_llm": bool(llm_answer),
    }


def _serialize_context(retrieval_result: dict) -> str:
    """Convert retrieval result to a compact text representation for LLM context."""
    data = retrieval_result.get("data") or {}
    parts = []

    # Databases
    for d in data.get("databases", []):
        parts.append(
            f"[DB] {d.name} | {d.display_name or ''} | type={d.db_type} | {d.description or ''}"
        )

    # Tables
    for t in data.get("tables", []):
        parts.append(
            f"[TABLE] {t.table_name} | {t.display_name or ''} | type={t.table_type or ''} "
            f"| owner={t.owner or ''} | rows={t.row_count_estimate or ''} "
            f"| desc={t.description or ''}"
        )

    # Columns
    for c in data.get("columns", []):
        parts.append(
            f"[COL] {c.column_name} | {c.display_name or ''} | type={c.data_type or ''} "
            f"| desc={c.description or ''}"
        )

    # Task
    for tk in data.get("tasks", []):
        parts.append(f"[TASK] {tk.task_name} | {tk.schedule_desc or ''} | status={tk.status or ''}")

    # Table detail
    table = data.get("table")
    if table:
        parts.append(f"[TABLE_DETAIL] {table.table_name} | {table.display_name or ''}")
        for c in table.columns:
            parts.append(f"[COL] {c.column_name} | {c.display_name or ''} | {c.data_type or ''}")
        for s in table.schedules:
            parts.append(f"[SCHEDULE] {s.task_name} | {s.schedule_desc or ''} | {s.status or ''}")
        for u in table.upstream_tables:
            parts.append(f"[UPSTREAM] {u.table_name}")
        for d in table.downstream_tables:
            parts.append(f"[DOWNSTREAM] {d.table_name}")

    return "\n".join(parts)
