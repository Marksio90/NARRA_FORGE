# NARRA_FORGE - Docker Deployment Guide

Complete guide to running NARRA_FORGE platform with Docker Compose.

## Architecture

The platform consists of 5 services:

1. **PostgreSQL 17** - Main database with pgvector extension
2. **Redis 7** - Message broker and cache
3. **API (FastAPI)** - Backend REST API
4. **Worker (Celery)** - Background task processor
5. **UI (Next.js 16)** - Production web interface

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- OpenAI API key (for production use)

## Quick Start

### 1. Environment Setup

Create `.env` file in the project root:

```bash
# OpenAI API (required for production)
OPENAI_API_KEY=your-api-key-here

# Database (optional - defaults provided)
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/narra_forge

# Redis (optional - defaults provided)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Environment
ENVIRONMENT=development
```

### 2. Start All Services

```bash
# Start with dev profile (includes all services)
docker compose --profile dev up -d

# Or build first if you made changes
docker compose --profile dev up --build -d
```

### 3. Check Status

```bash
# View running containers
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f ui
docker compose logs -f worker
```

### 4. Access Services

- **UI (Frontend)**: http://localhost:3000
- **API (Backend)**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Development Workflow

### Start Services

```bash
# Start all services in background
docker compose --profile dev up -d

# Start with logs visible
docker compose --profile dev up

# Start specific service
docker compose up api
docker compose up ui
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v
```

### Rebuild After Changes

```bash
# Rebuild specific service
docker compose build api
docker compose build ui

# Rebuild and restart
docker compose up --build api
docker compose up --build ui
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f ui
docker compose logs -f worker

# Last 100 lines
docker compose logs --tail=100 api
```

### Execute Commands

```bash
# Run backend tests
docker compose exec api uv run pytest tests/unit/ -v

# Access backend shell
docker compose exec api bash

# Access database
docker compose exec postgres psql -U user -d narra_forge

# Check Redis
docker compose exec redis redis-cli
```

## Database Management

### Run Migrations

```bash
# Generate migration
docker compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec api alembic upgrade head

# Rollback
docker compose exec api alembic downgrade -1
```

### Backup Database

```bash
# Create backup
docker compose exec postgres pg_dump -U user narra_forge > backup.sql

# Restore backup
docker compose exec -T postgres psql -U user narra_forge < backup.sql
```

## Production Deployment

### 1. Create Production Config

```bash
cp .env.example .env.production
# Edit .env.production with production values
```

### 2. Build Production Images

```bash
# Build optimized images
docker compose -f compose.yaml build --no-cache

# Tag images for registry
docker tag narra-forge-api:latest your-registry/narra-forge-api:v1.0.0
docker tag narra-forge-ui:latest your-registry/narra-forge-ui:v1.0.0
```

### 3. Deploy to Production

```bash
# Use production profile
docker compose --profile prod up -d

# Or with specific env file
docker compose --env-file .env.production up -d
```

### 4. Health Checks

All services include health checks:

```bash
# Check container health
docker compose ps

# Manual health check
curl http://localhost:8000/health
curl http://localhost:3000
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker compose logs api
docker compose logs ui

# Check container status
docker compose ps

# Restart service
docker compose restart api
```

### Database Connection Issues

```bash
# Verify database is running
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Test connection
docker compose exec postgres pg_isready -U user -d narra_forge
```

### UI Can't Connect to API

```bash
# Verify API is healthy
curl http://localhost:8000/health

# Check network
docker network inspect narra-forge_narra-network

# Rebuild UI with correct API URL
docker compose build ui
docker compose up -d ui
```

### Worker Not Processing Tasks

```bash
# Check worker logs
docker compose logs worker

# Verify Redis connection
docker compose exec redis redis-cli ping

# Restart worker
docker compose restart worker
```

### Out of Disk Space

```bash
# Remove unused containers
docker system prune

# Remove unused images
docker image prune -a

# Remove unused volumes (⚠️ deletes data)
docker volume prune
```

## Performance Tuning

### Resource Limits

Add to `compose.yaml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### PostgreSQL Tuning

```yaml
postgres:
  environment:
    - POSTGRES_SHARED_BUFFERS=256MB
    - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
    - POSTGRES_MAINTENANCE_WORK_MEM=128MB
```

### Redis Tuning

```yaml
redis:
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

## Monitoring

### Container Stats

```bash
# Real-time stats
docker stats

# Specific container
docker stats narra-forge-api
```

### Logs Export

```bash
# Export all logs
docker compose logs > logs.txt

# Export with timestamps
docker compose logs --timestamps > logs_timestamped.txt
```

### Health Check Script

Create `health_check.sh`:

```bash
#!/bin/bash
echo "Checking API..."
curl -f http://localhost:8000/health || echo "API DOWN"

echo "Checking UI..."
curl -f http://localhost:3000 || echo "UI DOWN"

echo "Checking PostgreSQL..."
docker compose exec postgres pg_isready -U user -d narra_forge || echo "DB DOWN"

echo "Checking Redis..."
docker compose exec redis redis-cli ping || echo "REDIS DOWN"
```

## Security

### Production Checklist

- [ ] Change default PostgreSQL password
- [ ] Use secrets management for API keys
- [ ] Enable HTTPS with reverse proxy (nginx/traefik)
- [ ] Set up firewall rules
- [ ] Enable Docker content trust
- [ ] Regular security updates
- [ ] Implement rate limiting
- [ ] Set up log aggregation

### Secrets Management

Use Docker secrets:

```yaml
services:
  api:
    secrets:
      - openai_api_key
      - db_password

secrets:
  openai_api_key:
    external: true
  db_password:
    external: true
```

## Scaling

### Horizontal Scaling

```bash
# Scale workers
docker compose up --scale worker=3 -d

# Scale API (requires load balancer)
docker compose up --scale api=3 -d
```

### Load Balancer Example (nginx)

```nginx
upstream api_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://api_backend;
    }
}
```

## Maintenance

### Update Images

```bash
# Pull latest images
docker compose pull

# Restart with new images
docker compose up -d
```

### Cleanup

```bash
# Remove stopped containers
docker compose rm

# Remove all project containers and networks
docker compose down

# Remove everything including volumes
docker compose down -v --remove-orphans
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/NARRA_FORGE/issues
- Documentation: See README.md files in backend/ and ui/
