"""Add error column to datasets

Revision ID: 003_dataset_error
Revises: 002_seed_metrics
Create Date: 2026-04-19 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_dataset_error"
down_revision: Union[str, None] = "002_seed_metrics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add error column to datasets if it doesn't exist
    # Using raw SQL for safety in case it somewhat exists in some envs
    op.execute("ALTER TABLE datasets ADD COLUMN IF NOT EXISTS error TEXT;")


def downgrade() -> None:
    op.execute("ALTER TABLE datasets DROP COLUMN IF EXISTS error;")
