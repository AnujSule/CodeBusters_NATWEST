"""MetricDefinition SQLAlchemy model for the metric dictionary."""

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin


class MetricDefinition(Base, TimestampMixin):
    """Metric dictionary model for canonical metric definitions and aliases."""

    __tablename__ = "metric_definitions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    definition: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    calculation_notes: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )
    aliases: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation of MetricDefinition."""
        return f"<MetricDefinition(name={self.name}, display_name={self.display_name})>"
