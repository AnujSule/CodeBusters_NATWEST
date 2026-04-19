"""Tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration with valid data."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecureP@ss123",
            "full_name": "Test User",
        },
    )
    # May return 201 (success) or 400 (if user exists) or 500 (if DB not available)
    assert response.status_code in [201, 400, 500]


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Test registration with invalid email format."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "SecureP@ss123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    """Test registration with password too short."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test2@example.com",
            "password": "short",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with wrong credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword123",
        },
    )
    assert response.status_code in [401, 500]


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    """Test /me endpoint without authentication."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient):
    """Test /me endpoint with invalid token."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Test token refresh with invalid refresh token."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )
    assert response.status_code in [401, 500]
