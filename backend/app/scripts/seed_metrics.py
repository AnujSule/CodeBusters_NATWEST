"""Seed metric definitions script.

Run with: python -m app.scripts.seed_metrics
"""

import asyncio

from sqlalchemy import select
from app.database import async_session_factory
from app.models.metric_definition import MetricDefinition
from app.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)

METRIC_DEFINITIONS = [
    {
        "name": "revenue",
        "display_name": "Total Revenue",
        "definition": "Gross revenue before any deductions. Sum of all income-generating transactions.",
        "calculation_notes": "SUM(revenue) or SUM(amount) depending on column naming.",
        "aliases": ["sales", "income", "turnover", "gross revenue", "total sales"],
    },
    {
        "name": "net_revenue",
        "display_name": "Net Revenue",
        "definition": "Revenue after deducting returns, allowances, and discounts.",
        "calculation_notes": "revenue - returns - discounts",
        "aliases": ["net sales", "net income from operations"],
    },
    {
        "name": "churn_rate",
        "display_name": "Customer Churn Rate",
        "definition": "Percentage of customers who stopped using the product in a given period. (lost_customers / total_customers_start) * 100",
        "calculation_notes": "(churned_customers / (new_customers + existing_customers)) * 100",
        "aliases": ["churn", "attrition", "customer loss rate"],
    },
    {
        "name": "active_users",
        "display_name": "Monthly Active Users",
        "definition": "Unique users who performed at least one action in the calendar month.",
        "calculation_notes": "COUNT(DISTINCT user_id) WHERE action_date WITHIN month",
        "aliases": ["MAU", "active customers", "monthly users"],
    },
    {
        "name": "nps",
        "display_name": "Net Promoter Score",
        "definition": "Customer loyalty metric. % Promoters (9-10) minus % Detractors (0-6). Range: -100 to +100.",
        "calculation_notes": "(COUNT(score >= 9) / total * 100) - (COUNT(score <= 6) / total * 100)",
        "aliases": ["net promoter", "customer satisfaction score", "NPS score"],
    },
    {
        "name": "cost_to_income",
        "display_name": "Cost-to-Income Ratio",
        "definition": "Operating costs divided by operating income, expressed as a percentage. Lower is better.",
        "calculation_notes": "(operating_costs / operating_income) * 100",
        "aliases": ["CIR", "efficiency ratio", "cost ratio"],
    },
]


async def seed_metrics() -> None:
    """Seed metric definitions into the database if not already present."""
    setup_logging()

    async with async_session_factory() as session:
        for metric_data in METRIC_DEFINITIONS:
            # Check if already exists
            result = await session.execute(
                select(MetricDefinition).where(MetricDefinition.name == metric_data["name"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.info("metric_exists", name=metric_data["name"])
                continue

            metric = MetricDefinition(**metric_data)
            session.add(metric)
            logger.info("metric_seeded", name=metric_data["name"])

        await session.commit()

    logger.info("metric_seeding_complete", count=len(METRIC_DEFINITIONS))


if __name__ == "__main__":
    asyncio.run(seed_metrics())
