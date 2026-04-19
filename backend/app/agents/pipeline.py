"""
DataDialogue AI Pipeline
Plain async functions — no LangGraph, no state machine.
classify_intent → generate_sql → execute_sql → synthesise → return
"""
import os
import json
import time
import logging
import tempfile
import duckdb
from typing import Optional
from app.config import settings
from app.services.storage import download_file

logger = logging.getLogger(__name__)


def _get_llm():
    """Return the configured LLM. Prefers Groq, falls back to Anthropic."""
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY.startswith("gsk_"):
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0,
            max_tokens=2048,
        )
    elif settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.startswith("sk-ant"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0,
            max_tokens=2048,
        )
    else:
        raise RuntimeError(
            "No LLM API key configured. "
            "Add GROQ_API_KEY=gsk_... or ANTHROPIC_API_KEY=sk-ant-... to your .env"
        )


async def run_pipeline(
    question: str,
    dataset_id: str,
    file_path: str,
    file_type: str,
    schema_info: dict,
) -> dict:
    """Main entry point. Returns dict with answer, chart_spec, sql, etc."""
    t0 = time.time()

    try:
        llm = _get_llm()
    except RuntimeError as e:
        return _error_response(str(e), t0)

    try:
        intent, entities = await _classify_intent(llm, question, schema_info)
    except Exception as e:
        logger.warning(f"Intent classification failed: {e}")
        intent, entities = "explain", []

    sql_query = None
    sql_result = []
    sql_error = None

    if file_type == "csv":
        tmp_path = None
        try:
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".csv")
            os.close(tmp_fd)
            await download_file(file_path, tmp_path)
            sql_query, sql_result, sql_error = await _run_csv_query(
                llm, question, schema_info, tmp_path, intent, entities
            )
            # Retry once with a simpler approach if failed
            if sql_error and not sql_result:
                sql_query, sql_result, sql_error = await _run_csv_query(
                    llm, question, schema_info, tmp_path, intent, entities, simple=True
                )
        except Exception as e:
            sql_error = str(e)
            logger.error(f"CSV query error: {e}", exc_info=True)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
    else:
        # PDF — return text chunks as result
        sql_result = await _get_pdf_chunks(dataset_id)

    # Synthesise answer
    try:
        answer, key_metric, chart_spec = await _synthesise(
            llm, question, intent, sql_result, schema_info, sql_query
        )
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        answer = f"Data retrieved ({len(sql_result)} records) but answer generation failed: {str(e)[:150]}"
        key_metric = f"{len(sql_result)} records found"
        chart_spec = _auto_chart(sql_result, intent)

    latency = int((time.time() - t0) * 1000)
    
    model = "none"
    try:
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.startswith("gsk_"):
            model = settings.GROQ_MODEL
        elif settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.startswith("sk-ant"):
            model = settings.ANTHROPIC_MODEL
    except Exception:
        pass

    return {
        "intent": intent,
        "answer": answer,
        "key_metric": key_metric,
        "chart_spec": chart_spec,
        "sql_executed": sql_query,
        "sql_error": sql_error,
        "sources": _build_sources(file_path, schema_info, sql_query, sql_result),
        "tokens_used": 0,
        "latency_ms": latency,
        "model_used": model,
        "error": sql_error if not sql_result else None,
    }


async def _classify_intent(llm, question: str, schema_info: dict) -> tuple:
    from langchain_core.messages import HumanMessage
    cols = [c["name"] for c in schema_info.get("columns", [])] if schema_info else []
    prompt = f"""Classify this data question into exactly one intent.

Question: "{question}"
Columns available: {cols}

Return ONLY this JSON (no other text, no markdown):
{{"intent": "compare", "entities": ["term1", "term2"]}}

Intent must be one of:
- compare (comparing two+ things: time periods, regions, products)
- decompose (breaking a total into parts/components)
- summarise (overview, trends, summary)
- explain (why something happened, root cause)"""

    resp = await llm.ainvoke([HumanMessage(content=prompt)])
    text = resp.content.strip()
    if "```" in text:
        text = text.split("```")[1].replace("json", "").strip()
    if "{" in text:
        text = text[text.index("{"):text.rindex("}")+1]
    try:
        parsed = json.loads(text)
        return parsed.get("intent", "explain"), parsed.get("entities", [])
    except Exception:
        return "explain", []


async def _run_csv_query(
    llm, question: str, schema_info: dict, csv_path: str,
    intent: str, entities: list, simple: bool = False
) -> tuple:
    """Generate SQL from question, execute against CSV via DuckDB."""
    from langchain_core.messages import HumanMessage

    # Normalize path for DuckDB (forward slashes)
    csv_path_normalized = csv_path.replace("\\", "/")

    cols_info = "\n".join([
        f"  {c['name']} ({c['type']})"
        for c in schema_info.get("columns", [])
    ]) if schema_info.get("columns") else "  (unknown columns)"

    sample = json.dumps(schema_info.get("sample_rows", [])[:2], default=str)

    simple_note = """
KEEP IT SIMPLE: Only use basic SELECT, WHERE, GROUP BY, ORDER BY, LIMIT.
No subqueries. No CTEs. No window functions.""" if simple else ""

    prompt = f"""Generate a DuckDB SQL query to answer this question.

QUESTION: "{question}"
INTENT: {intent}
KEY TERMS: {entities}

TABLE REFERENCE: read_csv_auto('{csv_path_normalized}')
COLUMNS:
{cols_info}

SAMPLE DATA: {sample}
{simple_note}

STRICT RULES:
1. Return ONLY the SQL query. No explanation. No markdown. No backticks.
2. Table reference must be exactly: read_csv_auto('{csv_path_normalized}')
3. Use LIMIT 50 unless user asks for all data
4. If a column name has spaces, wrap in double quotes: "column name"
5. Use try_cast() for any type conversion
6. For percentages: ROUND(((new - old) / NULLIF(old,0)) * 100, 2)
7. Only SELECT statements allowed"""

    resp = await llm.ainvoke([HumanMessage(content=prompt)])
    sql = resp.content.strip()

    # Clean markdown
    for marker in ["```sql", "```SQL", "```", "SQL:", "sql:"]:
        sql = sql.replace(marker, "")
    sql = sql.strip()

    # Safety check
    for forbidden in ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"]:
        if forbidden in sql.upper():
            return None, [], f"Unsafe SQL blocked: contains {forbidden}"

    # Execute
    conn = duckdb.connect(":memory:")
    try:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        col_names = [d[0] for d in cursor.description] if cursor.description else []
        result = [_serialize_row(dict(zip(col_names, row))) for row in rows]
        return sql, result, None
    except Exception as e:
        logger.warning(f"SQL exec failed: {e}\nSQL: {sql}")
        return sql, [], str(e)
    finally:
        conn.close()


async def _get_pdf_chunks(dataset_id: str) -> list:
    """Get stored PDF text chunks — not implemented for SQLite local mode."""
    # PDF chunk storage was PostgreSQL-specific; for local mode, return empty
    logger.info("PDF chunk retrieval not available in local mode")
    return []


async def _synthesise(
    llm, question: str, intent: str,
    data: list, schema_info: dict, sql: Optional[str]
) -> tuple:
    """Generate plain-English answer, key metric, and chart spec."""
    from langchain_core.messages import HumanMessage

    if not data:
        return (
            "No data was returned for your question. "
            "Try rephrasing or check that the dataset has loaded correctly.",
            "No data found",
            None
        )

    preview = json.dumps(data[:15], default=str)
    row_count = len(data)

    prompt = f"""You are a financial analyst at NatWest explaining data insights to business users.

QUESTION: "{question}"
INTENT: {intent}
DATA ({row_count} rows, first 15 shown):
{preview}

Write your response in EXACTLY this format with ||| as separator:

ONE_LINE_FINDING|||NARRATIVE|||CHART_JSON

Rules:
- ONE_LINE_FINDING: Single sentence, max 15 words, most important number/finding
- NARRATIVE: 2-3 sentences, plain English, specific numbers from data, no jargon
- CHART_JSON: Valid JSON for a chart OR the word null

Chart JSON format (if data suits a chart):
{{"type":"bar","title":"Revenue by Region","x_key":"region","y_key":"revenue","data":[...first 12 rows...]}}

Chart types: bar (categories), line (time series), pie (parts of whole, max 6 slices), area (trend over time)
Use EXACT column names from the data for x_key and y_key.
If data has only 1 row or no numeric columns, use null."""

    resp = await llm.ainvoke([HumanMessage(content=prompt)])
    text = resp.content.strip()

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
        key_metric = f"Found {row_count} records"
        narrative = text[:400]
        chart_raw = "null"

    chart_spec = None
    if chart_raw and chart_raw.lower() != "null":
        try:
            if "```" in chart_raw:
                chart_raw = chart_raw.split("```")[1].replace("json","").strip()
            if "{" in chart_raw:
                chart_raw = chart_raw[chart_raw.index("{"):chart_raw.rindex("}")+1]
            parsed = json.loads(chart_raw)
            if not parsed.get("data"):
                parsed["data"] = data[:12]
            chart_spec = parsed
        except Exception as e:
            logger.debug(f"Chart parse failed: {e}")
            chart_spec = _auto_chart(data, intent)

    if not chart_spec:
        chart_spec = _auto_chart(data, intent)

    return narrative, key_metric, chart_spec


def _auto_chart(data: list, intent: str) -> Optional[dict]:
    """Automatically pick best chart type from data shape."""
    if not data or len(data) < 2:
        return None
    cols = list(data[0].keys())
    if len(cols) < 2:
        return None

    text_cols = [c for c in cols if isinstance(data[0].get(c), str)]
    num_cols = [c for c in cols if isinstance(data[0].get(c), (int, float))]

    if not num_cols:
        # Try to find any column that looks numeric
        for c in cols:
            try:
                float(str(data[0].get(c, "")))
                num_cols.append(c)
                break
            except Exception:
                pass

    if not num_cols:
        return None

    x_key = text_cols[0] if text_cols else cols[0]
    y_key = num_cols[0]

    chart_type = "bar"
    if intent == "summarise":
        chart_type = "area"
    elif intent == "decompose" and len(data) <= 6:
        chart_type = "pie"

    return {
        "type": chart_type,
        "title": f"{y_key} by {x_key}",
        "x_key": x_key,
        "y_key": y_key,
        "data": _serialize_rows(data[:12]),
    }


def _build_sources(file_path: str, schema_info: dict, sql: Optional[str], result: list) -> list:
    fname = file_path.split("/")[-1] if file_path else "unknown"
    cols_used = []
    if sql and schema_info.get("columns"):
        cols_used = [c["name"] for c in schema_info["columns"] if c["name"].lower() in sql.lower()]
    return [{
        "file": fname,
        "columns_used": cols_used,
        "rows_returned": len(result),
        "sql": sql,
    }]


def _error_response(msg: str, t0: float) -> dict:
    return {
        "intent": "unknown",
        "answer": f"Configuration error: {msg}",
        "key_metric": "Error",
        "chart_spec": None,
        "sql_executed": None,
        "sql_error": msg,
        "sources": [],
        "tokens_used": 0,
        "latency_ms": int((time.time() - t0) * 1000),
        "model_used": "none",
        "error": msg,
    }


def _serialize_row(row: dict) -> dict:
    import decimal, datetime
    out = {}
    for k, v in row.items():
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


def _serialize_rows(rows: list) -> list:
    return [_serialize_row(r) for r in rows]
