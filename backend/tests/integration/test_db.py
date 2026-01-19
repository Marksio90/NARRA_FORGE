"""Integration tests for database."""

import pytest
from sqlalchemy import text

from models.database import engine


@pytest.mark.asyncio  # type: ignore[misc]
async def test_database_connection() -> None:
    """Test database connection."""
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio  # type: ignore[misc]
async def test_tables_exist() -> None:
    """Test that all tables exist."""
    async with engine.begin() as conn:
        # Check jobs table
        result = await conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'jobs')")
        )
        assert result.scalar() is True

        # Check artifacts table
        result = await conn.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = 'artifacts')"
            )
        )
        assert result.scalar() is True

        # Check worlds table
        result = await conn.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'worlds')"
            )
        )
        assert result.scalar() is True


@pytest.mark.asyncio  # type: ignore[misc]
async def test_alembic_version() -> None:
    """Test that Alembic version table exists."""
    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = 'alembic_version')"
            )
        )
        assert result.scalar() is True
