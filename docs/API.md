# NARRA_FORGE API Documentation

Complete REST API documentation for NARRA_FORGE narrative generation platform.

## Overview

The NARRA_FORGE API is a RESTful API built with FastAPI that provides programmatic access to narrative generation capabilities.

**Base URL:** `http://localhost:8000`
**API Version:** `2.0.0`
**Documentation:** `http://localhost:8000/docs` (Swagger UI)
**ReDoc:** `http://localhost:8000/redoc`

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# At minimum, set:
# - DATABASE_URL
# - JWT_SECRET_KEY
# - OPENAI_API_KEY
```

### 2. Setup Database

```bash
# Install PostgreSQL (see DATABASE.md for details)

# Run migrations
alembic upgrade head
```

### 3. Start API Server

```bash
# Development mode (with auto-reload)
python run_api.py

# Or with uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Check readiness (database connectivity)
curl http://localhost:8000/health/ready

# View API docs
open http://localhost:8000/docs
```

## Architecture

### Stack

- **Framework:** FastAPI 0.109+
- **ASGI Server:** Uvicorn
- **Database:** PostgreSQL 14+ with SQLAlchemy 2.0 (async)
- **Task Queue:** Celery with Redis
- **Authentication:** JWT tokens (python-jose)
- **WebSockets:** For real-time progress updates

### Project Structure

```
api/
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── dependencies.py      # Dependency injection
├── middleware.py        # Custom middleware
├── models/              # SQLAlchemy models
│   ├── user.py
│   ├── project.py
│   ├── job.py
│   ├── narrative.py
│   └── usage.py
├── routes/              # API endpoints
│   ├── health.py        # Health checks
│   ├── auth.py          # Authentication
│   ├── projects.py      # Project management
│   ├── jobs.py          # Generation jobs
│   └── narratives.py    # Narrative retrieval
├── schemas/             # Pydantic schemas (TODO)
└── services/            # Business logic (TODO)
```

## API Endpoints

### Root

**GET /**

Get API information.

```bash
curl http://localhost:8000/
```

Response:
```json
{
  "name": "NARRA_FORGE API",
  "version": "2.0.0",
  "description": "Professional AI-powered narrative generation platform",
  "docs": "/docs",
  "health": "/health",
  "endpoints": {
    "auth": "/auth",
    "projects": "/projects",
    "jobs": "/jobs",
    "narratives": "/narratives"
  }
}
```

### Health Checks

#### GET /health

Basic health check - always returns 200 if server is running.

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-17T12:00:00",
  "service": "NARRA_FORGE API",
  "version": "2.0.0"
}
```

#### GET /health/ready

Readiness check - verifies dependencies (database, Redis, etc.).

```bash
curl http://localhost:8000/health/ready
```

Response:
```json
{
  "status": "ready",
  "timestamp": "2024-01-17T12:00:00",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "celery": "ok"
  }
}
```

#### GET /health/live

Liveness check - simple check for Kubernetes/Docker health probes.

```bash
curl http://localhost:8000/health/live
```

#### GET /health/metrics

Get metrics endpoint information.

```bash
curl http://localhost:8000/health/metrics
```

### Authentication

**Status:** 🚧 Not yet implemented (Phase 2, Task 4)

All authentication endpoints currently return `501 Not Implemented`.

#### POST /auth/register

Register new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

#### POST /auth/login

Login with email/password, get JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /auth/refresh

Refresh access token using refresh token.

#### GET /auth/oauth/google

Google OAuth2 login flow.

#### GET /auth/oauth/github

GitHub OAuth2 login flow.

### Projects

**Status:** 🚧 Not yet implemented (Phase 2, Task 5)

Projects are workspaces for organizing narratives.

#### GET /projects

List all projects for authenticated user.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)
- `sort` (str): Sort field (default: created_at)

#### POST /projects

Create new project.

**Request:**
```json
{
  "name": "My Fantasy Series",
  "description": "Epic fantasy world building",
  "default_genre": "fantasy",
  "default_production_type": "novel"
}
```

#### GET /projects/{project_id}

Get project by ID.

#### PUT /projects/{project_id}

Update project.

#### DELETE /projects/{project_id}

Delete project and all associated narratives.

### Generation Jobs

**Status:** 🚧 Not yet implemented (Phase 2, Task 5)

Jobs represent narrative generation tasks.

#### GET /jobs

List all jobs for authenticated user.

**Query Parameters:**
- `page` (int): Page number
- `page_size` (int): Items per page
- `status` (str): Filter by status (queued, running, completed, failed, cancelled)
- `project_id` (str): Filter by project

#### POST /jobs

Create new generation job.

**Request:**
```json
{
  "project_id": "proj_123",
  "production_brief": {
    "production_type": "short_story",
    "genre": "scifi",
    "inspiration": "A story about AI consciousness",
    "target_word_count": 5000,
    "target_audience": "Adult",
    "tone": "Thoughtful"
  }
}
```

**Response:**
```json
{
  "id": "job_456",
  "status": "queued",
  "estimated_cost_usd": 2.50,
  "created_at": "2024-01-17T12:00:00"
}
```

#### GET /jobs/{job_id}

Get job details with full progress information.

#### GET /jobs/{job_id}/status

Get real-time job status (lightweight endpoint for polling).

**Response:**
```json
{
  "id": "job_456",
  "status": "running",
  "current_stage": "a04_character_designer",
  "progress_percentage": 35.0,
  "actual_cost_usd": 0.87
}
```

#### POST /jobs/{job_id}/cancel

Cancel running job.

#### POST /jobs/{job_id}/resume

Resume failed job from last checkpoint.

### Narratives

**Status:** 🚧 Not yet implemented (Phase 2, Task 5)

Narratives are generated outputs.

#### GET /narratives

List all narratives for authenticated user.

**Query Parameters:**
- `page` (int): Page number
- `page_size` (int): Items per page
- `project_id` (str): Filter by project
- `production_type` (str): Filter by type
- `genre` (str): Filter by genre

#### GET /narratives/{narrative_id}

Get narrative by ID with full content.

**Response:**
```json
{
  "id": "narr_789",
  "title": "The Last Algorithm",
  "production_type": "short_story",
  "genre": "scifi",
  "word_count": 5247,
  "narrative_text": "Full story text...",
  "metadata": {
    "characters": [...],
    "structure": {...}
  },
  "quality_metrics": {
    "overall_score": 0.92,
    "coherence": 0.95,
    "language_quality": 0.89
  },
  "generation_cost_usd": 2.34,
  "created_at": "2024-01-17T12:00:00"
}
```

#### GET /narratives/{narrative_id}/export/{format}

Export narrative in specified format.

**Formats:** `txt`, `pdf`, `epub`, `docx`

**Response:** File download

#### DELETE /narratives/{narrative_id}

Delete narrative.

#### GET /narratives/{narrative_id}/versions

Get all versions of a narrative (version history).

#### POST /narratives/{narrative_id}/regenerate

Create new version by regenerating narrative with same brief.

## Authentication

### JWT Tokens

The API uses JWT (JSON Web Tokens) for authentication.

**Token Types:**
- **Access Token:** Short-lived (30 min), used for API requests
- **Refresh Token:** Long-lived (7 days), used to get new access tokens

**Usage:**

```bash
# Include in Authorization header
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/projects
```

### OAuth2

Optional OAuth2 integration with:
- **Google:** Sign in with Google account
- **GitHub:** Sign in with GitHub account

## Rate Limiting

**Default Limits:**
- 60 requests per minute
- 100 burst requests

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests per minute
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `501 Not Implemented`: Endpoint not yet implemented

### Error Response Format

```json
{
  "detail": "Error message",
  "request_id": "req_123",
  "error_type": "ValidationError"
}
```

## WebSocket API

**Status:** 🚧 Not yet implemented (Phase 2, Task 7)

Real-time progress updates via WebSockets.

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs/{job_id}');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Progress:', update.progress_percentage);
  console.log('Stage:', update.current_stage);
};
```

### Message Format

```json
{
  "type": "progress",
  "job_id": "job_456",
  "status": "running",
  "current_stage": "a05_relationship_mapper",
  "progress_percentage": 45.0,
  "actual_cost_usd": 1.23,
  "timestamp": "2024-01-17T12:05:00"
}
```

## Subscription Tiers

Users have different limits based on subscription tier:

| Tier | Monthly Generations | Cost Limit | Price |
|------|-------------------|------------|-------|
| Free | 5 | $10 | $0 |
| Pro | 50 | $100 | $19/mo |
| Enterprise | Unlimited | Unlimited | Custom |

## Cost Tracking

All operations track costs:
- Generation jobs track `estimated_cost_usd` and `actual_cost_usd`
- Users have `monthly_cost_used_usd` counter
- Usage logs record detailed token and cost breakdowns

## Monitoring

### Metrics

Prometheus metrics available at `http://localhost:9090/metrics`

**Key Metrics:**
- `api_requests_total`: Total API requests
- `api_request_duration_seconds`: Request duration
- `generation_jobs_total`: Total generation jobs
- `generation_jobs_duration_seconds`: Job duration
- `generation_cost_usd_total`: Total generation costs

### Grafana Dashboards

Pre-built dashboards available in `monitoring/grafana/dashboards/`

### Error Tracking

Optional Sentry integration for error tracking and performance monitoring.

## Development

### Running Tests

```bash
# API tests (TODO)
pytest tests/api/ -v

# With coverage
pytest tests/api/ --cov=api --cov-report=html
```

### API Documentation

FastAPI auto-generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Adding New Endpoints

1. Create route in `api/routes/`
2. Define Pydantic schemas in `api/schemas/`
3. Implement business logic in `api/services/`
4. Add tests in `tests/api/routes/`
5. Update this documentation

## Deployment

### Docker

```bash
# Build image
docker build -t narra-forge-api .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e JWT_SECRET_KEY=... \
  narra-forge-api
```

### Docker Compose

```bash
# Start all services (API, PostgreSQL, Redis, Celery)
docker-compose up -d

# View logs
docker-compose logs -f api
```

### Production

See `docs/DEPLOYMENT.md` for production deployment guide.

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Database Schema](./DATABASE.md)
- [Monitoring Guide](../MONITORING_GUIDE.md)

## Support

For issues and questions:
- GitHub Issues: https://github.com/Marksio90/NARRA_FORGE/issues
- Documentation: `/docs`
- API Status: `/health`
