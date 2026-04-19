"""CSV processor service.

Downloads CSV from MinIO, loads it into a DuckDB in-memory connection
as a virtual table, and extracts schema information.
"""

import os
import tempfile
from typing import Tuple, Dict, Any, Optional
from contextlib import asynccontextmanager

import duckdb

from app.services.storage import download_file_to_path
from app.utils.logging import get_logger

logger = get_logger(__name__)


def sanitize_table_name(name: str) -> str:
    """Sanitize a file name into a valid DuckDB table name.

    Args:
        name: Original file name.

    Returns:
        Sanitized table name safe for SQL.
    """
    # Remove extension and special characters
    base = os.path.splitext(name)[0]
    sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in base)
    # Ensure it starts with a letter
    if sanitized and sanitized[0].isdigit():
        sanitized = "t_" + sanitized
    return sanitized.lower() or "dataset"


async def get_csv_schema(file_path: str, table_name: str) -> Dict[str, Any]:
    """Extract schema information from a CSV file using DuckDB.

    Args:
        file_path: Local path to the CSV file.
        table_name: Name for the virtual table.

    Returns:
        Dictionary with schema info including columns, types, sample rows, and row count.
    """
    conn = duckdb.connect(":memory:")

    try:
        # Create a view from the CSV file
        conn.execute(
            f'CREATE VIEW "{table_name}" AS SELECT * FROM read_csv_auto(\'{file_path}\')'
        )

        # Get column names and types
        describe_result = conn.execute(f'DESCRIBE "{table_name}"').fetchall()
        columns = []
        column_types = {}
        for row in describe_result:
            col_name = row[0]
            col_type = row[1]
            columns.append(col_name)
            column_types[col_name] = col_type

        # Get row count
        row_count = conn.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]

        # Get sample rows (first 5)
        sample_result = conn.execute(f'SELECT * FROM "{table_name}" LIMIT 5')
        sample_columns = [desc[0] for desc in sample_result.description]
        sample_rows = [dict(zip(sample_columns, row)) for row in sample_result.fetchall()]

        schema_info = {
            "columns": columns,
            "column_types": column_types,
            "row_count": row_count,
            "sample_rows": sample_rows,
            "table_name": table_name,
            "file_path": file_path,
        }

        logger.info(
            "csv_schema_extracted",
            table=table_name,
            columns=len(columns),
            rows=row_count,
        )

        return schema_info

    finally:
        conn.close()


async def process_csv(
    object_name: str,
    file_name: str,
) -> Tuple[str, str, Dict[str, Any]]:
    """Process a CSV file: download from MinIO, extract schema, prepare for querying.

    Args:
        object_name: MinIO object key for the CSV file.
        file_name: Original file name.

    Returns:
        Tuple of (temp_file_path, table_name, schema_info).
    """
    logger.info("processing_csv", object_name=object_name, file_name=file_name)

    # Create a temp file for the CSV
    temp_dir = tempfile.mkdtemp(prefix="datadialogue_")
    temp_path = os.path.join(temp_dir, file_name)

    # Download from MinIO
    await download_file_to_path(object_name, temp_path)

    # Generate table name
    table_name = sanitize_table_name(file_name)

    # Extract schema
    schema_info = await get_csv_schema(temp_path, table_name)
    schema_info["file_name"] = file_name
    schema_info["object_name"] = object_name

    logger.info(
        "csv_processed",
        table_name=table_name,
        columns=len(schema_info["columns"]),
        rows=schema_info["row_count"],
    )

    return temp_path, table_name, schema_info


@asynccontextmanager
async def get_duckdb_connection(file_path: str, table_name: str):
    """Context manager for a DuckDB connection with a CSV loaded as a virtual table.

    DuckDB connections are per-request (not shared) since DuckDB has
    connection-level state.

    Args:
        file_path: Path to the CSV file.
        table_name: Name for the virtual table.

    Yields:
        DuckDB connection with the CSV loaded.
    """
    conn = duckdb.connect(":memory:")

    try:
        conn.execute(
            f'CREATE VIEW "{table_name}" AS SELECT * FROM read_csv_auto(\'{file_path}\')'
        )
        yield conn
    finally:
        conn.close()
