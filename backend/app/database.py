"""
Database configuration and session management
"""

import os
import glob
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from typing import Generator

from app.config import settings

logger = logging.getLogger(__name__)


# Create SQLAlchemy engine with proper connection pooling
# QueuePool (default) reuses connections instead of creating new ones per request
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections are alive before use
    pool_recycle=1800,    # Recycle connections after 30 minutes
    echo=settings.DEBUG,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Modern SQLAlchemy 2.0 declarative base
class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def apply_sql_migrations():
    """
    Apply SQL migrations from the migrations directory.
    Tracks applied migrations to avoid re-applying them.
    Must be called AFTER create_all() to ensure tables exist.
    """
    migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')

    if not os.path.isdir(migrations_dir):
        logger.warning("No migrations directory found")
        return

    migration_files = sorted(glob.glob(os.path.join(migrations_dir, '*.sql')))

    with engine.connect() as conn:
        # Create migration tracking table if not exists
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS _applied_migrations (
                filename VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.commit()

        # Get already-applied migrations
        result = conn.execute(text("SELECT filename FROM _applied_migrations"))
        applied = {row[0] for row in result}

        for migration_path in migration_files:
            filename = os.path.basename(migration_path)
            # Skip init.sql as it's handled by postgres entrypoint
            if filename == 'init.sql':
                continue

            # Skip already-applied migrations
            if filename in applied:
                logger.debug(f"Skipping already-applied migration: {filename}")
                continue

            try:
                with open(migration_path, 'r') as f:
                    sql = f.read()

                logger.info(f"Applying migration: {filename}")
                conn.execute(text(sql))
                conn.execute(
                    text("INSERT INTO _applied_migrations (filename) VALUES (:f)"),
                    {"f": filename}
                )
                conn.commit()
            except Exception as e:
                logger.warning(f"Warning applying {filename}: {e}")
                conn.rollback()

    logger.info("Migrations complete")


def init_db():
    """
    Initialize database tables and apply migrations
    """
    # Import all models here to ensure they are registered with Base
    from app.models import (
        project,
        world_bible,
        character,
        plot_structure,
        chapter,
        scene,
        continuity_fact,
        generation_log,
        user,
        series,
        publishing,
    )

    # First, create tables that don't exist
    Base.metadata.create_all(bind=engine)

    # Then apply SQL migrations (for schema changes to existing tables)
    logger.info("Applying database migrations...")
    apply_sql_migrations()
