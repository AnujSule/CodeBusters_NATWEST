import uuid
import os
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.database import get_db
from app.models.dataset import Dataset
from app.dependencies import get_current_user
from app.models.user import User
from app.services.storage import upload_file, delete_file

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED = {"csv", "pdf"}
MAX_BYTES = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024


@router.post("/upload", status_code=202)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fname = file.filename or "upload.csv"
    ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
    if ext not in ALLOWED:
        raise HTTPException(400, f"Only CSV and PDF files are allowed. Got: .{ext}")

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(400, "File too large. Maximum 50MB.")

    dataset_id = str(uuid.uuid4())
    object_key = f"datasets/{current_user.id}/{dataset_id}/{fname}"

    try:
        await upload_file(object_key, content)
    except Exception as e:
        raise HTTPException(500, f"Storage upload failed: {str(e)[:200]}")

    display_name = name or fname.rsplit(".", 1)[0].replace("_", " ").title()
    dataset = Dataset(
        id=dataset_id,
        user_id=current_user.id,
        name=display_name,
        file_type=ext,
        file_path=object_key,
        file_size_bytes=len(content),
        status="pending",
    )
    db.add(dataset)
    await db.commit()

    # Process synchronously (no Celery/Redis needed)
    try:
        from app.tasks.processing import process_dataset_sync
        process_dataset_sync(dataset_id)
        # Refresh to get updated status
        await db.refresh(dataset)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        dataset.status = "failed"
        dataset.error = f"Processing error: {str(e)[:200]}"
        await db.commit()

    return _serialize_dataset(dataset)


@router.get("/")
async def list_datasets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Dataset)
        .where(Dataset.user_id == current_user.id)
        .order_by(Dataset.created_at.desc())
    )
    rows = result.scalars().all()
    return [_serialize_dataset(r) for r in rows]


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.user_id == current_user.id
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(404, "Dataset not found")
    return _serialize_dataset(ds, include_schema=True)


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.user_id == current_user.id
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(404, "Dataset not found")
    try:
        await delete_file(ds.file_path)
    except Exception:
        pass
    await db.delete(ds)
    await db.commit()
    return {"deleted": True}


def _parse_json_field(value):
    """Parse a JSON field that may be stored as a string (SQLite) or dict (PostgreSQL)."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def _serialize_dataset(ds: Dataset, include_schema: bool = False) -> dict:
    d = {
        "id": ds.id,                          # Frontend expects 'id', not 'dataset_id'
        "dataset_id": ds.id,                  # Keep for backward compat
        "user_id": ds.user_id,
        "name": ds.name,
        "description": ds.description,
        "file_type": ds.file_type,
        "file_size_bytes": ds.file_size_bytes,
        "status": ds.status,
        "row_count": ds.row_count,
        "column_names": ds.column_names or [],
        "created_at": str(ds.created_at) if ds.created_at else None,
        "updated_at": str(ds.updated_at) if ds.updated_at else None,
        "error": ds.error,
    }
    if include_schema:
        d["schema_info"] = ds.schema_info or {}
    return d
