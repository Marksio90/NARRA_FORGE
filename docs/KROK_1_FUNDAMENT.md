# KROK 1 — Fundament Repo + Jakość Kodu

## STATUS: ✅ COMPLETED

## GATE-1: PASS

### Wyniki testów:
- ✅ `uv run pytest` — **PASS** (10/10 testów, coverage 57%)
- ✅ `ruff check .` — **PASS** (All checks passed!)
- ✅ `mypy .` — **PASS** (Success: no issues found in 14 source files)

---

## 1. LISTA PLIKÓW I ICH ROLE

```
NARRA_FORGE/
├── backend/
│   ├── agents/          # Agenci produkcyjni (11 typów)
│   │   └── __init__.py
│   ├── models/          # Modele danych (Pydantic schemas)
│   │   └── __init__.py
│   ├── services/        # Serwisy biznesowe
│   │   └── __init__.py
│   ├── api/             # FastAPI endpoints
│   │   └── __init__.py
│   ├── core/            # Konfiguracja, logging, exceptions
│   │   ├── __init__.py
│   │   ├── config.py         # Settings (Pydantic Settings)
│   │   ├── logging.py        # JSON logging
│   │   └── exceptions.py     # Custom exceptions
│   ├── tests/           # Testy
│   │   ├── unit/        # Testy jednostkowe
│   │   │   ├── test_config.py
│   │   │   └── test_exceptions.py
│   │   └── integration/ # Testy integracyjne
│   ├── pyproject.toml   # Konfiguracja projektu (uv, ruff, mypy, pytest)
│   └── main.py          # Entry point
├── ui/                  # Next.js UI (KROK 14)
├── infra/               # Docker, deployment
├── docs/                # Dokumentacja
│   └── KROK_1_FUNDAMENT.md
├── .pre-commit-config.yaml
└── .gitignore
```

---

## 2. SCHEMATY DANYCH

### core/config.py (Pydantic Settings)

```python
class Settings(BaseSettings):
    # Application
    app_name: str = "NARRA_FORGE"
    environment: str = "development|production|test"

    # Database
    database_url: str
    database_pool_size: int = 5

    # Redis & Celery
    redis_url: str
    celery_broker_url: str

    # OpenAI
    openai_api_key: str

    # Model Policy
    model_mini: str = "gpt-4o-mini"  # Struktury, QA, walidacja
    model_high: str = "gpt-4o"       # Proza, stylizacja, redakcja

    # Token Budgets
    token_budget_per_segment: int = 2000
    token_budget_per_job_default: int = 50000
```

### core/exceptions.py

Hierarchia wyjątków:
- `NarraForgeException` (base)
  - `ValidationError` — błąd walidacji Pydantic
  - `QAGateError` — bramka jakości nie przeszła
  - `ModelPolicyError` — naruszenie polityki modeli
  - `TokenBudgetExceededError` — przekroczenie budżetu tokenów
  - `WorldRuleViolationError` — złamanie reguł świata

---

## 3. TESTY

### tests/unit/test_config.py
- `test_settings_default_values()` — domyślne wartości
- `test_settings_model_validation()` — walidacja environment
- `test_model_policy()` — polityka modeli (mini/high)
- `test_token_budgets()` — budżety tokenów

### tests/unit/test_exceptions.py
- Testy dla każdego typu wyjątku
- Weryfikacja hierarchii dziedziczenia

---

## 4. KONFIGURACJA JAKOŚCI KODU

### pyproject.toml — [tool.ruff]
```toml
line-length = 100
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501", "B008"]
```

### pyproject.toml — [tool.mypy]
```toml
strict = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]
```

### pyproject.toml — [tool.pytest.ini_options]
```toml
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = ["--strict-markers", "--cov=."]
```

---

## 5. ZALEŻNOŚCI (pyproject.toml)

### Runtime:
- `fastapi>=0.115.0` — ASGI framework
- `pydantic>=2.10.0` — Data validation
- `sqlalchemy>=2.0.36` — ORM
- `alembic>=1.14.0` — Migracje DB
- `asyncpg>=0.30.0` — PostgreSQL async driver
- `redis>=5.2.0` — Cache & messaging
- `celery>=5.4.0` — Task queue
- `openai>=1.59.0` — OpenAI API
- `pgvector>=0.3.6` — Semantic search (PostgreSQL extension)
- `opentelemetry-*` — Observability
- `python-json-logger>=3.2.1` — JSON logging

### Dev:
- `pytest>=8.3.0` — Testing framework
- `pytest-asyncio>=0.25.0` — Async tests
- `pytest-cov>=6.0.0` — Coverage
- `ruff>=0.9.0` — Linter & formatter
- `mypy>=1.14.0` — Type checker
- `pre-commit>=4.0.0` — Git hooks
- `httpx>=0.28.1` — HTTP client (for testing)

---

## 6. PRE-COMMIT HOOKS

`.pre-commit-config.yaml`:
- **pre-commit-hooks**: trailing-whitespace, end-of-file-fixer, check-yaml, check-json
- **ruff**: lint + format (auto-fix)
- **mypy**: strict type checking

---

## 7. LOGGING (JSON)

`core/logging.py` — CustomJsonFormatter:
- Output: JSON na stdout
- Fields: `timestamp`, `level`, `app_name`, `app_version`, `environment`, `message`
- Integracja z OpenTelemetry (KROK 13)

Przykład logu:
```json
{
  "timestamp": "2026-01-19T10:00:00",
  "level": "INFO",
  "app_name": "NARRA_FORGE",
  "app_version": "0.1.0",
  "environment": "production",
  "message": "Job started: job_id=123"
}
```

---

## 8. NASTĘPNE KROKI

✅ **KROK 1**: Fundament Repo + Jakość Kodu — **COMPLETED**
⏭️ **KROK 2**: Docker-First Dev Environment — **PENDING**

---

## RAPORT GATE-1

```
GATE-1: PASS ✅

✓ Wszystkie testy przeszły (10/10)
✓ Ruff check: All checks passed!
✓ Mypy: Success: no issues found
✓ Pre-commit hooks zainstalowane
✓ Struktura katalogów utworzona
✓ Konfiguracja (Settings) działająca
✓ JSON logging skonfigurowany
✓ Custom exceptions zdefiniowane

Gotowe do KROK 2: Docker-First Dev Environment
```
