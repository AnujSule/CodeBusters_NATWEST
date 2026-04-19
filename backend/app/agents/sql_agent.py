"""SQL Agent node.

Generates SQL queries from natural language and executes them against
DuckDB in-memory database loaded with the user's CSV data.

Uses Groq (OpenAI-compatible API) with LLaMA 3.3 70B.
"""

import json
import re
from typing import Any, Dict

import duckdb
from openai import OpenAI

from app.config import settings
from app.agents.prompts import SQL_AGENT_PROMPT
from app.agents.state import AgentState
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _get_groq_client() -> OpenAI:
    """Create a Groq-compatible OpenAI client."""
    return OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.GROQ_BASE_URL,
    )


async def generate_sql(state: AgentState) -> Dict[str, Any]:
    """Generate a SQL query from the user's question using the LLM.

    Args:
        state: Current agent pipeline state with schema info and intent.

    Returns:
        Dictionary with sql_query to merge into state.
    """
    logger.info("generating_sql", question=state["question"], intent=state.get("intent"))

    try:
        client = _get_groq_client()

        metric_defs = state.get("metric_definitions") or {}
        metric_context = json.dumps(metric_defs, indent=2) if metric_defs else "None available."

        prompt = SQL_AGENT_PROMPT.format(
            schema_info=json.dumps(state["schema_info"], indent=2),
            table_name=state["duckdb_table_name"],
            metric_definitions=metric_context,
            question=state["question"],
            intent=state.get("intent", "unknown"),
            entities=json.dumps(state.get("entities", [])),
            time_range=json.dumps(state.get("time_range", {})),
        )

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        sql_query = response.choices[0].message.content.strip()

        # Clean up SQL - remove markdown fences if present
        if sql_query.startswith("```"):
            sql_query = re.sub(r"```(?:sql)?\n?", "", sql_query).strip()
            sql_query = sql_query.rstrip("```").strip()

        tokens_used = (response.usage.prompt_tokens or 0) + (response.usage.completion_tokens or 0)

        logger.info("sql_generated", sql=sql_query[:200], tokens=tokens_used)

        return {
            "sql_query": sql_query,
            "tokens_used": state.get("tokens_used", 0) + tokens_used,
        }

    except Exception as e:
        logger.error("sql_generation_error", error=str(e))
        return {
            "sql_query": None,
            "sql_error": f"Failed to generate SQL: {str(e)}",
            "error": f"SQL generation failed: {str(e)}",
        }


async def execute_sql(state: AgentState) -> Dict[str, Any]:
    """Execute the generated SQL query against DuckDB with the CSV data.

    The CSV file is loaded into a DuckDB in-memory connection as a virtual table.
    This is sandboxed — no access to the application database.

    Args:
        state: Current agent pipeline state with sql_query.

    Returns:
        Dictionary with sql_result to merge into state.
    """
    sql_query = state.get("sql_query") or state.get("corrected_sql")

    if not sql_query:
        return {
            "sql_result": None,
            "sql_error": "No SQL query to execute",
        }

    logger.info("executing_sql", sql=sql_query[:200])

    try:
        # Create a sandboxed in-memory DuckDB connection
        conn = duckdb.connect(":memory:")

        try:
            # Register the CSV file as a virtual table
            csv_path = state.get("schema_info", {}).get("file_path", "")
            table_name = state["duckdb_table_name"]

            if csv_path:
                conn.execute(
                    f"CREATE VIEW \"{table_name}\" AS SELECT * FROM read_csv_auto('{csv_path}')"
                )

            # Execute the query
            result = conn.execute(sql_query)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()

            # Convert to list of dicts for easy JSON serialisation
            sql_result = [dict(zip(columns, row)) for row in rows]

            logger.info("sql_executed", row_count=len(sql_result), columns=columns)

            return {
                "sql_result": sql_result,
                "sql_error": None,
                "sources": [{
                    "file": state.get("schema_info", {}).get("file_name", "dataset"),
                    "columns": columns,
                    "rows_used": len(sql_result),
                    "total_rows": state.get("schema_info", {}).get("row_count", 0),
                    "confidence": 0.95,
                }],
            }

        finally:
            conn.close()

    except duckdb.Error as e:
        logger.error("sql_execution_error", error=str(e), sql=sql_query[:200])
        return {
            "sql_result": None,
            "sql_error": f"SQL execution error: {str(e)}",
        }
    except Exception as e:
        logger.error("sql_execution_unexpected_error", error=str(e))
        return {
            "sql_result": None,
            "sql_error": f"Unexpected error during SQL execution: {str(e)}",
        }
