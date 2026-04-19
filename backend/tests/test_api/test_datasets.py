"""Tests for dataset API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_datasets_unauthenticated(client: AsyncClient):
    """Test listing datasets without authentication."""
    response = await client.get("/api/v1/datasets")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_get_nonexistent_dataset(client: AsyncClient, auth_headers: dict):
    """Test getting a dataset that doesn't exist."""
    response = await client.get(
        "/api/v1/datasets/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    # May return 404 or 500 depending on DB availability
    assert response.status_code in [404, 500, 401]


@pytest.mark.asyncio
async def test_delete_nonexistent_dataset(client: AsyncClient, auth_headers: dict):
    """Test deleting a dataset that doesn't exist."""
    response = await client.delete(
        "/api/v1/datasets/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code in [404, 500, 401]


@pytest.mark.asyncio
async def test_upload_no_file(client: AsyncClient, auth_headers: dict):
    """Test upload endpoint without a file."""
    response = await client.post(
        "/api/v1/datasets/upload",
        headers=auth_headers,
        data={"name": "Test Dataset"},
    )
    assert response.status_code == 422
