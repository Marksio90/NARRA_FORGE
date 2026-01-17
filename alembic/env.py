"""
Alembic environment configuration for NARRA_FORGE.

This module connects Alembic to our SQLAlchemy models and database.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import all models to ensure they're registered with Base
from api.models.base import Base, SYNC_DATABASE_URL
from api.models import User, Project, GenerationJob, Narrative, UsageLog

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate' support
target_metadata = Base.metadata

# Set database URL from environment or use default
def get_url():
    """Get database URL from environment variables."""
    # Try to get from environment first
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # Convert async URL to sync for Alembic
        return db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

    # Build from individual components
    user = os.getenv("DB_USER", "narra_forge")
    password = os.getenv("DB_PASSWORD", "password")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "narra_forge")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Override sqlalchemy.url in config
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
