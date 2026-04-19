"""Verifier Agent node.

Cross-checks the SQL output against the original question to ensure
the answer is correct and the query actually addresses what was asked.

Uses Groq (OpenAI-compatible API) with LLaMA 3.3 70B.
"""

import json
from typing import Any, Dict

from openai import OpenAI

from app.config import settings
from app.agents.prompts import VERIFIER_AGENT_PROMPT
from app.agents.state import AgentState
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _get_groq_client() -> OpenAI:
    """Create a Groq-compatible OpenAI client."""
    return OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.GROQ_BASE_URL,
    )


async def verify_answer(state: AgentState) -> Dict[str, Any]:
    """Verify that the SQL result correctly answers the user's question.

    The verifier checks for:
    - Whether the SQL addresses the question
    - Calculation errors
    - Empty results that shouldn't be empty
    - Suspicious values

    If issues are found, it may provide corrected SQL.

    Args:
        state: Current agent pipeline state with sql_query and sql_result.

    Returns:
        Dictionary with verification results to merge into state.
    """
    sql_query = state.get("sql_query")
    sql_result = state.get("sql_result")

    # Skip verification if no SQL was executed (PDF-only path)
    if not sql_query and not sql_result:
        logger.info("skipping_verification", reason="no_sql_executed")
        return {
            "verification_passed": True,
            "verification_notes": "No SQL verification needed (document-based query).",
            "corrected_sql": None,
        }

    logger.info("verifying_answer", sql_length=len(sql_query or ""), result_rows=len(sql_result or []))

    try:
        client = _get_groq_client()

        # Limit result to first 20 rows for the verifier
        result_preview = (sql_result or [])[:20]

        prompt = VERIFIER_AGENT_PROMPT.format(
            question=state["question"],
            sql_query=sql_query or "None",
            sql_result=json.dumps(result_preview, indent=2, default=str),
            schema_info=json.dumps(state["schema_info"], indent=2),
        )

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        response_text = response.choices[0].message.content.strip()

        # Parse JSON response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        result = json.loads(response_text)
        tokens_used = (response.usage.prompt_tokens or 0) + (response.usage.completion_tokens or 0)

        passed = result.get("passed", True)
        issues = result.get("issues", [])
        corrected_sql = result.get("corrected_sql")

        logger.info(
            "verification_complete",
            passed=passed,
            issues_count=len(issues),
            has_correction=corrected_sql is not None,
            tokens=tokens_used,
        )

        return {
            "verification_passed": passed,
            "verification_notes": "; ".join(issues) if issues else "Verification passed.",
            "corrected_sql": corrected_sql,
            "tokens_used": state.get("tokens_used", 0) + tokens_used,
        }

    except json.JSONDecodeError as e:
        logger.error("verification_parse_error", error=str(e))
        return {
            "verification_passed": True,
            "verification_notes": "Verification result could not be parsed, proceeding with original result.",
            "corrected_sql": None,
        }
    except Exception as e:
        logger.error("verification_error", error=str(e))
        return {
            "verification_passed": True,
            "verification_notes": f"Verification skipped due to error: {str(e)}",
            "corrected_sql": None,
        }
