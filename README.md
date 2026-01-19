# NARRA_FORGE 📚✨

**Autonomiczna Platforma Produkcji Literackiej**

Wieloagentowy system AI do automatycznej tworzenia treści literackich z kontrolą jakości, kosztów i pełną obserwowalnością.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/next.js-16-black.svg)](https://nextjs.org/)
[![Tests](https://img.shields.io/badge/tests-264%20passing-success.svg)](backend/tests/)
[![Coverage](https://img.shields.io/badge/coverage-96%25-success.svg)](backend/tests/)

## 🎯 Funkcjonalności

- **7 Wyspecjalizowanych Agentów AI**: Interpreter, WorldArchitect, CharacterArchitect, PlotCreator, ProseGenerator, QAAgent, StylePolish
- **Pipeline 9 Etapów**: Od interpretacji do finalnego pakowania
- **Kontrola Jakości**: Automatyczna walidacja logiki, psychologii postaci i spójności fabularnej
- **Śledzenie Kosztów**: Real-time monitoring kosztów OpenAI API z budżetami i alertami
- **Observability**: Traces, metrics, events dla pełnej widoczności pipeline'u
- **Production UI**: Next.js 16 z real-time monitoring i wizualizacją pipeline'u
- **Packaging**: Export do JSON, Markdown i Audio Manifest (TTS/audiobook)

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                      Next.js 16 UI                          │
│              http://localhost:3000                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   FastAPI Backend                           │
│              http://localhost:8000                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Pipeline Orchestrator (9 Stages)                    │  │
│  │  ┌───────┐ ┌────────┐ ┌──────┐ ┌───────┐ ┌──────┐  │  │
│  │  │ INTER │→│ WORLD  │→│ CHAR │→│ PLOT  │→│PROSE │  │  │
│  │  │ PRET  │ │ARCHITECT│ │ARCHI │ │CREATE │ │ GEN  │  │  │
│  │  └───────┘ └────────┘ └──────┘ └───────┘ └──────┘  │  │
│  │                    ↓                                 │  │
│  │  ┌───────┐ ┌──────┐ ┌──────┐ ┌────────┐            │  │
│  │  │ STYLE │→│  QA  │→│DIALOG│→│PACKAGE │            │  │
│  │  │POLISH │ │      │ │      │ │        │            │  │
│  │  └───────┘ └──────┘ └──────┘ └────────┘            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────┬───────────────────┬──────────────────────────┘
              │                   │
    ┌─────────▼────────┐  ┌──────▼──────┐
    │  PostgreSQL 17   │  │   Redis 7   │
    │   + pgvector     │  │ + Celery    │
    └──────────────────┘  └─────────────┘
              │
    ┌─────────▼────────┐
    │  OpenAI API      │
    │  gpt-4o / mini   │
    └──────────────────┘
```

## 🚀 Quick Start (Docker)

### Wymagania

- Docker 20.10+
- Docker Compose 2.0+
- OpenAI API key

### 1. Konfiguracja

```bash
# Clone repository
git clone https://github.com/Marksio90/NARRA_FORGE.git
cd NARRA_FORGE

# Create environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
# Set: OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. Uruchomienie

```bash
# Start wszystkich serwisów (PostgreSQL, Redis, API, Worker, UI)
./docker-dev.sh start

# Sprawdź status
./docker-dev.sh health
```

### 3. Dostęp do Serwisów

- **UI (Frontend)**: http://localhost:3000
- **API (Backend)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Tworzenie Pierwszego Zlecenia

1. Otwórz http://localhost:3000
2. Kliknij "Utwórz Nowe Zlecenie"
3. Wypełnij formularz:
   - Typ: Short Story
   - Gatunek: Fantasy
   - Inspiracja: "Opowiadanie o czarodzieju..."
   - Liczba słów: 2000
   - Budżet: $5.00
4. Kliknij "Utwórz Zlecenie"
5. Obserwuj progress w czasie rzeczywistym!

## 📦 Komponenty

### Backend (Python 3.11)

```bash
cd backend/

# Setup
uv sync

# Run tests
uv run pytest tests/unit/ -v

# Run API
uv run uvicorn api.main:app --reload
```

Zobacz: [backend/README.md](backend/README.md)

### Frontend (Next.js 16)

```bash
cd ui/

# Setup
npm install

# Development
npm run dev

# Build
npm run build
```

Zobacz: [ui/README.md](ui/README.md)

## 🔧 Development

### Backend Development

```bash
# Uruchom PostgreSQL i Redis
docker compose --profile dev up postgres redis -d

# Uruchom API lokalnie
cd backend
uv run uvicorn api.main:app --reload

# Uruchom Celery worker
uv run celery -A services.tasks worker --loglevel=info

# Uruchom testy
uv run pytest tests/unit/ -v

# Type checking
uv run mypy .

# Linting
uv run ruff check .
```

### Frontend Development

```bash
# Uruchom backend w Docker
docker compose --profile dev up postgres redis api worker -d

# Uruchom UI lokalnie
cd ui
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🧪 Testing

### Backend Tests (264 tests, 96% coverage)

```bash
# All tests
uv run pytest tests/unit/ -v

# Specific test file
uv run pytest tests/unit/test_agent_prose_generator.py -v

# With coverage
uv run pytest tests/unit/ --cov=. --cov-report=html

# View coverage
open htmlcov/index.html
```

### Test Breakdown

- **Agents**: 62 tests (Interpreter, WorldArchitect, CharacterArchitect, PlotCreator, ProseGenerator, QAAgent, StylePolish)
- **Model Policy**: 15 tests
- **OpenAI Client**: 15 tests
- **Schemas**: 54 tests (Domain, Agent, Job, Base)
- **Tasks**: 17 tests (Agent tasks, Job tasks, Celery)
- **Packaging**: 18 tests
- **Observability**: 21 tests
- **Utilities**: 62 tests (Token counter, embeddings, exceptions, config)

## 📊 Pipeline Stages

1. **STRUCTURE** (gpt-4o-mini, 0.3, 2000 tokens) - Interpretacja user inspiration
2. **PLAN** (gpt-4o-mini, 0.3, 3000 tokens) - Planowanie struktury
3. **WORLD** (gpt-4o, 0.5, 5000 tokens) - World building
4. **CHARACTER_PROFILE** (gpt-4o, 0.5, 4000 tokens) - Tworzenie postaci
5. **PROSE** (gpt-4o, 0.8, 10000 tokens) - Generowanie prozy
6. **STYLE** (gpt-4o, 0.8, 2500 tokens) - Stylizacja polska
7. **QA** (gpt-4o-mini, 0.3, 3000 tokens) - Quality assurance
8. **DIALOG** (gpt-4o, 0.8, 5000 tokens) - Dialogi
9. **PACKAGE** (local, N/A, N/A) - Pakowanie

## 🎨 AI Agents

### 1. **InterpreterAgent**
- Model: gpt-4o-mini
- Role: Interpretacja user inspiration
- Output: Tematy, gatunek, ton, długość

### 2. **WorldArchitectAgent**
- Model: gpt-4o
- Role: World building i reguły świata
- Output: Geografia, historia, zasady magii/technologii

### 3. **CharacterArchitectAgent**
- Model: gpt-4o
- Role: Tworzenie charakterów postaci
- Output: Motywacje, trajektorie, relacje

### 4. **PlotCreatorAgent**
- Model: gpt-4o
- Role: Struktura fabularna i sceny
- Output: Akty, sceny, punkty zwrotne

### 5. **ProseGeneratorAgent**
- Model: gpt-4o (temp 0.8)
- Role: Generowanie prozy narracyjnej
- Output: Tekst literacki (~2000 słów/segment)

### 6. **QAAgent**
- Model: gpt-4o-mini
- Role: Walidacja jakości
- Output: Scores (logic, psychology, timeline) + errors

### 7. **StylePolishAgent**
- Model: gpt-4o (temp 0.8)
- Role: Redakcja polska (3 poziomy: light/standard/intensive)
- Output: Wypolerowana proza + scores

## 💰 Cost Management

- **Budget Limits**: Konfigurowalne per job ($1-$100)
- **Real-time Tracking**: Śledzenie kosztów per agent/model
- **Token Budgets**: Limity per stage (2000-10000 tokens)
- **Cost Snapshots**: Historia kosztów z timestamps
- **Budget Exceeded Alerts**: Automatyczne zatrzymanie

## 📈 Observability

- **Traces**: Timing każdego agent call
- **Metrics**: Cost, tokens, QA scores
- **Events**: Pipeline stage transitions
- **Statistics**: Count, avg, min, max aggregations
- **Job Context**: Thread-safe tracking z contextvars

## 🗄️ Database Schema

### Core Tables

- `jobs` - Job configuration and status
- `artifacts` - World specs, character specs, prose segments, QA reports
- `cost_snapshots` - Cost tracking per agent call
- `pipeline_stages` - Stage execution history

## 🔐 Security

- **Environment Variables**: Secrets w .env
- **Database**: PostgreSQL z asyncpg
- **API**: CORS configuration
- **Docker**: Non-root users
- **Input Validation**: Pydantic schemas

## 📚 Documentation

- [DOCKER.md](DOCKER.md) - Complete Docker guide
- [backend/README.md](backend/README.md) - Backend details
- [ui/README.md](ui/README.md) - Frontend details
- [API Docs](http://localhost:8000/docs) - Interactive API documentation

## 🛠️ Tech Stack

### Backend
- **Python 3.11** - Core language
- **FastAPI** - Modern web framework
- **PostgreSQL 17** - Relational database + pgvector
- **Redis 7** - Message broker & cache
- **Celery** - Distributed task queue
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic v2** - Data validation
- **OpenAI API** - AI models (gpt-4o, gpt-4o-mini)

### Frontend
- **Next.js 16** - React framework
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **date-fns** - Date formatting

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **uv** - Python package manager
- **pytest** - Testing framework
- **ruff** - Python linter
- **mypy** - Static type checker

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Make changes and add tests
4. Run tests (`uv run pytest tests/unit/ -v`)
5. Run linters (`uv run ruff check .` && `uv run mypy .`)
6. Commit (`git commit -m 'Add amazing feature'`)
7. Push (`git push origin feature/amazing`)
8. Open Pull Request

## 📝 License

Part of the NARRA_FORGE project.

## 🙏 Acknowledgments

- OpenAI API for GPT-4o and GPT-4o-mini models
- FastAPI framework
- Next.js framework
- PostgreSQL and pgvector
- Celery distributed task queue

## 📧 Support

For issues and questions:
- GitHub Issues: https://github.com/Marksio90/NARRA_FORGE/issues
- Documentation: See DOCKER.md and component READMEs

---

**Made with ❤️ for autonomous literary production**
