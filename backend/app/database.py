"""
Database configuration and session management
"""

import os
import glob
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from typing import Generator

from app.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=settings.DEBUG,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


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
    Must be called AFTER create_all() to ensure tables exist.
    """
    migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')

    if not os.path.isdir(migrations_dir):
        print("⚠️  No migrations directory found")
        return

    migration_files = sorted(glob.glob(os.path.join(migrations_dir, '*.sql')))

    with engine.connect() as conn:
        for migration_path in migration_files:
            filename = os.path.basename(migration_path)
            # Skip init.sql as it's handled by postgres entrypoint
            if filename == 'init.sql':
                continue

            try:
                with open(migration_path, 'r') as f:
                    sql = f.read()

                print(f"  Applying: {filename}")
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                print(f"  Warning applying {filename}: {e}")
                conn.rollback()

    print("✅ Migrations complete!")


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
    )

    # First, create tables that don't exist
    Base.metadata.create_all(bind=engine)

    # Then apply SQL migrations (for schema changes to existing tables)
    print("📦 Applying database migrations...")
    apply_sql_migrations()
