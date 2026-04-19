"""
Dataset processing — synchronous, no Celery/Redis required.
Uses SQLite for local development.
"""
import os
import json
import logging
import tempfile
import traceback
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


def _get_db_url():
    """Get sync database URL."""
    url = os.getenv("DATABASE_URL", "sqlite:///./datadialogue.db")
    # Convert async URLs to sync
    url = url.replace("sqlite+aiosqlite:///", "sqlite:///")
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("postgresql+psycopg://", "postgresql://")
    return url


def _get_engine():
    url = _get_db_url()
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True, pool_size=3, max_overflow=5)


_engine = _get_engine()


def _get_conn():
    return _engine.connect()


def process_dataset_sync(dataset_id: str):
    """Process an uploaded dataset synchronously. Update status to ready or failed."""
    logger.info(f"[{dataset_id}] Processing started")

    with _get_conn() as conn:
        # Mark as processing
        conn.execute(
            text("UPDATE datasets SET status='processing' WHERE id=:id"),
            {"id": dataset_id}
        )
        conn.commit()

        # Fetch dataset row
        row = conn.execute(
            text("SELECT id, name, file_type, file_path FROM datasets WHERE id=:id"),
            {"id": dataset_id}
        ).fetchone()

        if not row:
            logger.error(f"Dataset {dataset_id} not found")
            return {"error": "not found"}

        file_type = row[2]  # file_type
        file_path = row[3]  # file_path

    # Get the actual file from local storage
    tmp_path = None
    try:
        from app.config import settings
        upload_dir = settings.UPLOAD_DIR
        source_path = os.path.join(upload_dir, file_path)

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"File not found: {source_path}")

        suffix = ".csv" if file_type == "csv" else ".pdf"
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        os.close(tmp_fd)

        # Copy file to temp location
        import shutil
        shutil.copy2(source_path, tmp_path)
        logger.info(f"[{dataset_id}] Copied to {tmp_path}")

        # Process file
        if file_type == "csv":
            schema_info, row_count, column_names = _process_csv(tmp_path)
        else:
            schema_info, row_count, column_names = _process_pdf(tmp_path, dataset_id)

        # Mark as ready
        with _get_conn() as conn:
            is_pg = _engine.dialect.name == "postgresql"
            col_sql = "CAST(:col_names AS JSONB)" if is_pg else ":col_names"
            schema_sql = "CAST(:schema AS JSONB)" if is_pg else ":schema"
            conn.execute(
                text(f"""
                    UPDATE datasets SET
                        status='ready',
                        row_count=:row_count,
                        column_names={col_sql},
                        schema_info={schema_sql},
                        error=NULL
                    WHERE id=:id
                """),
                {
                    "id": dataset_id,
                    "row_count": row_count,
                    "col_names": json.dumps(column_names),
                    "schema": json.dumps(schema_info),
                }
            )
            conn.commit()

        logger.info(f"[{dataset_id}] Ready. rows={row_count}")
        return {"status": "ready", "row_count": row_count}

    except Exception as exc:
        err = f"{type(exc).__name__}: {str(exc)}"
        tb = traceback.format_exc()[-800:]
        logger.error(f"[{dataset_id}] FAILED: {err}\n{tb}")

        try:
            with _get_conn() as conn:
                conn.execute(
                    text("UPDATE datasets SET status='failed', error=:err WHERE id=:id"),
                    {"id": dataset_id, "err": f"{err}\n{tb}"[:2000]}
                )
                conn.commit()
        except Exception as db_err:
            logger.error(f"Could not write failure to DB: {db_err}")

        return {"status": "failed", "error": err}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def _process_csv(tmp_path: str) -> tuple:
    """Parse CSV with DuckDB. Return (schema_info, row_count, column_names)."""
    import duckdb

    # Normalize path for DuckDB (use forward slashes)
    csv_path = tmp_path.replace("\\", "/")

    conn = duckdb.connect(":memory:")
    try:
        conn.execute(f"CREATE VIEW v AS SELECT * FROM read_csv_auto('{csv_path}', sample_size=2000)")

        # Schema
        cols = conn.execute("DESCRIBE v").fetchall()
        column_names = [c[0] for c in cols]
        columns = [{"name": c[0], "type": str(c[1])} for c in cols]

        # Row count
        row_count = conn.execute("SELECT COUNT(*) FROM v").fetchone()[0]

        # Sample rows
        sample_rows = conn.execute("SELECT * FROM v LIMIT 5").fetchall()
        sample = [_safe_dict(dict(zip(column_names, r))) for r in sample_rows]

        schema_info = {
            "table_name": "uploaded_csv",
            "columns": columns,
            "row_count": row_count,
            "sample_rows": sample,
        }
        return schema_info, row_count, column_names
    finally:
        conn.close()


def _process_pdf(tmp_path: str, dataset_id: str) -> tuple:
    """Extract text from PDF and store chunks."""
    import pdfplumber

    pages = []
    with pdfplumber.open(tmp_path) as pdf:
        for i, page in enumerate(pdf.pages):
            t = page.extract_text() or ""
            if t.strip():
                pages.append({"page": i+1, "text": t.strip()})

    if not pages:
        raise ValueError("PDF has no extractable text")

    full_text = "\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages)
    chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
    overlap = int(os.getenv("CHUNK_OVERLAP", "64"))

    chunks = []
    start = 0
    while start < len(full_text):
        chunks.append(full_text[start:start+chunk_size])
        start += chunk_size - overlap

    schema_info = {
        "file_type": "pdf",
        "page_count": len(pages),
        "chunk_count": len(chunks),
        "sample_text": full_text[:300],
    }
    return schema_info, len(chunks), ["page", "text", "chunk_index"]


def _safe_dict(d: dict) -> dict:
    import decimal, datetime
    out = {}
    for k, v in d.items():
        if isinstance(v, decimal.Decimal):
            out[k] = float(v)
        elif isinstance(v, (datetime.date, datetime.datetime)):
            out[k] = str(v)
        elif v is None:
            out[k] = None
        else:
            try:
                json.dumps(v)
                out[k] = v
            except Exception:
                out[k] = str(v)
    return out
