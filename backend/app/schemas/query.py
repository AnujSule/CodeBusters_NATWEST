"""Query Pydantic schemas for request/response validation."""

from uuid import UUID
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Schema for submitting a natural language question."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language question about the dataset",
        examples=["Why did revenue drop in February?"],
    )


class SourceCitation(BaseModel):
    """Schema for a single source citation."""

    file: str = Field(..., description="Source file name")
    columns: Optional[List[str]] = Field(None, description="Columns referenced")
    rows_used: Optional[int] = Field(None, description="Number of rows used in analysis")
    total_rows: Optional[int] = Field(None, description="Total rows in dataset")
    confidence: Optional[float] = Field(None, description="Confidence score 0-1")


class ChartSpec(BaseModel):
    """Schema for a Recharts-compatible chart specification."""

    type: str = Field(..., description="Chart type: bar, line, pie, area")
    title: str = Field(..., description="Chart title")
    x_key: str = Field(..., description="Column name for x-axis")
    y_key: str = Field(..., description="Column name for y-axis")
    color_key: Optional[str] = Field(None, description="Optional grouping column for color")
    data: List[dict] = Field(..., description="Chart data rows")


class QueryResponse(BaseModel):
    """Schema for query result response."""

    query_id: str = Field(..., description="Query log ID")
    intent: str = Field(..., description="Classified intent: compare, decompose, summarise, explain")
    answer: str = Field(..., description="Plain-English narrative answer")
    key_metric: Optional[str] = Field(None, description="One-line key metric summary")
    chart_spec: Optional[ChartSpec] = Field(None, description="Chart specification or null")
    sources: List[SourceCitation] = Field(default_factory=list, description="Source citations")
    sql_executed: Optional[str] = Field(None, description="SQL query executed (for transparency)")
    latency_ms: int = Field(..., description="Query processing time in milliseconds")
    model_used: str = Field(..., description="AI model used")
    created_at: str = Field(..., description="Query timestamp")

    model_config = {"from_attributes": True}


class QueryHistoryResponse(BaseModel):
    """Schema for query history list."""

    queries: List[QueryResponse] = Field(..., description="List of past queries")
    total: int = Field(..., description="Total number of queries")
