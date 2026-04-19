import uuid
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.dataset import Dataset
from app.models.query_log import QueryLog
from app.models.user import User
from app.dependencies import get_current_user
from app.agents.pipeline import run_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    question: str


def _parse_json_field(value):
    """Parse a JSON field that may be stored as a string (SQLite) or dict."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


@router.post("/{dataset_id}")
async def submit_query(
    dataset_id: str,
    req: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.user_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(404, "Dataset not found")
    if ds.status == "failed":
        raise HTTPException(422, f"Dataset failed: {ds.error}. Please re-upload.")
    if ds.status != "ready":
        raise HTTPException(422, f"Dataset is {ds.status}. Wait for processing to complete.")

    schema_info = _parse_json_field(ds.schema_info) or {}

    output = await run_pipeline(
        question=req.question,
        dataset_id=ds.id,
        file_path=ds.file_path,
        file_type=ds.file_type,
        schema_info=schema_info,
    )

    # Save audit log
    query_id = str(uuid.uuid4())
    log = QueryLog(
        id=query_id,
        user_id=current_user.id,
        dataset_id=ds.id,
        question=req.question,
        intent=output.get("intent"),
        sql_executed=output.get("sql_executed"),
        answer_narrative=output.get("answer"),
        chart_spec=json.dumps(output.get("chart_spec")) if output.get("chart_spec") else None,
        sources=json.dumps(output.get("sources", [])),
        model_used=output.get("model_used"),
        tokens_used=output.get("tokens_used", 0),
        latency_ms=output.get("latency_ms", 0),
        error=output.get("error"),
    )
    db.add(log)
    try:
        await db.commit()
    except Exception as e:
        logger.warning(f"Audit log save failed: {e}")
        await db.rollback()

    return {
        "query_id": query_id,
        "intent": output.get("intent", "unknown"),
        "answer": output.get("answer", ""),
        "key_metric": output.get("key_metric", ""),
        "chart_spec": output.get("chart_spec"),
        "sources": output.get("sources", []),
        "sql_executed": output.get("sql_executed"),
        "latency_ms": output.get("latency_ms", 0),
        "model_used": output.get("model_used", ""),
        "error": output.get("error"),
        "created_at": str(log.created_at) if log.created_at else None,
    }


@router.get("/{dataset_id}/history")
async def query_history(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(QueryLog)
        .where(
            QueryLog.dataset_id == dataset_id,
            QueryLog.user_id == current_user.id,
        )
        .order_by(QueryLog.created_at.desc())
        .limit(50)
    )
    rows = result.scalars().all()
    return [
        {
            "query_id": r.id,
            "question": r.question,
            "intent": r.intent,
            "answer": r.answer_narrative,
            "chart_spec": _parse_json_field(r.chart_spec),
            "sql_executed": r.sql_executed,
            "latency_ms": r.latency_ms,
            "created_at": str(r.created_at) if r.created_at else None,
            "error": r.error,
        }
        for r in rows
    ]
