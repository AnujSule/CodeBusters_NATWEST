"""Tests for query API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_query_unauthenticated(client: AsyncClient):
    """Test querying without authentication."""
    response = await client.post(
        "/api/v1/queries/00000000-0000-0000-0000-000000000000",
        json={"question": "What is the total revenue?"},
    )
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_query_nonexistent_dataset(client: AsyncClient, auth_headers: dict):
    """Test querying a dataset that doesn't exist."""
    response = await client.post(
        "/api/v1/queries/00000000-0000-0000-0000-000000000000",
        json={"question": "What is the total revenue?"},
        headers=auth_headers,
    )
    assert response.status_code in [404, 500, 401]


@pytest.mark.asyncio
async def test_query_empty_question(client: AsyncClient, auth_headers: dict):
    """Test querying with an empty question."""
    response = await client.post(
        "/api/v1/queries/00000000-0000-0000-0000-000000000000",
        json={"question": ""},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_query_history_unauthenticated(client: AsyncClient):
    """Test getting query history without authentication."""
    response = await client.get(
        "/api/v1/queries/00000000-0000-0000-0000-000000000000/history",
    )
    assert response.status_code in [401, 403]
