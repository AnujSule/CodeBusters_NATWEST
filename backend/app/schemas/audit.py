"""Audit log Pydantic schemas for request/response validation."""

from uuid import UUID
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class AuditLogEntry(BaseModel):
    """Schema for a single audit log entry."""

    id: UUID = Field(..., description="Audit entry UUID")
    user_id: UUID = Field(..., description="User UUID")
    dataset_id: UUID = Field(..., description="Dataset UUID")
    dataset_name: Optional[str] = Field(None, description="Dataset name for display")
    question: str = Field(..., description="Original user question")
    intent: str = Field(..., description="Classified intent")
    sql_executed: Optional[str] = Field(None, description="SQL query executed")
    answer_narrative: str = Field(..., description="AI-generated answer")
    model_used: str = Field(..., description="AI model used")
    tokens_used: int = Field(..., description="Tokens consumed")
    latency_ms: int = Field(..., description="Processing time in ms")
    error: Optional[str] = Field(None, description="Error message if any")
    created_at: datetime = Field(..., description="Timestamp")

    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    """Schema for paginated audit log response."""

    entries: List[AuditLogEntry] = Field(..., description="Audit log entries")
    total: int = Field(..., description="Total number of entries")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=50, description="Page size")
