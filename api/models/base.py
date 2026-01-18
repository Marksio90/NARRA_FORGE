"""
Base database model and session management.
"""

import os
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.pool import NullPool


def get_database_url() -> str:
    """Get database URL from environment variables."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Build from components
    user = os.getenv("DB_USER", "narra_forge")
    password = os.getenv("DB_PASSWORD", "password")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "narra_forge")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


def get_sync_database_url() -> str:
    """Get sync database URL for migrations."""
    async_url = get_database_url()
    return async_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")


# Database URLs
DATABASE_URL = get_database_url()
SYNC_DATABASE_URL = get_sync_database_url()


class Base(DeclarativeBase):
    """
    Base class for all database models.

    Provides:
    - Auto-generated table names (snake_case from class name)
    - Common id, created_at, updated_at fields
    - Async session support
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Auto-generate table name from class name."""
        # Convert CamelCase to snake_case
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    # Common fields for all models
    id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


# Async engine (for FastAPI)
# Determine if we should echo SQL based on environment
_db_echo = os.getenv("DB_ECHO", "false").lower() == "true"
_debug = os.getenv("DEBUG", "false").lower() == "true"

async_engine = create_async_engine(
    DATABASE_URL,
    echo=_db_echo or _debug,  # SQL logging only in debug mode
    pool_pre_ping=True,  # Verify connections before using
    pool_size=20,  # Number of connections to maintain
    max_overflow=10,  # Additional connections when pool is exhausted
    pool_timeout=30,  # Wait time for connection from pool
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine (for Alembic migrations)
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=_db_echo or _debug,  # SQL logging only in debug mode
    pool_pre_ping=True,
    pool_size=10,  # Smaller pool for migrations
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=3600,
)


async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI routes.

    Usage:
        @app.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create all tables)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all tables (for testing)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
