"""Seed metric definitions

Revision ID: 002_seed_metrics
Revises: 001_initial
Create Date: 2024-01-01 00:01:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import json

# revision identifiers, used by Alembic.
revision: str = "002_seed_metrics"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

METRIC_DEFINITIONS = [
    {
        "name": "revenue",
        "display_name": "Total Revenue",
        "definition": "Gross revenue before any deductions. Sum of all income-generating transactions.",
        "calculation_notes": "SUM(revenue) or SUM(amount) depending on column naming.",
        "aliases": json.dumps(["sales", "income", "turnover", "gross revenue", "total sales"]),
    },
    {
        "name": "net_revenue",
        "display_name": "Net Revenue",
        "definition": "Revenue after deducting returns, allowances, and discounts.",
        "calculation_notes": "revenue - returns - discounts",
        "aliases": json.dumps(["net sales", "net income from operations"]),
    },
    {
        "name": "churn_rate",
        "display_name": "Customer Churn Rate",
        "definition": "Percentage of customers who stopped using the product in a given period. (lost_customers / total_customers_start) * 100",
        "calculation_notes": "(churned_customers / (new_customers + existing_customers)) * 100",
        "aliases": json.dumps(["churn", "attrition", "customer loss rate"]),
    },
    {
        "name": "active_users",
        "display_name": "Monthly Active Users",
        "definition": "Unique users who performed at least one action in the calendar month.",
        "calculation_notes": "COUNT(DISTINCT user_id) WHERE action_date WITHIN month",
        "aliases": json.dumps(["MAU", "active customers", "monthly users"]),
    },
    {
        "name": "nps",
        "display_name": "Net Promoter Score",
        "definition": "Customer loyalty metric. % Promoters (9-10) minus % Detractors (0-6). Range: -100 to +100.",
        "calculation_notes": "(COUNT(score >= 9) / total * 100) - (COUNT(score <= 6) / total * 100)",
        "aliases": json.dumps(["net promoter", "customer satisfaction score", "NPS score"]),
    },
    {
        "name": "cost_to_income",
        "display_name": "Cost-to-Income Ratio",
        "definition": "Operating costs divided by operating income, expressed as a percentage. Lower is better.",
        "calculation_notes": "(operating_costs / operating_income) * 100",
        "aliases": json.dumps(["CIR", "efficiency ratio", "cost ratio"]),
    },
]


def upgrade() -> None:
    """Seed metric definitions into the database."""
    metric_table = sa.table(
        "metric_definitions",
        sa.column("name", sa.String),
        sa.column("display_name", sa.String),
        sa.column("definition", sa.Text),
        sa.column("calculation_notes", sa.Text),
        sa.column("aliases", JSONB),
    )

    for metric in METRIC_DEFINITIONS:
        op.execute(
            metric_table.insert().values(
                name=metric["name"],
                display_name=metric["display_name"],
                definition=metric["definition"],
                calculation_notes=metric["calculation_notes"],
                aliases=sa.text(f"'{metric['aliases']}'::jsonb"),
            )
        )


def downgrade() -> None:
    """Remove seeded metric definitions."""
    op.execute("DELETE FROM metric_definitions WHERE name IN ('revenue', 'net_revenue', 'churn_rate', 'active_users', 'nps', 'cost_to_income')")
