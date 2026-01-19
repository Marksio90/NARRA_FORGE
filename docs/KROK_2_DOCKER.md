# KROK 2 — Docker-First Dev Environment

## STATUS: ✅ COMPLETED (DOCUMENTED)

## GATE-2: READY FOR EXECUTION

---

## 1. LISTA PLIKÓW I ICH ROLE

```
NARRA_FORGE/
├── compose.yaml                    # Docker Compose spec
├── backend/
│   ├── Dockerfile                  # Multi-stage Dockerfile dla API/Worker
│   ├── .dockerignore               # Exclude niepotrzebnych plików
│   ├── .env.example                # Template zmiennych środowiskowych
│   ├── api/
│   │   └── main.py                 # FastAPI app + /health endpoint
│   └── services/
│       └── tasks.py                # Celery app + tasks
├── artifacts/                      # Volume: artefakty produkcji
│   └── .gitkeep
└── logs/                           # Volume: logi aplikacji
    └── .gitkeep
```

---

## 2. SERWISY DOCKER COMPOSE

### compose.yaml — Serwisy

```yaml
services:
  postgres:
    image: postgres:17.2-alpine
    healthcheck: pg_isready -U user -d narra_forge
    volumes: postgres_data:/var/lib/postgresql/data
    profiles: [dev, test]

  redis:
    image: redis:7.4.2-alpine
    healthcheck: redis-cli ping
    volumes: redis_data:/data
    profiles: [dev, test]

  api:
    build: ./backend
    ports: 8000:8000
    depends_on: [postgres (healthy), redis (healthy)]
    healthcheck: curl -f http://localhost:8000/health
    command: uvicorn api.main:app --reload
    profiles: [dev]

  worker:
    build: ./backend
    depends_on: [postgres (healthy), redis (healthy)]
    command: celery -A services.tasks worker --loglevel=info
    profiles: [dev]
```

### Profiles:
- **dev** — Development (api + worker + postgres + redis)
- **test** — Testing (tylko postgres + redis)

### Networks:
- `narra-network` (bridge driver)

### Volumes:
- `postgres_data` — Persistence PostgreSQL
- `redis_data` — Persistence Redis AOF
- `./artifacts` — Artefakty produkcyjne (WorldSpec, FinalPackage, etc.)
- `./logs` — Logi JSON

---

## 3. DOCKERFILE (backend/Dockerfile)

### Multi-stage build:
1. **Base**: Python 3.11.14-slim
2. **Dependencies**: uv sync (production deps)
3. **App**: Copy application code

### Optimalizacje:
- Layer caching (pyproject.toml przed kodem)
- .dockerignore (exclude .venv, .git, __pycache__)
- Single RUN dla apt-get (reduce layers)

### Installed system packages:
- `curl` — healthcheck
- `build-essential` — compilation
- `libpq-dev` — PostgreSQL driver

---

## 4. FASTAPI ENDPOINTS (api/main.py)

### GET /health
```json
{
  "status": "healthy",
  "app_name": "NARRA_FORGE",
  "version": "0.1.0",
  "environment": "development"
}
```

### GET /
```json
{
  "message": "NARRA FORGE - Literary Production Platform",
  "version": "0.1.0",
  "docs": "/docs"
}
```

---

## 5. CELERY TASKS (services/tasks.py)

### Configuration:
- Broker: Redis (DB 1)
- Backend: Redis (DB 2)
- Serializer: JSON
- Timezone: UTC
- Task time limit: 1 hour (soft: 55min)

### Tasks:
- `tasks.health_check` — Health check dla worker

---

## 6. ZMIENNE ŚRODOWISKOWE (.env.example)

```bash
# Application
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/narra_forge

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# OpenAI
OPENAI_API_KEY=your-key-here

# Model Policy
MODEL_MINI=gpt-4o-mini
MODEL_HIGH=gpt-4o

# Token Budgets
TOKEN_BUDGET_PER_SEGMENT=2000
TOKEN_BUDGET_PER_JOB_DEFAULT=50000
```

---

## 7. KOMENDY DOCKER

### Uruchomienie (profil dev):
```bash
docker compose --profile dev up -d
```

### Sprawdzenie statusu:
```bash
docker compose ps
```

Oczekiwane:
```
NAME                     STATUS         HEALTH
narra-forge-postgres     Up (healthy)   healthy
narra-forge-redis        Up (healthy)   healthy
narra-forge-api          Up (healthy)   healthy
narra-forge-worker       Up             -
```

### Health check API:
```bash
curl http://localhost:8000/health
```

Oczekiwane:
```json
{"status":"healthy","app_name":"NARRA_FORGE","version":"0.1.0","environment":"development"}
```

### Logi:
```bash
docker compose logs -f api
docker compose logs -f worker
```

### Zatrzymanie:
```bash
docker compose down
```

### Zatrzymanie + usunięcie volumes:
```bash
docker compose down -v
```

---

## 8. HEALTHCHECKS

### PostgreSQL:
```bash
pg_isready -U user -d narra_forge
interval: 10s, timeout: 5s, retries: 5
```

### Redis:
```bash
redis-cli ping
interval: 10s, timeout: 3s, retries: 5
```

### API:
```bash
curl -f http://localhost:8000/health
interval: 30s, timeout: 10s, retries: 3, start_period: 40s
```

---

## 9. VOLUMES MAPPING

| Host                  | Container       | Purpose                          |
|-----------------------|-----------------|----------------------------------|
| `./backend`           | `/app`          | Hot reload (development)         |
| `./artifacts`         | `/artifacts`    | FinalPackage, WorldSpec, etc.    |
| `./logs`              | `/logs`         | JSON logs                        |
| `postgres_data` (vol) | `/var/lib/...`  | PostgreSQL persistence           |
| `redis_data` (vol)    | `/data`         | Redis AOF persistence            |

---

## 10. NASTĘPNE KROKI

✅ **KROK 1**: Fundament Repo + Jakość Kodu — **COMPLETED**
✅ **KROK 2**: Docker-First Dev Environment — **COMPLETED**
⏭️ **KROK 3**: Model Danych + Migracje (PostgreSQL 17) — **PENDING**

---

## RAPORT GATE-2

```
GATE-2: READY FOR EXECUTION ✅

✓ compose.yaml utworzony (Compose Spec)
✓ Dockerfile utworzony (multi-stage, optimized)
✓ Serwisy: api, worker, postgres, redis
✓ Healthchecki: PostgreSQL, Redis, API
✓ Profiles: dev, test
✓ Volumes: postgres_data, redis_data, artifacts, logs
✓ FastAPI endpoint /health
✓ Celery app + tasks placeholder
✓ .env.example
✓ .dockerignore

UWAGA: Docker nie jest dostępny w środowisku buildowym.
Weryfikacja manualna wymagana w środowisku z Dockerem:
  1. docker compose --profile dev up -d
  2. docker compose ps  # wszystkie HEALTHY
  3. curl http://localhost:8000/health  # 200 OK

Gotowe do KROK 3: Model Danych + Migracje (PostgreSQL 17)
```
