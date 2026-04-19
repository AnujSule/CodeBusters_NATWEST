"""Shared test fixtures and configuration."""

import asyncio
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.utils.security import hash_password, create_access_token


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_user_id() -> str:
    """Generate a mock user ID."""
    return str(uuid4())


@pytest.fixture
def auth_headers(mock_user_id: str) -> dict:
    """Generate authentication headers with a valid JWT token."""
    token = create_access_token(subject=mock_user_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_csv_content() -> bytes:
    """Sample CSV content for testing."""
    return b"""date,region,product,revenue,transactions
2024-01-01,North,Widget A,125000,4200
2024-01-01,South,Widget A,98000,3100
2024-02-01,North,Widget B,129000,4300
2024-02-01,South,Widget B,76000,2400
"""


@pytest.fixture
def sample_question() -> str:
    """Sample question for testing."""
    return "What is the total revenue by region?"
