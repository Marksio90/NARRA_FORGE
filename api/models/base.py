"""
Base database model and session management.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.pool import NullPool

# Database URL (will be configured from settings)
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/narra_forge"
SYNC_DATABASE_URL = "postgresql+psycopg2://user:password@localhost/narra_forge"


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
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


# Async engine (for FastAPI)
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL logging (set to False in production)
    pool_pre_ping=True,
    poolclass=NullPool,  # Disable pooling for async
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
    echo=True,
    pool_pre_ping=True,
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
