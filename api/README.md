# NARRA_FORGE API Documentation

**Version:** 2.0.0  
**Status:** Phase 2 Complete (87.5% - 14/16 tasks)

Professional REST API for AI-powered narrative generation platform.

---

## 🎯 Quick Start

### 1. Start Services

```bash
# Start PostgreSQL & Redis
docker compose -f docker-compose.api.yml up -d postgres redis

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker (separate terminal)
celery -A api.celery_app worker --loglevel=info
```

### 2. Access API

- **API Server:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc (ReDoc)
- **Health Check:** http://localhost:8000/health

---

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/register` | Register new user | ❌ |
| `POST` | `/auth/login` | Login with email/password | ❌ |
| `POST` | `/auth/refresh` | Refresh access token | ❌ |
| `GET` | `/auth/oauth/google` | Google OAuth2 login | ❌ |
| `GET` | `/auth/oauth/github` | GitHub OAuth2 login | ❌ |

**Example Registration:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "subscription_tier": "FREE",
    "monthly_generation_limit": 5
  }
}
```

---

### Projects

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/projects/` | List user's projects (paginated) | ✅ |
| `POST` | `/projects/` | Create new project | ✅ |
| `GET` | `/projects/{id}` | Get project details | ✅ |
| `PUT` | `/projects/{id}` | Update project | ✅ |
| `DELETE` | `/projects/{id}` | Delete project (cascade) | ✅ |

**Example Create Project:**
```bash
curl -X POST http://localhost:8000/projects/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Fantasy World",
    "description": "Collection of fantasy stories",
    "default_genre": "fantasy",
    "default_production_type": "short_story"
  }'
```

---

### Generation Jobs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/jobs/` | List jobs (filtered, paginated) | ✅ |
| `POST` | `/jobs/` | Create new generation job | ✅ |
| `GET` | `/jobs/{id}` | Get full job details | ✅ |
| `GET` | `/jobs/{id}/status` | Get lightweight status (for polling) | ✅ |
| `POST` | `/jobs/{id}/cancel` | Cancel running job | ✅ |
| `POST` | `/jobs/{id}/resume` | Resume failed job from checkpoint | ✅ |

**Example Create Job:**
```bash
curl -X POST http://localhost:8000/jobs/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "project-uuid-here",
    "production_brief": {
      "production_type": "short_story",
      "genre": "fantasy",
      "subject": "A wizard apprentice discovers forbidden magic",
      "style_instructions": "Dark and mysterious tone",
      "target_length": 5000,
      "character_count": 3
    }
  }'
```

**Job Status Response:**
```json
{
  "id": "job-uuid",
  "status": "RUNNING",
  "current_stage": "Generating narrative",
  "progress_percentage": 45.5,
  "estimated_cost_usd": 0.25,
  "actual_cost_usd": 0.12,
  "can_resume": false
}
```

---

### Narratives

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/narratives/` | List narratives (filtered, paginated) | ✅ |
| `GET` | `/narratives/{id}` | Get full narrative with metadata | ✅ |
| `GET` | `/narratives/{id}/text` | Get plain text only | ✅ |
| `DELETE` | `/narratives/{id}` | Delete narrative | ✅ |
| `GET` | `/narratives/{id}/export/{format}` | Export (PDF/ePub/Docx) | ✅ Phase 4 |
| `GET` | `/narratives/{id}/versions` | Get version history | ✅ Phase 4 |
| `POST` | `/narratives/{id}/regenerate` | Create new version | ✅ Phase 4 |

**Example List Narratives:**
```bash
curl -X GET "http://localhost:8000/narratives/?page=1&page_size=10&genre=fantasy" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### Health & Monitoring

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health/` | Basic health check | ❌ |
| `GET` | `/health/ready` | Readiness (DB connectivity) | ❌ |
| `GET` | `/health/live` | Liveness check | ❌ |
| `GET` | `/health/metrics` | Prometheus metrics info | ❌ |

---

## 🔐 Authentication

All protected endpoints require JWT authentication via `Authorization` header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Token Lifecycle:**
- **Access Token:** 30 minutes (default)
- **Refresh Token:** 7 days (default)

**Refresh Flow:**
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

---

## 💾 Database Schema

### Users Table
- UUID primary key
- Email (unique)
- Hashed password (bcrypt)
- Subscription tier (FREE, PRO, ENTERPRISE)
- Monthly limits (generations, cost)
- OAuth provider fields (Google, GitHub)

### Projects Table
- UUID primary key
- Foreign key to User
- Name, description
- World ID (memory system integration)
- Statistics (narrative count, total words, total cost)

### GenerationJobs Table
- UUID primary key
- Foreign keys to User, Project
- Status (QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED)
- Production brief (JSON)
- Progress tracking (stage, percentage)
- Cost tracking (estimated, actual, tokens)
- Celery task ID
- Error handling (retry count, can_resume)

### Narratives Table
- UUID primary key
- Foreign keys to User, Project, Job
- Full narrative text
- Metadata (characters, structure, segments)
- Quality metrics (coherence, logic, etc.)
- Versioning (version number, parent ID)
- Statistics (view count, download count)

### UsageLogs Table
- Billing and usage tracking
- Token consumption per job
- Cost tracking per user

---

## ⚙️ Background Tasks (Celery)

### Worker Configuration

```bash
# Start worker with concurrency
celery -A api.celery_app worker \
  --loglevel=info \
  --concurrency=2 \
  --queue=narrative_generation
```

### Task: `generate_narrative_task`

**What it does:**
1. Loads job from database
2. Updates status to RUNNING
3. Executes NarraForge pipeline (orchestrator)
4. Saves narrative to database
5. Updates project & user statistics
6. Reports progress via Celery state

**Lifecycle:**
- **Time Limit:** 7200s (2 hours)
- **Retries:** 3 attempts with 60s delay
- **Checkpoint Support:** Can resume failed jobs
- **Progress Tracking:** Real-time updates to database

---

## 🎨 Pydantic Schemas

All requests and responses use Pydantic models for validation:

### Auth Schemas
- `UserRegisterRequest` - Email, password (validated strength), full name
- `UserLoginRequest` - Email, password
- `AuthResponse` - Tokens + user info
- `UserResponse` - User profile

### Project Schemas
- `ProjectCreateRequest`, `ProjectUpdateRequest`
- `ProjectResponse`, `ProjectListResponse`

### Job Schemas
- `JobCreateRequest` - Production brief
- `JobResponse` - Full job details
- `JobStatusResponse` - Lightweight status
- `JobListResponse` - Paginated list

### Narrative Schemas
- `NarrativeResponse` - Without full text (for lists)
- `NarrativeDetailResponse` - With full text and metadata
- `NarrativeListResponse` - Paginated list

---

## 📊 Subscription Tiers & Limits

| Tier | Monthly Generations | Monthly Cost Limit | Features |
|------|---------------------|-------------------|----------|
| **FREE** | 5 | $0 | Basic narratives (up to 10k words) |
| **PRO** | 100 | Unlimited | Full features, priority queue |
| **ENTERPRISE** | Unlimited | Unlimited | Custom models, dedicated support |

**Limit Enforcement:**
- Checked before job creation
- Returns 403 if limit exceeded
- Tracked in `User.monthly_generations_used` and `User.monthly_cost_used_usd`

---

## 🔧 Configuration (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/narra_forge

# Redis & Celery
CELERY_BROKER_URL=redis://:password@localhost:6379/0
CELERY_RESULT_BACKEND=redis://:password@localhost:6379/1

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth2
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_PORT=9090
```

---

## 🐳 Docker Deployment

### Full Stack

```bash
# Start all services
docker compose -f docker-compose.api.yml up -d

# Check logs
docker compose -f docker-compose.api.yml logs -f api
docker compose -f docker-compose.api.yml logs -f celery_worker

# Stop all
docker compose -f docker-compose.api.yml down
```

### Services
- **postgres** - PostgreSQL 16
- **redis** - Redis 7 for Celery & caching
- **api** - FastAPI application
- **celery_worker** - Celery worker for async tasks
- **celery_beat** - Scheduled tasks (optional, --profile full)

---

## 📈 Monitoring

### Prometheus Metrics
- Pipeline duration, success rate
- Cost tracking (per model, per hour)
- Token usage
- Quality scores

### Grafana Dashboard
- 10-panel dashboard (`monitoring/grafana/dashboards/`)
- Real-time job tracking
- Cost analytics

### Sentry Error Tracking
- Automatic error capture
- Performance monitoring
- Transaction tracking

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test specific module
pytest tests/integration/test_api.py

# With coverage
pytest tests/ --cov=api --cov-report=html
```

**Current Coverage:** 86.45% (Phase 1)

---

## 🚀 Phase 2 Status: **COMPLETE**

### ✅ Implemented (14/16 tasks):
1. ✅ Database migrations (Alembic, 5 tables)
2. ✅ JWT authentication module
3. ✅ POST /auth/register
4. ✅ POST /auth/login
5. ✅ POST /auth/refresh
6. ✅ OAuth2 structure (needs external config)
7-8. ✅ OAuth2 placeholders (Google, GitHub)
9. ✅ Projects CRUD (5 endpoints)
10. ✅ Celery app configuration
11. ✅ generate_narrative_task
12. ✅ Jobs endpoints (6 endpoints)
13. ✅ Narratives endpoints (4 endpoints + 3 Phase 4 placeholders)

### ⏭️ Skipped (optional for MVP):
14. WebSockets (complex, needs frontend)
15. Rate limiting middleware (can add later)

### 📋 Next Phase:
**Phase 3: Frontend (Next.js 14 + TypeScript + shadcn/ui)**

---

## 📞 Support

- **Documentation:** http://localhost:8000/docs
- **Health Status:** http://localhost:8000/health
- **Prometheus Metrics:** http://localhost:9090 (if running monitoring stack)
- **Grafana Dashboards:** http://localhost:3000 (if running monitoring stack)

---

**Built with:**
- FastAPI 0.115+
- SQLAlchemy 2.0 (async)
- Celery 5.4
- PostgreSQL 16
- Redis 7
- Pydantic 2.9
- JWT (python-jose)
- bcrypt password hashing

**License:** MIT  
**Author:** NARRA_FORGE Team  
**Version:** 2.0.0
