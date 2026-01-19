# KROK 3 — Model Danych + Migracje (PostgreSQL 17)

## STATUS: ✅ COMPLETED (DOCUMENTED)

## GATE-3: READY FOR EXECUTION

---

## 1. LISTA PLIKÓW I ICH ROLE

```
backend/
├── models/
│   ├── database.py                 # Database engine, session maker, Base
│   └── schema.py                   # SQLAlchemy models
├── migrations/
│   ├── env.py                      # Alembic environment config
│   ├── versions/
│   │   └── af4b3ea397a4_initial_schema.py  # Initial migration
│   └── README                      # Alembic README
├── alembic.ini                     # Alembic configuration
└── tests/
    └── integration/
        └── test_db.py              # Database integration tests
```

---

## 2. TABELE (SCHEMA)

### jobs — Production Jobs
| Column        | Type          | Description                          |
|---------------|---------------|--------------------------------------|
| id            | UUID (PK)     | Job ID                               |
| type          | String(50)    | short_story, novella, novel, saga    |
| genre         | String(100)   | Genre                                |
| inspiration   | Text          | Optional inspiration                 |
| constraints   | JSON          | Job constraints                      |
| status        | String(50)    | queued, running, completed, failed   |
| created_at    | DateTime      | Creation timestamp                   |
| updated_at    | DateTime      | Last update timestamp                |
| completed_at  | DateTime      | Completion timestamp (nullable)      |

**Indexes:** `status`, `created_at`

---

### artifacts — All Production Artifacts
| Column        | Type          | Description                          |
|---------------|---------------|--------------------------------------|
| id            | UUID (PK)     | Artifact ID                          |
| job_id        | UUID (FK)     | Foreign key to jobs                  |
| type          | String(50)    | world_spec, character_spec, etc.     |
| version       | Integer       | Version number                       |
| data          | JSON          | Artifact data (structured)           |
| checksum      | String(64)    | SHA-256 checksum                     |
| created_at    | DateTime      | Creation timestamp                   |

**Foreign Key:** `job_id → jobs.id` (CASCADE DELETE)
**Index:** `job_id`

---

### worlds — IP-Level World Specifications
| Column        | Type          | Description                          |
|---------------|---------------|--------------------------------------|
| id            | UUID (PK)     | World ID                             |
| name          | String(200)   | World name (UNIQUE)                  |
| rules         | JSON          | List of world rules                  |
| geography     | JSON          | Geography data                       |
| history       | JSON          | Timeline nodes                       |
| themes        | JSON          | List of themes                       |
| version       | Integer       | Version number                       |
| checksum      | String(64)    | SHA-256 checksum                     |
| created_at    | DateTime      | Creation timestamp                   |
| updated_at    | DateTime      | Last update timestamp                |

**Constraint:** `name` is UNIQUE

---

### characters — Character Trajectories
| Column        | Type          | Description                          |
|---------------|---------------|--------------------------------------|
| id            | UUID (PK)     | Character ID                         |
| world_id      | UUID (FK)     | Foreign key to worlds                |
| name          | String(200)   | Character name                       |
| trajectory    | JSON          | List of transformation nodes         |
| relationships | JSON          | List of relationships                |
| constraints   | JSON          | Psychological constraints            |
| created_at    | DateTime      | Creation timestamp                   |
| updated_at    | DateTime      | Last update timestamp                |

**Foreign Key:** `world_id → worlds.id` (CASCADE DELETE)
**Index:** `world_id`

---

### timelines — Event Timelines
| Column        | Type          | Description                          |
|---------------|---------------|--------------------------------------|
| id            | UUID (PK)     | Timeline ID                          |
| world_id      | UUID (FK)     | Foreign key to worlds                |
| nodes         | JSON          | List of timeline event nodes         |
| created_at    | DateTime      | Creation timestamp                   |
| updated_at    | DateTime      | Last update timestamp                |

**Foreign Key:** `world_id → worlds.id` (CASCADE DELETE)
**Index:** `world_id`

---

### qa_reports — Quality Gate Reports
| Column            | Type          | Description                      |
|-------------------|---------------|----------------------------------|
| id                | UUID (PK)     | Report ID                        |
| job_id            | UUID (FK)     | Foreign key to jobs              |
| logic_score       | Float         | Logic score (0.0 - 1.0)          |
| psychology_score  | Float         | Psychology score (0.0 - 1.0)     |
| timeline_score    | Float         | Timeline score (0.0 - 1.0)       |
| critical_errors   | JSON          | List of critical errors          |
| warnings          | JSON          | List of warnings                 |
| passed            | Boolean       | QA gate passed?                  |
| created_at        | DateTime      | Creation timestamp               |

**Foreign Key:** `job_id → jobs.id` (CASCADE DELETE)
**Index:** `job_id`

---

### cost_snapshots — Cost Tracking per Stage
| Column        | Type          | Description                          |
|---------------|---------------|--------------------------------------|
| id            | UUID (PK)     | Snapshot ID                          |
| job_id        | UUID (FK)     | Foreign key to jobs                  |
| stage         | String(100)   | Stage name (e.g., "world_architect") |
| tokens_used   | Integer       | Tokens consumed                      |
| cost_usd      | Float         | Cost in USD                          |
| model         | String(50)    | Model used (gpt-4o-mini, gpt-4o)     |
| created_at    | DateTime      | Creation timestamp                   |

**Foreign Key:** `job_id → jobs.id` (CASCADE DELETE)
**Index:** `job_id`

---

## 3. MIGRACJE (Alembic)

### Konfiguracja Alembic (alembic.ini):
- **script_location**: `migrations/`
- **sqlalchemy.url**: Dynamicznie ustawiane z `core.config.settings.database_url`

### Migracja początkowa (af4b3ea397a4_initial_schema.py):
- **Upgrade**: Tworzy wszystkie tabele + indexy
- **Downgrade**: Usuwa wszystkie tabele

### Komenda uruchomienia migracji:
```bash
uv run alembic upgrade head
```

### Komenda sprawdzenia statusu:
```bash
uv run alembic current
```

### Komenda rollback:
```bash
uv run alembic downgrade -1
```

---

## 4. SQLALCHEMY MODELE (models/schema.py)

### Hierarchia klas:
```python
Base (declarative_base)
├── Job
│   ├── artifacts (relationship → Artifact)
│   ├── qa_reports (relationship → QAReport)
│   └── cost_snapshots (relationship → CostSnapshot)
├── Artifact
│   └── job (relationship → Job)
├── World
│   ├── characters (relationship → Character)
│   └── timelines (relationship → Timeline)
├── Character
│   └── world (relationship → World)
├── Timeline
│   └── world (relationship → World)
├── QAReport
│   └── job (relationship → Job)
└── CostSnapshot
    └── job (relationship → Job)
```

### Cascade Deletes:
- Usunięcie `Job` → usuwa wszystkie `Artifacts`, `QAReports`, `CostSnapshots`
- Usunięcie `World` → usuwa wszystkie `Characters`, `Timelines`

---

## 5. DATABASE SESSION (models/database.py)

### Async Engine:
```python
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
)
```

### Async Session Factory:
```python
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### Dependency Injection (FastAPI):
```python
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

## 6. TESTS (tests/integration/test_db.py)

### Test Cases:
1. **test_database_connection** — Test połączenia z bazą
2. **test_tables_exist** — Test istnienia tabel (jobs, artifacts, worlds)
3. **test_alembic_version** — Test istnienia tabeli `alembic_version`

### Komenda uruchomienia testów:
```bash
uv run pytest tests/integration/test_db.py -v
```

**UWAGA:** Testy wymagają działającej bazy PostgreSQL (Docker Compose).

---

## 7. KOMENDY DOCKER

### Uruchomienie PostgreSQL:
```bash
docker compose --profile dev up postgres -d
```

### Sprawdzenie statusu:
```bash
docker compose ps
```

### Połączenie z bazą (psql):
```bash
docker compose exec postgres psql -U user -d narra_forge
```

### Lista tabel (\dt):
```sql
\dt
```

Oczekiwane tabele:
```
 public | alembic_version  | table
 public | artifacts        | table
 public | characters       | table
 public | cost_snapshots   | table
 public | jobs             | table
 public | qa_reports       | table
 public | timelines        | table
 public | worlds           | table
```

---

## 8. NASTĘPNE KROKI

✅ **KROK 1**: Fundament Repo + Jakość Kodu — **COMPLETED**
✅ **KROK 2**: Docker-First Dev Environment — **COMPLETED**
✅ **KROK 3**: Model Danych + Migracje (PostgreSQL 17) — **COMPLETED**
⏭️ **KROK 4**: Pamięć Semantyczna (pgvector) — **PENDING**

---

## RAPORT GATE-3

```
GATE-3: READY FOR EXECUTION ✅

✓ models/database.py: async engine, session maker, Base
✓ models/schema.py: 7 tabel (Job, Artifact, World, Character, Timeline, QAReport, CostSnapshot)
✓ Alembic zainicjalizowany
✓ Migracja początkowa: af4b3ea397a4_initial_schema.py
✓ migrations/env.py: async migrations + Base metadata
✓ tests/integration/test_db.py: 3 testy

UWAGA: PostgreSQL nie jest dostępny w środowisku buildowym.
Weryfikacja manualna wymagana:
  1. docker compose --profile dev up postgres -d
  2. uv run alembic upgrade head
  3. docker compose exec postgres psql -U user -d narra_forge -c "\dt"
  4. uv run pytest tests/integration/test_db.py -v

Gotowe do KROK 4: Pamięć Semantyczna (pgvector)
```
