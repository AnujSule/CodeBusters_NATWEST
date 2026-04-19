"""
Local filesystem storage — replaces MinIO/S3 for local development.
Files stored under backend/uploads/ directory.
"""
import os
import shutil
import logging
from app.config import settings

logger = logging.getLogger(__name__)

UPLOAD_DIR = settings.UPLOAD_DIR


def _ensure_dir(path: str):
    """Ensure directory exists for the given file path."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


async def upload_file(object_key: str, content: bytes) -> str:
    """Save file content to local filesystem."""
    full_path = os.path.join(UPLOAD_DIR, object_key)
    _ensure_dir(full_path)
    with open(full_path, "wb") as f:
        f.write(content)
    logger.info(f"Saved file: {full_path} ({len(content)} bytes)")
    return object_key


async def download_file(object_key: str, dest_path: str):
    """Copy file from local storage to destination path."""
    full_path = os.path.join(UPLOAD_DIR, object_key)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found in storage: {full_path}")
    _ensure_dir(dest_path)
    shutil.copy2(full_path, dest_path)
    logger.info(f"Downloaded: {full_path} -> {dest_path}")


async def delete_file(object_key: str):
    """Delete file from local storage."""
    full_path = os.path.join(UPLOAD_DIR, object_key)
    if os.path.exists(full_path):
        os.remove(full_path)
        logger.info(f"Deleted: {full_path}")
