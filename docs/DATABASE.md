# NARRA_FORGE Database Architecture

Complete guide to the NARRA_FORGE PostgreSQL database schema.

## Overview

NARRA_FORGE uses PostgreSQL with SQLAlchemy ORM and Alembic migrations.

**Stack:**
- **Database:** PostgreSQL 14+
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Adapters:** psycopg2 (sync), asyncpg (async)

## Schema

### Tables

#### 1. `users`

User accounts and authentication.

```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,

    -- OAuth
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),

    -- Profile
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),

    -- Subscription
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_ends_at TIMESTAMP,

    -- Usage limits
    monthly_generation_limit INTEGER DEFAULT 5,
    monthly_generations_used INTEGER DEFAULT 0,
    monthly_cost_limit_usd FLOAT DEFAULT 10.0,
    monthly_cost_used_usd FLOAT DEFAULT 0.0,

    -- Timestamps
    last_login_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

**Subscription Tiers:**
- `free`: 5 generations/month, $10 limit
- `pro`: 50 generations/month, $100 limit
- `enterprise`: Unlimited

#### 2. `projects`

User workspaces for organizing narratives.

```sql
CREATE TABLE projects (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,

    -- Project info
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- World settings
    world_id VARCHAR,

    -- Defaults
    default_genre VARCHAR(50),
    default_production_type VARCHAR(50),

    -- Statistics
    narrative_count INTEGER DEFAULT 0,
    total_word_count INTEGER DEFAULT 0,
    total_cost_usd FLOAT DEFAULT 0.0,

    -- Timestamps
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

#### 3. `generation_jobs`

Async narrative generation tasks.

```sql
CREATE TABLE generation_jobs (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    project_id VARCHAR REFERENCES projects(id) ON DELETE CASCADE,

    -- Job status
    status VARCHAR(20) DEFAULT 'queued',  -- queued, running, completed, failed, cancelled

    -- Input/Output
    production_brief JSON NOT NULL,
    output JSON,

    -- Progress
    current_stage VARCHAR(100),
    completed_stages JSON DEFAULT '[]',
    progress_percentage FLOAT DEFAULT 0.0,

    -- Cost tracking
    estimated_cost_usd FLOAT,
    actual_cost_usd FLOAT DEFAULT 0.0,
    tokens_used INTEGER DEFAULT 0,

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,

    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    can_resume BOOLEAN DEFAULT FALSE,

    -- Celery integration
    celery_task_id VARCHAR(255),

    -- Timestamps
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

**Job Lifecycle:**
1. User creates job → `status=queued`
2. Celery picks it up → `status=running`
3. Pipeline executes → progress updated
4. Completes → `status=completed` or `status=failed`

#### 4. `narratives`

Generated narratives (versioned).

```sql
CREATE TABLE narratives (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    project_id VARCHAR REFERENCES projects(id) ON DELETE CASCADE,
    job_id VARCHAR REFERENCES generation_jobs(id) ON DELETE SET NULL,

    -- Narrative info
    title VARCHAR(500),
    production_type VARCHAR(50) NOT NULL,
    genre VARCHAR(50) NOT NULL,

    -- Content
    narrative_text TEXT NOT NULL,
    word_count INTEGER NOT NULL,

    -- Metadata
    metadata JSON NOT NULL,
    quality_metrics JSON,
    overall_quality_score FLOAT,

    -- Cost
    generation_cost_usd FLOAT NOT NULL,
    tokens_used INTEGER NOT NULL,

    -- Versioning
    version INTEGER DEFAULT 1,
    parent_narrative_id VARCHAR REFERENCES narratives(id) ON DELETE SET NULL,

    -- Export
    exported_formats JSON DEFAULT '[]',

    -- Statistics
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

#### 5. `usage_logs`

Billing and usage tracking.

```sql
CREATE TABLE usage_logs (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    project_id VARCHAR REFERENCES projects(id) ON DELETE SET NULL,
    job_id VARCHAR REFERENCES generation_jobs(id) ON DELETE SET NULL,

    -- Usage details
    operation_type VARCHAR(50) NOT NULL,
    production_type VARCHAR(50),

    -- Tokens & Cost
    tokens_used INTEGER NOT NULL,
    cost_usd FLOAT NOT NULL,

    -- Model breakdown
    mini_tokens INTEGER DEFAULT 0,
    gpt4_tokens INTEGER DEFAULT 0,
    mini_cost_usd FLOAT DEFAULT 0.0,
    gpt4_cost_usd FLOAT DEFAULT 0.0,

    -- Timestamps
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## Relationships

```
users (1) ──< (N) projects
projects (1) ──< (N) generation_jobs
projects (1) ──< (N) narratives
generation_jobs (1) ──< (1) narratives
users (1) ──< (N) usage_logs
```

## Indexes

Performance-critical indexes:

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_oauth ON users(oauth_provider, oauth_id);

-- Project lookups
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_world_id ON projects(world_id);

-- Job lookups
CREATE INDEX idx_jobs_user_id ON generation_jobs(user_id);
CREATE INDEX idx_jobs_project_id ON generation_jobs(project_id);
CREATE INDEX idx_jobs_status ON generation_jobs(status);
CREATE INDEX idx_jobs_celery_task_id ON generation_jobs(celery_task_id);

-- Narrative lookups
CREATE INDEX idx_narratives_user_id ON narratives(user_id);
CREATE INDEX idx_narratives_project_id ON narratives(project_id);
CREATE INDEX idx_narratives_job_id ON narratives(job_id);
CREATE INDEX idx_narratives_type_genre ON narratives(production_type, genre);

-- Usage log lookups
CREATE INDEX idx_usage_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_project_id ON usage_logs(project_id);
CREATE INDEX idx_usage_job_id ON usage_logs(job_id);
```

## Setup

### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@14
brew services start postgresql@14

# Docker
docker run -d \
  --name narra-forge-postgres \
  -e POSTGRES_USER=narra_forge \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=narra_forge \
  -p 5432:5432 \
  postgres:14
```

### 2. Create Database

```bash
# Create user
createuser -P narra_forge

# Create database
createdb -O narra_forge narra_forge

# Or via Docker
docker exec -it narra-forge-postgres createdb -U narra_forge narra_forge
```

### 3. Set Environment Variables

```bash
# Add to .env
DB_USER=narra_forge
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=narra_forge

# Or use DATABASE_URL
DATABASE_URL=postgresql+asyncpg://narra_forge:password@localhost/narra_forge
```

### 4. Run Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Check current version
alembic current
```

## Usage

### Connect to Database

**Async (FastAPI):**
```python
from api.models.base import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

**Sync (scripts):**
```python
from api.models.base import sync_engine
from sqlalchemy.orm import Session

with Session(sync_engine) as session:
    users = session.query(User).all()
```

### Create User

```python
from api.models import User
from api.models.base import get_db

async def create_user(email: str, password: str):
    async with get_db() as db:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            subscription_tier=SubscriptionTier.FREE
        )
        db.add(user)
        await db.commit()
        return user
```

### Query Jobs

```python
from api.models import GenerationJob
from sqlalchemy import select

# Get running jobs
async with get_db() as db:
    result = await db.execute(
        select(GenerationJob)
        .where(GenerationJob.status == JobStatus.RUNNING)
    )
    running_jobs = result.scalars().all()

# Get user's jobs
async with get_db() as db:
    result = await db.execute(
        select(GenerationJob)
        .where(GenerationJob.user_id == user_id)
        .order_by(GenerationJob.created_at.desc())
    )
    user_jobs = result.scalars().all()
```

## Migrations

### Create Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add new field to users"

# Create empty migration
alembic revision -m "Custom data migration"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Upgrade to specific version
alembic upgrade abc123
```

### Migration Best Practices

1. **Always review auto-generated migrations**
   - Alembic might miss some changes
   - Check indexes and constraints

2. **Test migrations on staging first**
   - Never run untested migrations in production

3. **Write reversible migrations**
   - Always implement downgrade()
   - Test both upgrade and downgrade

4. **Use transactions**
   - Migrations are wrapped in transactions by default

5. **Data migrations**
   - Separate schema and data migrations
   - Use batch operations for large datasets

## Backup & Restore

### Backup

```bash
# Full backup
pg_dump -U narra_forge narra_forge > backup.sql

# Schema only
pg_dump -U narra_forge -s narra_forge > schema.sql

# Data only
pg_dump -U narra_forge -a narra_forge > data.sql
```

### Restore

```bash
# Restore full backup
psql -U narra_forge narra_forge < backup.sql

# Restore with create database
psql -U narra_forge postgres < backup.sql
```

## Performance

### Query Optimization

1. **Use indexes** - All foreign keys are indexed
2. **Limit results** - Use `.limit()` for large datasets
3. **Eager loading** - Use `selectinload()` for relationships
4. **Connection pooling** - Configured in `base.py`

### Monitoring

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Slow queries
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '1 second';

-- Table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI + SQLAlchemy Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)
