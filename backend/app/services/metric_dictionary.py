"""Metric dictionary service.

Loads and queries metric definitions from the database.
Maps user-facing metric terms and aliases to canonical metric definitions.
"""

from typing import Dict, Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.metric_definition import MetricDefinition
from app.utils.logging import get_logger

logger = get_logger(__name__)

# In-memory cache for metric definitions (loaded once)
_metrics_cache: Optional[List[Dict[str, Any]]] = None


async def load_all_metrics() -> List[Dict[str, Any]]:
    """Load all metric definitions from the database.

    Results are cached in memory for subsequent calls.

    Returns:
        List of metric definition dictionaries.
    """
    global _metrics_cache

    if _metrics_cache is not None:
        return _metrics_cache

    async with async_session_factory() as session:
        result = await session.execute(select(MetricDefinition))
        metrics = result.scalars().all()

        _metrics_cache = [
            {
                "name": m.name,
                "display_name": m.display_name,
                "definition": m.definition,
                "calculation_notes": m.calculation_notes,
                "aliases": m.aliases or [],
            }
            for m in metrics
        ]

    logger.info("metrics_loaded", count=len(_metrics_cache))
    return _metrics_cache


async def lookup_metrics(
    metric_names: List[str],
    question_text: str = "",
) -> Dict[str, Any]:
    """Look up metric definitions by name, aliases, or terms in the question.

    Args:
        metric_names: Explicit metric names to look up.
        question_text: The full question text to scan for metric aliases.

    Returns:
        Dictionary mapping metric names to their definitions.
    """
    all_metrics = await load_all_metrics()
    resolved = {}

    question_lower = question_text.lower()

    for metric in all_metrics:
        # Check if explicitly requested by name
        if metric["name"] in [m.lower() for m in metric_names]:
            resolved[metric["name"]] = metric
            continue

        # Check aliases against the question text
        for alias in metric.get("aliases", []):
            if alias.lower() in question_lower:
                resolved[metric["name"]] = metric
                break

        # Check if the metric name itself appears in the question
        if metric["name"].replace("_", " ") in question_lower:
            resolved[metric["name"]] = metric
        elif metric["display_name"].lower() in question_lower:
            resolved[metric["name"]] = metric

    logger.info("metrics_resolved", requested=len(metric_names), resolved=len(resolved))
    return resolved


async def get_all_metrics_context() -> str:
    """Get all metric definitions as a formatted string for LLM context.

    Returns:
        Formatted string of all metric definitions.
    """
    all_metrics = await load_all_metrics()

    if not all_metrics:
        return "No metric definitions available."

    lines = []
    for m in all_metrics:
        aliases = ", ".join(m.get("aliases", []))
        lines.append(
            f"- **{m['display_name']}** ({m['name']}): {m['definition']} "
            f"[Aliases: {aliases}]"
        )

    return "\n".join(lines)


def clear_cache() -> None:
    """Clear the metrics cache (useful for testing)."""
    global _metrics_cache
    _metrics_cache = None
