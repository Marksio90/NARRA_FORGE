# 📚 NarraForge - Autonomiczna Kuźnia Literacka

Multi-agentowa platforma do autonomicznego tworzenia pełnometrażowych książek z wykorzystaniem OpenAI API i inteligentnego skalowania modeli.

![Version](https://img.shields.io/badge/version-1.0.0--MVP-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Czym jest NarraForge?

NarraForge to zaawansowana platforma AI, która autonomicznie tworzy kompletne książki na poziomie bestsellerowym. System orkiestruje zespół wyspecjalizowanych agentów AI przy użyciu LangGraph i LangChain, z których każdy odpowiada za konkretny aspekt procesu twórczego.

### Kluczowe Funkcje MVP

✨ **Multi-agentowy system AI** - 4 wyspecjalizowane agenty (Orchestrator, World Architect, Character Smith, Plot Master)
🎭 **3 gatunki literackie** - Fantasy, Sci-Fi, Thriller
🤖 **Inteligentne skalowanie modeli** - GPT-4o-mini dla prostych zadań, GPT-4o dla złożonych
📊 **Real-time progress tracking** - WebSocket updates w czasie rzeczywistym
💰 **Cost tracking** - Precyzyjne śledzenie kosztów na każdym etapie
📤 **Export** - Markdown i JSON (EPUB/PDF w kolejnych wersjach)
🐳 **Docker Compose** - Łatwe uruchomienie jedną komendą

## 🏗️ Architektura

### Stack Technologiczny

- **Backend**: FastAPI + Python 3.11
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS
- **AI Orchestration**: LangGraph + LangChain
- **Database**: PostgreSQL 16 + pgvector
- **Cache/Queue**: Redis 7 + Celery
- **AI Engine**: OpenAI API (GPT-4o-mini, GPT-4o)
- **Deploy**: Docker Compose

### Struktura Kontenerów

```
narraforge-postgres    # PostgreSQL + pgvector (port 5432)
narraforge-redis       # Redis cache + broker (port 6379)
narraforge-api         # FastAPI backend (port 8000)
narraforge-worker      # Celery worker (background tasks)
narraforge-ui          # Next.js frontend (port 3000)
```

## 🚀 Szybki Start

### Wymagania

- Docker Engine 24+
- Docker Compose v2
- Min. 8GB RAM
- Min. 20GB disk space
- OpenAI API Key

### Instalacja

1. **Sklonuj repozytorium**
```bash
git clone https://github.com/Marksio90/NARRA_FORGE.git
cd NARRA_FORGE
```

2. **Skonfiguruj zmienne środowiskowe**
```bash
cp .env.example .env
# Edytuj .env i dodaj swój OPENAI_API_KEY
```

3. **Uruchom platformę**
```bash
docker compose up -d
```

4. **Sprawdź status**
```bash
docker compose ps
docker compose logs -f
```

5. **Otwórz interfejs**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/health

## 📖 Jak używać?

### Tworzenie nowej książki przez UI

1. Otwórz http://localhost:3000
2. Kliknij **"New Job"**
3. Wybierz gatunek (Fantasy/Sci-Fi/Thriller)
4. Wpisz inspirację dla historii
5. Ustaw limit budżetu (domyślnie $10)
6. Kliknij **"Generate Book"**
7. Monitoruj postęp w czasie rzeczywistym
8. Po zakończeniu eksportuj do Markdown lub JSON

### Tworzenie książki przez API

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "genre": "fantasy",
    "inspiration": "A young mage discovers an ancient prophecy",
    "budget_limit": 10.0
  }'
```

## 🤖 System Agentów

### MVP Agents

| Agent | Rola | Model |
|-------|------|-------|
| **Orchestrator** | Koordynacja pipeline'u (LangGraph) | GPT-4o-mini |
| **World_Architect** | Budowanie świata i zasad | GPT-4o |
| **Character_Smith** | Tworzenie postaci i ich arców | GPT-4o |
| **Plot_Master** | Projektowanie struktury fabularnej | GPT-4o |
| **Prose_Weaver** | Generowanie finalnej prozy | GPT-4o |

### Pipeline Generacji (8 etapów MVP)

1. **Inicjalizacja** - Utworzenie projektu
2. **World Building** - Generowanie świata
3. **Character Creation** - Tworzenie postaci głównych
4. **Plot Structure** - Projektowanie fabuły
5. **Scene Planning** - Planowanie scen
6. **Prose Generation** - Pisanie rozdziałów
7. **Cost Tracking** - Śledzenie kosztów
8. **Export** - Finalizacja i eksport

## 📊 API Endpoints

### Jobs

- `POST /api/jobs` - Utwórz nowy job
- `GET /api/jobs` - Lista wszystkich jobów
- `GET /api/jobs/{id}` - Szczegóły joba
- `GET /api/jobs/{id}/export/{format}` - Eksport (markdown/json)

### WebSocket

- `WS /ws/jobs/{id}` - Real-time progress updates

## 🧪 Development

### Uruchomienie testów

```bash
docker compose exec api pytest
```

### Logi

```bash
# Wszystkie serwisy
docker compose logs -f

# Konkretny serwis
docker compose logs -f api
docker compose logs -f worker
```

### Restart serwisu

```bash
docker compose restart api
docker compose restart worker
```

## 💰 Koszty OpenAI

### Pricing (styczeń 2026)

- **GPT-4o-mini**: $0.150 / $0.600 per 1M tokens (input/output)
- **GPT-4o**: $2.50 / $10.00 per 1M tokens (input/output)

### Szacowane koszty

- **Short story (2000 słów)**: ~$1-2 USD
- **Novella (20000 słów)**: ~$5-10 USD
- **Novel (80000 słów)**: ~$20-40 USD

## 🗺️ Roadmap

### ✅ MVP (Current)

- [x] 4 core agents (Orchestrator, World, Character, Plot)
- [x] LangGraph orchestration
- [x] 3 genres (Fantasy, Sci-Fi, Thriller)
- [x] WebSocket progress tracking
- [x] Markdown/JSON export
- [x] Cost tracking

### 🔜 v2 (Planowane)

- [ ] Continuity_Guardian z RAG (pgvector)
- [ ] Style_Master + Genre_Expert agents
- [ ] 15-etapowy pełny pipeline
- [ ] Wszystkie 8 gatunków
- [ ] EPUB + DOCX export
- [ ] Retry failed stages

### 🔮 v3 (Przyszłość)

- [ ] PDF export
- [ ] GPT-4 dla premium jobs
- [ ] Multi-user + authentication
- [ ] Job templates
- [ ] Analytics dashboard

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines first.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- OpenAI for GPT models
- LangChain/LangGraph for orchestration framework
- FastAPI for amazing Python web framework
- Next.js team for incredible React framework

---

**Built with ❤️ using Claude Code**

*NarraForge - Where AI Becomes Author*
