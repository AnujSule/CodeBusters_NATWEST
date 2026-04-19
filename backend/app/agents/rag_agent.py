"""RAG Agent node for PDF document retrieval.

Retrieves relevant document chunks from pgvector and augments
the pipeline state with context from PDF documents.
"""

import json
from typing import Any, Dict, List

from app.config import settings
from app.agents.prompts import RAG_RETRIEVAL_PROMPT
from app.agents.state import AgentState
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def retrieve_rag(state: AgentState) -> Dict[str, Any]:
    """Retrieve relevant document chunks from pgvector.

    Uses semantic search to find chunks most relevant to the user's question.

    Args:
        state: Current agent pipeline state.

    Returns:
        Dictionary with rag_chunks to merge into state.
    """
    logger.info("retrieving_rag_chunks", question=state["question"])

    try:
        # Import here to avoid circular imports
        from app.services.vector_store import search_similar_chunks

        chunks = await search_similar_chunks(
            query_text=state["question"],
            dataset_id=state["dataset_id"],
            top_k=5,
        )

        if not chunks:
            logger.info("no_rag_chunks_found")
            return {
                "rag_chunks": [],
            }

        logger.info("rag_chunks_retrieved", count=len(chunks))

        return {
            "rag_chunks": chunks,
        }

    except Exception as e:
        logger.error("rag_retrieval_error", error=str(e))
        return {
            "rag_chunks": [],
            "error": f"RAG retrieval failed: {str(e)}",
        }


async def augment_with_metrics(state: AgentState) -> Dict[str, Any]:
    """Augment the state with metric definitions relevant to the query.

    Looks up the metric dictionary for any metric terms referenced
    in the user's question or extracted entities.

    Args:
        state: Current agent pipeline state.

    Returns:
        Dictionary with metric_definitions to merge into state.
    """
    logger.info("augmenting_with_metrics", metrics=state.get("metrics", []))

    try:
        from app.services.metric_dictionary import lookup_metrics

        metrics = state.get("metrics", [])
        question = state["question"].lower()

        # Also search the question text for metric aliases
        resolved_metrics = await lookup_metrics(metrics, question)

        logger.info("metrics_resolved", count=len(resolved_metrics))

        return {
            "metric_definitions": resolved_metrics,
        }

    except Exception as e:
        logger.error("metric_augmentation_error", error=str(e))
        return {
            "metric_definitions": {},
        }
