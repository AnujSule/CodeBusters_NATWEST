"""Authentication Pydantic schemas for request/response validation."""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(..., description="User email address", examples=["user@example.com"])
    password: str = Field(..., min_length=8, max_length=128, description="User password", examples=["SecureP@ss123"])
    full_name: str = Field(..., min_length=1, max_length=255, description="User full name", examples=["John Smith"])

    model_config = {"json_schema_extra": {"example": {"email": "user@example.com", "password": "SecureP@ss123", "full_name": "John Smith"}}}


class UserLoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(..., description="User email address", examples=["user@example.com"])
    password: str = Field(..., description="User password", examples=["SecureP@ss123"])


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="JWT refresh token to refresh")


class UserResponse(BaseModel):
    """Schema for user profile response."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    created_at: str = Field(..., description="Account creation timestamp")

    model_config = {"from_attributes": True}
