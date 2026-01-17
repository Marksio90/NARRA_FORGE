"""
API Test Configuration and Fixtures.

Provides test fixtures for FastAPI testing with database setup/teardown.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from api.main import app
from api.models.base import Base, get_session
from api.config import settings


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://narra_forge:narra_forge@localhost:5432/narra_forge_test"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.

    Creates all tables before the test and drops them after.
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create test HTTP client with overridden database session.

    Args:
        db_session: Test database session fixture

    Yields:
        AsyncClient: HTTP test client
    """
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(client: AsyncClient) -> dict:
    """
    Create a test user and return auth tokens.

    Args:
        client: HTTP test client

    Returns:
        dict: User data with tokens
    """
    # Register user
    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200

    data = response.json()
    return {
        "user": data["user"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "email": "test@example.com",
        "password": "TestPass123"
    }


@pytest.fixture
async def auth_headers(test_user: dict) -> dict:
    """
    Get authorization headers for authenticated requests.

    Args:
        test_user: Test user fixture

    Returns:
        dict: Headers with Bearer token
    """
    return {
        "Authorization": f"Bearer {test_user['access_token']}"
    }


@pytest.fixture
async def test_project(client: AsyncClient, auth_headers: dict) -> dict:
    """
    Create a test project.

    Args:
        client: HTTP test client
        auth_headers: Authorization headers

    Returns:
        dict: Project data
    """
    response = await client.post(
        "/projects",
        json={
            "name": "Test Project",
            "description": "A test project for integration tests",
            "default_genre": "Science Fiction",
            "default_production_type": "Film"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()
