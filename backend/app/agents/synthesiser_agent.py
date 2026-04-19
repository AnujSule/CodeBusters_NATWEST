"""Synthesiser Agent node.

Builds the final plain-English narrative and chart specification
from the verified SQL results.

Uses Groq (OpenAI-compatible API) with LLaMA 3.3 70B.
"""

import json
from typing import Any, Dict

from openai import OpenAI

from app.config import settings
from app.agents.prompts import SYNTHESISER_AGENT_PROMPT
from app.agents.state import AgentState
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _get_groq_client() -> OpenAI:
    """Create a Groq-compatible OpenAI client."""
    return OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.GROQ_BASE_URL,
    )


async def synthesise_response(state: AgentState) -> Dict[str, Any]:
    """Synthesise a plain-English narrative and chart spec from the query results.

    This is the final agent in the pipeline. It produces:
    - A human-readable narrative answer
    - An optional chart specification for Recharts
    - A one-line key metric summary

    Args:
        state: Current agent pipeline state with sql_result and verification.

    Returns:
        Dictionary with narrative, chart_spec, and key_metric to merge into state.
    """
    logger.info("synthesising_response", intent=state.get("intent"))

    try:
        client = _get_groq_client()

        sql_result = state.get("sql_result") or []
        rag_chunks = state.get("rag_chunks") or []

        # Combine SQL results and RAG chunks for context
        result_data = sql_result[:20] if sql_result else []

        # If we have RAG chunks but no SQL result, include chunk content
        if rag_chunks and not sql_result:
            result_data = [{"document_excerpt": chunk.get("content", "")} for chunk in rag_chunks[:10]]

        prompt = SYNTHESISER_AGENT_PROMPT.format(
            question=state["question"],
            intent=state.get("intent", "explain"),
            sql_result=json.dumps(result_data, indent=2, default=str),
            schema_info=json.dumps(state["schema_info"], indent=2),
            verification_notes=state.get("verification_notes", "No verification performed."),
        )

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            max_tokens=settings.GROQ_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
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

        narrative = result.get("narrative", "Unable to generate a narrative for this query.")
        chart_spec = result.get("chart_spec")
        key_metric = result.get("key_metric", "")

        # Validate chart_spec structure if present
        if chart_spec:
            required_keys = {"type", "title", "x_key", "y_key", "data"}
            if not all(key in chart_spec for key in required_keys):
                logger.warning("invalid_chart_spec", missing_keys=required_keys - set(chart_spec.keys()))
                chart_spec = None

        logger.info(
            "synthesis_complete",
            narrative_length=len(narrative),
            has_chart=chart_spec is not None,
            tokens=tokens_used,
        )

        return {
            "answer_narrative": narrative,
            "chart_spec": chart_spec,
            "key_metric": key_metric,
            "tokens_used": state.get("tokens_used", 0) + tokens_used,
        }

    except json.JSONDecodeError as e:
        logger.error("synthesis_parse_error", error=str(e))
        return {
            "answer_narrative": "I analysed your data but encountered a formatting issue. Please try rephrasing your question.",
            "chart_spec": None,
            "key_metric": "Analysis completed with formatting issues.",
        }
    except Exception as e:
        logger.error("synthesis_error", error=str(e))
        return {
            "answer_narrative": f"An error occurred while generating the response: {str(e)}",
            "chart_spec": None,
            "key_metric": "Error during analysis.",
            "error": f"Synthesis failed: {str(e)}",
        }
