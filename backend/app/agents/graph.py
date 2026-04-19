# backend/app/agents/graph.py
import os
import json
import time
import logging
import duckdb
import tempfile
import boto3
from botocore.client import Config
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

# ── LLM initialisation ──────────────────────────────────────────────────────
def get_llm():
    groq_key = os.getenv("GROQ_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if groq_key and groq_key.startswith("gsk_"):
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            api_key=groq_key,
            temperature=0,
            max_tokens=2048,
        )
    elif anthropic_key:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            api_key=anthropic_key,
            temperature=0,
            max_tokens=2048,
        )
    else:
        raise ValueError(
            "No LLM configured. Set GROQ_API_KEY (starts with gsk_) "
            "or ANTHROPIC_API_KEY in your .env file."
        )


# ── MinIO helper ────────────────────────────────────────────────────────────
def download_csv_from_minio(file_path: str) -> str:
    """Download CSV from MinIO to a temp file. Returns temp file path."""
    use_ssl = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
    proto = "https" if use_ssl else "http"
    endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")

    client = boto3.client(
        "s3",
        endpoint_url=f"{proto}://{endpoint}",
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", ""),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", ""),
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )
    bucket = os.getenv("MINIO_BUCKET_NAME", "datadialogue-files")
    tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    tmp.close()
    client.download_file(bucket, file_path, tmp.name)
    return tmp.name


# ── Main agent function ──────────────────────────────────────────────────────
async def run_query_pipeline(
    question: str,
    dataset_id: str,
    file_path: str,
    file_type: str,
    schema_info: dict,
    user_id: str,
) -> dict:
    """
    Full pipeline:
    1. Classify intent
    2. Generate SQL (CSV) or RAG (PDF)
    3. Execute SQL via DuckDB
    4. Verify result
    5. Synthesise narrative + chart_spec
    Returns a dict with all fields needed for QueryResponse.
    """
    start_time = time.time()
    llm = get_llm()
    tokens_used = 0

    try:
        # ── Step 1: Intent classification ────────────────────────────────
        intent, entities = await _classify_intent(llm, question, schema_info)

        # ── Step 2 & 3: SQL generation + execution (CSV) ─────────────────
        if file_type == "csv":
            tmp_path = None
            try:
                tmp_path = download_csv_from_minio(file_path)
                sql_query, sql_result, sql_error = await _run_sql_agent(
                    llm, question, schema_info, tmp_path, intent, entities
                )
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        else:
            # PDF — RAG path
            sql_query = None
            sql_error = None
            sql_result = await _run_rag_agent(question, dataset_id)

        if sql_error and not sql_result:
            # Retry once with a simpler query
            if file_type == "csv":
                tmp_path = None
                try:
                    tmp_path = download_csv_from_minio(file_path)
                    sql_query, sql_result, sql_error = await _run_sql_agent(
                        llm, question, schema_info, tmp_path, intent, entities,
                        retry=True
                    )
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.unlink(tmp_path)

        # ── Step 4: Synthesise answer ─────────────────────────────────────
        narrative, key_metric, chart_spec = await _synthesise(
            llm, question, intent, sql_result, schema_info, sql_query
        )

        # ── Step 5: Build sources ─────────────────────────────────────────
        sources = _build_sources(file_path, schema_info, sql_query, sql_result)

        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "intent": intent,
            "answer_narrative": narrative,
            "key_metric": key_metric,
            "chart_spec": chart_spec,
            "sql_executed": sql_query,
            "sql_error": sql_error,
            "sources": sources,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "model_used": os.getenv("GROQ_MODEL", os.getenv("ANTHROPIC_MODEL", "unknown")),
            "error": None,
        }

    except Exception as exc:
        logger.error(f"Pipeline error for dataset {dataset_id}: {exc}", exc_info=True)
        return {
            "intent": "unknown",
            "answer_narrative": f"I encountered an error processing your question: {str(exc)[:200]}. Please try rephrasing.",
            "key_metric": "Error",
            "chart_spec": None,
            "sql_executed": None,
            "sql_error": str(exc)[:500],
            "sources": [],
            "tokens_used": 0,
            "latency_ms": int((time.time() - start_time) * 1000),
            "model_used": "unknown",
            "error": str(exc)[:500],
        }


# ── Intent classifier ────────────────────────────────────────────────────────
async def _classify_intent(llm, question: str, schema_info: dict) -> tuple:
    columns = [c["name"] for c in schema_info.get("columns", [])]
    prompt = f"""You classify data analysis questions into one of four intents.

Question: "{question}"
Dataset columns: {columns}

Return ONLY valid JSON, no other text:
{{"intent": "compare|decompose|summarise|explain", "entities": ["list", "of", "key", "terms"]}}

Rules:
- compare: comparing two or more things (time, region, product, segment)
- decompose: breaking down totals into components
- summarise: overview or summary of metrics
- explain: understanding why something happened"""

    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        text = response.content.strip()
        # Extract JSON from response
        if "{" in text:
            text = text[text.index("{"):text.rindex("}")+1]
        result = json.loads(text)
        return result.get("intent", "explain"), result.get("entities", [])
    except Exception as e:
        logger.warning(f"Intent classification failed: {e}. Defaulting to explain.")
        return "explain", []


# ── SQL agent ────────────────────────────────────────────────────────────────
async def _run_sql_agent(
    llm, question: str, schema_info: dict, tmp_path: str,
    intent: str, entities: list, retry: bool = False
) -> tuple:
    """Generate SQL, execute it via DuckDB, return (sql, results, error)."""

    columns = schema_info.get("columns", [])
    col_desc = "\n".join([f"  - {c['name']} ({c['type']})" for c in columns])
    sample = schema_info.get("sample_rows", [])
    sample_str = json.dumps(sample[:2], default=str) if sample else "N/A"

    retry_note = "IMPORTANT: Keep the query very simple. Only SELECT, GROUP BY, and aggregate functions." if retry else ""

    prompt = f"""You are a DuckDB SQL expert. Generate a SQL query to answer the user's question.

Question: "{question}"
Intent: {intent}
Entities mentioned: {entities}

Table: read_csv_auto('{tmp_path}')
Columns:
{col_desc}

Sample data: {sample_str}

{retry_note}

Rules:
1. Return ONLY the SQL query. No explanation. No markdown. No backticks.
2. Use: SELECT * FROM read_csv_auto('{tmp_path}') as the table reference
3. Always LIMIT to 100 rows maximum
4. Column names with spaces must be quoted with double quotes
5. For percentages: ROUND(((a - b) / b) * 100, 2)
6. Use try_cast() for type conversions to avoid errors
7. Never use INSERT, UPDATE, DELETE, DROP, CREATE"""

    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        sql = response.content.strip()

        # Clean up any markdown the LLM added despite instructions
        sql = sql.replace("```sql", "").replace("```", "").strip()
        if sql.upper().startswith("SQL:"):
            sql = sql[4:].strip()

        # Execute
        conn = duckdb.connect(database=":memory:")
        try:
            result = conn.execute(sql).fetchall()
            col_names = [desc[0] for desc in conn.description]
            rows = [dict(zip(col_names, row)) for row in result]
            rows = _safe_json_rows(rows)
            return sql, rows, None
        except Exception as exec_err:
            logger.warning(f"SQL execution failed: {exec_err}\nSQL: {sql}")
            return sql, [], str(exec_err)
        finally:
            conn.close()

    except Exception as e:
        logger.error(f"SQL agent error: {e}")
        return None, [], str(e)


# ── RAG agent (PDF) ───────────────────────────────────────────────────────────
async def _run_rag_agent(question: str, dataset_id: str) -> list:
    """Retrieve relevant chunks from pgvector for PDF datasets."""
    try:
        import asyncpg
        db_url = os.getenv("DATABASE_URL", "").replace("postgresql+asyncpg://", "")
        conn = await asyncpg.connect(f"postgresql://{db_url}")
        try:
            rows = await conn.fetch(
                """
                SELECT content, chunk_index
                FROM document_chunks
                WHERE dataset_id = $1
                ORDER BY chunk_index
                LIMIT 10
                """,
                dataset_id
            )
            return [{"content": r["content"], "chunk": r["chunk_index"]} for r in rows]
        finally:
            await conn.close()
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
        return []


# ── Synthesiser ───────────────────────────────────────────────────────────────
async def _synthesise(
    llm, question: str, intent: str,
    sql_result: list, schema_info: dict, sql_query: Optional[str]
) -> tuple:
    """Generate narrative, key_metric, and chart_spec from SQL results."""

    if not sql_result:
        return (
            "I was unable to retrieve data to answer your question. "
            "Please check that your dataset has loaded correctly and try rephrasing.",
            "No data found",
            None
        )

    # Limit result for prompt
    result_preview = json.dumps(sql_result[:20], default=str)
    columns = list(sql_result[0].keys()) if sql_result else []

    prompt = f"""You are a financial data analyst writing for non-technical business users at NatWest.

Question asked: "{question}"
Intent: {intent}
Data result ({len(sql_result)} rows, showing first 20):
{result_preview}

Write a response with these EXACT sections, separated by |||:

SECTION 1 - KEY METRIC (one line, max 15 words, the single most important finding):
Example: "Revenue in South region fell 22% in February"

SECTION 2 - NARRATIVE (2-4 sentences, plain English, specific numbers, no jargon):
Lead with the most important finding. Support with 2-3 data points. End with one implication.

SECTION 3 - CHART SPEC (valid JSON for a chart, or null if data doesn't suit a chart):
Format: {{"type":"bar|line|pie|area","title":"...","x_key":"column_name","y_key":"column_name","data":[first 15 rows]}}
Use column names exactly as they appear in the data.

Respond in exactly this format:
KEY_METRIC|||NARRATIVE|||CHART_SPEC"""

    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        text = response.content.strip()

        parts = text.split("|||")
        if len(parts) >= 3:
            key_metric = parts[0].strip()
            narrative = parts[1].strip()
            chart_raw = parts[2].strip()
        elif len(parts) == 2:
            key_metric = parts[0].strip()
            narrative = parts[1].strip()
            chart_raw = "null"
        else:
            key_metric = "Analysis complete"
            narrative = text
            chart_raw = "null"

        # Parse chart spec
        chart_spec = None
        if chart_raw and chart_raw.lower() != "null":
            try:
                if "{" in chart_raw:
                    chart_raw = chart_raw[chart_raw.index("{"):chart_raw.rindex("}")+1]
                chart_spec = json.loads(chart_raw)
                # Inject actual data if missing
                if "data" not in chart_spec or not chart_spec["data"]:
                    chart_spec["data"] = _safe_json_rows(sql_result[:15])
            except Exception as e:
                logger.warning(f"Chart spec parse failed: {e}")
                chart_spec = _auto_chart(sql_result, intent)

        # Auto-generate chart if LLM didn't provide one
        if not chart_spec and sql_result:
            chart_spec = _auto_chart(sql_result, intent)

        return narrative, key_metric, chart_spec

    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        narrative = f"Analysis of {len(sql_result)} records: {_simple_summary(sql_result)}"
        return narrative, "Analysis complete", _auto_chart(sql_result, intent)


def _auto_chart(sql_result: list, intent: str) -> Optional[dict]:
    """Auto-generate a best-guess chart spec from SQL result columns."""
    if not sql_result:
        return None
    cols = list(sql_result[0].keys())
    if len(cols) < 2:
        return None

    # Find a text column (category) and a numeric column (value)
    text_cols = [c for c in cols if isinstance(sql_result[0].get(c), str)]
    num_cols = [c for c in cols if isinstance(sql_result[0].get(c), (int, float))]

    if not text_cols or not num_cols:
        # Try all columns
        x_key = cols[0]
        y_key = cols[1]
    else:
        x_key = text_cols[0]
        y_key = num_cols[0]

    chart_type = "bar"
    if intent == "summarise":
        chart_type = "area"
    elif intent == "decompose" and len(sql_result) <= 6:
        chart_type = "pie"

    return {
        "type": chart_type,
        "title": f"{y_key} by {x_key}",
        "x_key": x_key,
        "y_key": y_key,
        "data": _safe_json_rows(sql_result[:15]),
    }


def _build_sources(file_path: str, schema_info: dict, sql_query: Optional[str], result: list) -> list:
    filename = file_path.split("/")[-1] if file_path else "unknown"
    cols_used = []
    if sql_query:
        cols = [c["name"] for c in schema_info.get("columns", [])]
        cols_used = [c for c in cols if c.lower() in sql_query.lower()]

    return [{
        "file": filename,
        "columns_used": cols_used,
        "rows_matched": len(result),
        "total_rows": schema_info.get("row_count", 0),
        "sql": sql_query,
    }]


def _safe_json_rows(rows: list) -> list:
    """Make rows JSON-serializable."""
    import decimal, datetime
    clean = []
    for row in rows:
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, decimal.Decimal):
                clean_row[k] = float(v)
            elif isinstance(v, (datetime.date, datetime.datetime)):
                clean_row[k] = str(v)
            elif v is None:
                clean_row[k] = None
            else:
                try:
                    json.dumps(v)
                    clean_row[k] = v
                except Exception:
                    clean_row[k] = str(v)
        clean.append(clean_row)
    return clean


def _simple_summary(result: list) -> str:
    if not result:
        return "No data."
    cols = list(result[0].keys())
    return f"{len(result)} rows across columns: {', '.join(cols[:5])}"
