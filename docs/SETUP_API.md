# NARRA_FORGE API Setup Guide

Step-by-step guide to set up the NARRA_FORGE API server.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+ (for Celery)
- Git

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/Marksio90/NARRA_FORGE.git
cd NARRA_FORGE
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} installed')"
```

### 4. Setup PostgreSQL

#### Option A: Local PostgreSQL

```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql@14
brew services start postgresql@14

# Create database and user
sudo -u postgres psql

postgres=# CREATE USER narra_forge WITH PASSWORD 'your_password';
postgres=# CREATE DATABASE narra_forge OWNER narra_forge;
postgres=# GRANT ALL PRIVILEGES ON DATABASE narra_forge TO narra_forge;
postgres=# \q
```

#### Option B: Docker PostgreSQL

```bash
# Run PostgreSQL in Docker
docker run -d \
  --name narra-forge-postgres \
  -e POSTGRES_USER=narra_forge \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=narra_forge \
  -p 5432:5432 \
  postgres:14

# Verify connection
docker exec -it narra-forge-postgres psql -U narra_forge -c "SELECT version();"
```

### 5. Setup Redis

#### Option A: Local Redis

```bash
# Install Redis
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis
brew services start redis

# Verify Redis
redis-cli ping
# Should return: PONG
```

#### Option B: Docker Redis

```bash
# Run Redis in Docker
docker run -d \
  --name narra-forge-redis \
  -p 6379:6379 \
  redis:7-alpine

# Verify connection
docker exec -it narra-forge-redis redis-cli ping
# Should return: PONG
```

### 6. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

**Required Configuration:**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://narra_forge:your_password@localhost:5432/narra_forge

# JWT Secret (generate secure key)
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-key-here

# Redis
REDIS_URL=redis://localhost:6379/0

# API Settings
API_DEBUG=true
API_RELOAD=true
```

### 7. Run Database Migrations

```bash
# Run migrations to create tables
alembic upgrade head

# Verify tables were created
psql -U narra_forge -d narra_forge -c "\dt"
```

Expected output:
```
            List of relations
 Schema |       Name        | Type  |    Owner
--------+-------------------+-------+--------------
 public | alembic_version   | table | narra_forge
 public | generation_jobs   | table | narra_forge
 public | narratives        | table | narra_forge
 public | projects          | table | narra_forge
 public | usage_logs        | table | narra_forge
 public | users             | table | narra_forge
```

### 8. Start API Server

```bash
# Start development server with auto-reload
python run_api.py

# Or use uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
============================================================
Starting NARRA_FORGE API v2.0.0
============================================================
Environment: development
Host: 0.0.0.0:8000
Debug: True
Docs: http://0.0.0.0:8000/docs
Health: http://0.0.0.0:8000/health
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
```

### 9. Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "ok",
#   "timestamp": "2024-01-17T12:00:00",
#   "service": "NARRA_FORGE API",
#   "version": "2.0.0"
# }

# Check readiness (database connectivity)
curl http://localhost:8000/health/ready

# Expected response:
# {
#   "status": "ready",
#   "timestamp": "2024-01-17T12:00:00",
#   "checks": {
#     "database": "ok",
#     "redis": "not_checked",
#     "celery": "not_checked"
#   }
# }

# Open interactive docs
open http://localhost:8000/docs
```

## Optional: Setup Celery Worker

For background task processing (narrative generation):

```bash
# In a new terminal, activate venv and run Celery worker
source venv/bin/activate
celery -A api.celery worker --loglevel=info

# Optional: Run Flower for monitoring
celery -A api.celery flower --port=5555
# Open http://localhost:5555 in browser
```

## Docker Compose (All Services)

For a complete environment with all services:

```bash
# Create docker-compose.yml (TODO: create in Phase 2)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

## Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in .env matches your PostgreSQL configuration
- Test connection: `psql -U narra_forge -d narra_forge`

### Redis Connection Error

```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution:**
- Verify Redis is running: `redis-cli ping`
- Check REDIS_URL in .env
- Test connection: `redis-cli -u redis://localhost:6379/0 ping`

### Import Errors

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
- Verify virtual environment is activated: `which python`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (must be 3.10+)

### Port Already in Use

```
ERROR:    [Errno 48] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
```

**Solution:**
- Find process using port 8000: `lsof -i :8000`
- Kill process: `kill <PID>`
- Or use different port: `uvicorn api.main:app --port 8001`

### Migration Errors

```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**
- Check current version: `alembic current`
- Show migration history: `alembic history`
- Apply pending migrations: `alembic upgrade head`

## Development Workflow

1. **Make changes** to code
2. **Create migration** (if models changed): `alembic revision --autogenerate -m "Description"`
3. **Apply migration**: `alembic upgrade head`
4. **Test** changes: `pytest tests/api/`
5. **Commit** and push

## Next Steps

- ✅ API structure created
- 🚧 Implement JWT authentication (Task 4)
- 🚧 Create REST endpoints (Task 5)
- 🚧 Setup Celery integration (Task 6)
- 🚧 Add WebSocket support (Task 7)
- 🚧 Write API tests (Task 8)

## Resources

- [API Documentation](./API.md)
- [Database Documentation](./DATABASE.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
