# Health Check Endpoints Documentation

This document describes the health check endpoints available in the NarraForge backend API.

## Overview

NarraForge provides three health check endpoints for monitoring system status:

1. **`/health/live`** - Liveness check (basic ping)
2. **`/health/ready`** - Readiness check (ready for requests?)
3. **`/health`** - Full health check (detailed status)

## Endpoints

### 1. Liveness Check: `/health/live`

**Purpose**: Verify the application is running

**Use Case**: Used by orchestrators (Kubernetes, Docker Swarm) to know if the container should be restarted

**Response** (200 OK):
```json
{
  "alive": true,
  "message": "Application is running"
}
```

**Test**:
```bash
curl http://localhost:8000/health/live
```

---

### 2. Readiness Check: `/health/ready`

**Purpose**: Verify the system is ready to process requests

**Use Case**: Used by load balancers to know if traffic should be routed to this instance

**Checks**:
- ✓ PostgreSQL database connection
- ✓ Redis connection (for Celery tasks)
- ✓ OpenAI API key configuration

**Response when ready** (200 OK):
```json
{
  "ready": true,
  "message": "System is ready to process requests"
}
```

**Response when NOT ready** (200 OK with ready: false):
```json
{
  "ready": false,
  "reason": "OpenAI API key not configured"
}
```

**Test**:
```bash
curl http://localhost:8000/health/ready
```

---

### 3. Full Health Check: `/health`

**Purpose**: Get detailed status of all system components

**Use Case**: Monitoring dashboards, debugging, system status overview

**Checks**:
- ✓ PostgreSQL database connection
- ✓ Redis connection
- ✓ OpenAI API configuration
- ✓ Anthropic API configuration (optional)

**Response when healthy** (200 OK):
```json
{
  "status": "healthy",
  "app": "NarraForge",
  "version": "0.1.0",
  "services": {
    "database": {
      "status": "connected",
      "type": "postgresql"
    },
    "redis": {
      "status": "connected",
      "used_for": "celery_broker"
    },
    "openai": {
      "status": "configured",
      "available": true,
      "required": true
    },
    "anthropic": {
      "status": "configured",
      "available": true,
      "required": false
    }
  }
}
```

**Response when unhealthy** (200 OK with status: unhealthy):
```json
{
  "status": "unhealthy",
  "app": "NarraForge",
  "version": "0.1.0",
  "error": "OpenAI API key not configured (required for AI generation)",
  "services": {
    "database": {
      "status": "connected",
      "type": "postgresql"
    },
    "redis": {
      "status": "connected",
      "used_for": "celery_broker"
    },
    "openai": {
      "status": "not_configured",
      "available": false,
      "required": true
    },
    "anthropic": {
      "status": "not_configured",
      "available": false,
      "required": false
    }
  }
}
```

**Test**:
```bash
curl http://localhost:8000/health
```

---

## Status Values

### Overall Status
- `healthy` - All required services are operational
- `degraded` - Redis is down (optional for some operations)
- `unhealthy` - Critical services are down (database or OpenAI)

### Service Status
- `connected` - Service is accessible
- `disconnected` - Service is not accessible
- `configured` - API key is set
- `not_configured` - API key is missing or placeholder

---

## Testing the Endpoints

### Quick Test (Manual)
```bash
# Test liveness
curl http://localhost:8000/health/live

# Test readiness
curl http://localhost:8000/health/ready

# Test full health check
curl http://localhost:8000/health
```

### Using Test Scripts

**Linux/Mac**:
```bash
./test_health_endpoints.sh
```

**Windows PowerShell**:
```powershell
.\test_health_endpoints.ps1
```

---

## Common Issues and Solutions

### Issue: `/health/ready` returns `ready: false` with "OpenAI API key not configured"

**Solution**: Configure your OpenAI API key

1. Create `.env` file in project root (if not exists):
```bash
cp .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
```

3. Restart the backend service:
```bash
docker compose restart narraforge-backend
```

### Issue: `/health` shows `database: disconnected`

**Solution**: Ensure PostgreSQL container is running

```bash
# Check if PostgreSQL is running
docker compose ps narraforge-postgres

# If not running, start it
docker compose up -d narraforge-postgres

# Check logs
docker compose logs narraforge-postgres
```

### Issue: `/health` shows `redis: disconnected`

**Solution**: Ensure Redis container is running

```bash
# Check if Redis is running
docker compose ps narraforge-redis

# If not running, start it
docker compose up -d narraforge-redis

# Check logs
docker compose logs narraforge-redis
```

---

## Integration with Monitoring Tools

### Prometheus

The health endpoints can be scraped by Prometheus for monitoring:

```yaml
scrape_configs:
  - job_name: 'narraforge'
    metrics_path: '/health'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:8000']
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

### Docker Healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## Implementation Details

**Location**: `backend/app/api/health.py`

**Router Registration**: The health router is registered in `backend/app/main.py`:
```python
app.include_router(health.router, tags=["Health"])
```

**Dependencies**:
- PostgreSQL (via SQLAlchemy)
- Redis (via redis-py)
- FastAPI
- Settings/Config

---

## API Documentation

All health endpoints are documented in the OpenAPI/Swagger UI:

**Access**: http://localhost:8000/docs

Navigate to the "Health" section to see detailed documentation and test the endpoints interactively.

---

## Security Considerations

- Health endpoints do NOT expose API keys (only show if configured)
- No authentication required (public endpoints for monitoring)
- Safe to expose to monitoring systems
- Error messages do not include sensitive information

---

## Questions?

For more information about the NarraForge system, see:
- Main README: `README.md`
- API Documentation: http://localhost:8000/docs
- Environment Setup: `.env.example`
