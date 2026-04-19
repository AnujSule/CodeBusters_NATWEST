from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.query_log import QueryLog
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/")
async def get_audit_log(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(QueryLog)
        .where(QueryLog.user_id == current_user.id)
        .order_by(QueryLog.created_at.desc())
        .limit(200)
    )
    rows = result.scalars().all()
    return [
        {
            "query_id": r.id,
            "question": r.question,
            "intent": r.intent,
            "dataset_id": r.dataset_id,
            "sql_executed": r.sql_executed,
            "model_used": r.model_used,
            "tokens_used": r.tokens_used,
            "latency_ms": r.latency_ms,
            "error": r.error,
            "created_at": str(r.created_at) if r.created_at else None,
        }
        for r in rows
    ]
