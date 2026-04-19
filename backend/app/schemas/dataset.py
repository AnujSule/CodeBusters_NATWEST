"""Dataset Pydantic schemas for request/response validation."""

from uuid import UUID
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class DatasetCreateRequest(BaseModel):
    """Schema for dataset creation metadata (file uploaded separately)."""

    name: str = Field(..., min_length=1, max_length=255, description="Dataset display name", examples=["Q1 Sales Data"])
    description: Optional[str] = Field(None, max_length=1000, description="Optional description", examples=["Quarterly sales data by region"])


class DatasetResponse(BaseModel):
    """Schema for dataset response."""

    id: str = Field(..., description="Dataset ID")
    user_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="Dataset display name")
    description: Optional[str] = Field(None, description="Dataset description")
    file_type: str = Field(..., description="File type (csv or pdf)")
    file_size_bytes: int = Field(..., description="File size in bytes")
    status: str = Field(..., description="Processing status: pending, processing, ready, failed")
    row_count: Optional[int] = Field(None, description="Number of rows (CSV only)")
    column_names: Optional[List[str]] = Field(None, description="Column names (CSV only)")
    schema_info: Optional[dict] = Field(None, description="Schema details with column types")
    created_at: str = Field(..., description="Upload timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class DatasetListResponse(BaseModel):
    """Schema for paginated dataset list."""

    datasets: List[DatasetResponse] = Field(..., description="List of datasets")
    total: int = Field(..., description="Total number of datasets")
