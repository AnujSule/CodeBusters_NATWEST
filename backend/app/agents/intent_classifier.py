"""Intent Classifier Agent node.

Classifies the user's question into one of four intents:
compare, decompose, summarise, or explain. Also extracts entities,
time ranges, and metric references.

Uses Groq (OpenAI-compatible API) with LLaMA 3.3 70B.
"""

import json
from typing import Any, Dict

from openai import OpenAI

from app.config import settings
from app.agents.prompts import INTENT_CLASSIFIER_PROMPT
from app.agents.state import AgentState
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _get_groq_client() -> OpenAI:
    """Create a Groq-compatible OpenAI client."""
    return OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.GROQ_BASE_URL,
    )


async def classify_intent(state: AgentState) -> Dict[str, Any]:
    """Classify the user's question intent and extract entities.

    Args:
        state: Current agent pipeline state.

    Returns:
        Dictionary with intent classification results to merge into state.
    """
    logger.info("classifying_intent", question=state["question"])

    try:
        client = _get_groq_client()

        # Build metric definitions context
        metric_defs = state.get("metric_definitions") or {}
        metric_context = json.dumps(metric_defs, indent=2) if metric_defs else "No metric definitions available."

        prompt = INTENT_CLASSIFIER_PROMPT.format(
            schema_info=json.dumps(state["schema_info"], indent=2),
            metric_definitions=metric_context,
            question=state["question"],
        )

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        response_text = response.choices[0].message.content.strip()

        # Parse JSON response — handle potential markdown code fences
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        result = json.loads(response_text)

        tokens_used = (response.usage.prompt_tokens or 0) + (response.usage.completion_tokens or 0)

        logger.info(
            "intent_classified",
            intent=result.get("intent", "unknown"),
            confidence=result.get("confidence", 0.0),
            tokens=tokens_used,
        )

        return {
            "intent": result.get("intent", "unknown"),
            "intent_confidence": result.get("confidence", 0.0),
            "entities": result.get("entities", []),
            "time_range": result.get("time_range", {}),
            "metrics": result.get("metrics", []),
            "tokens_used": state.get("tokens_used", 0) + tokens_used,
        }

    except json.JSONDecodeError as e:
        logger.error("intent_parse_error", error=str(e))
        return {
            "intent": "explain",
            "intent_confidence": 0.5,
            "entities": [],
            "time_range": {},
            "metrics": [],
            "error": f"Failed to parse intent classification: {str(e)}",
        }
    except Exception as e:
        logger.error("intent_classification_error", error=str(e))
        return {
            "intent": "explain",
            "intent_confidence": 0.0,
            "entities": [],
            "time_range": {},
            "metrics": [],
            "error": f"Intent classification failed: {str(e)}",
        }
