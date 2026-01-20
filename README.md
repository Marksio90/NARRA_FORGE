# 🔥 NarraForge - Kuźnia Bestsellerów AI

**Kompleksowa platforma multi-agentowa do autonomicznego generowania pełnometrażowych książek**

NarraForge to rewolucyjna platforma, która zamienia prosty wybór gatunku w pełnowymiarową, profesjonalną książkę na poziomie światowych bestsellerów. Użytkownik wybiera **TYLKO gatunek** - wszystko inne jest autonomicznie generowane przez orkiestrę wyspecjalizowanych agentów AI.

## ✨ Kluczowe Funkcje

- **🤖 Multi-Agentowa Architektura**: 7 wyspecjalizowanych agentów AI (World, Character, Plot, Prose, Consistency, Director, Publisher)
- **💰 Inteligentne Skalowanie Kosztów**: Automatyczny wybór modelu OpenAI (mini/standard/advanced/premium) w zależności od złożoności zadania
- **📊 Live Progress Updates**: Real-time WebSocket updates z postępem generowania
- **🔗 Strażnik Spójności**: Eliminacja halucynacji i zapewnienie spójności fabularnej
- **📚 Eksport do Wielu Formatów**: DOCX, PDF, EPUB, TXT, Markdown
- **🔄 Kontynuacja Serii**: Automatyczny import świata i postaci do następnego tomu
- **🐳 Pełna Dockeryzacja**: Łatwe uruchomienie z Docker Compose

## 📋 Wymagania

- Docker & Docker Compose
- OpenAI API Key
- 8GB RAM (minimum)
- 20GB wolnego miejsca na dysku

## 🚀 Szybki Start

### 1. Klonowanie Repozytorium

```bash
git clone https://github.com/YOUR_USERNAME/NARRA_FORGE.git
cd NARRA_FORGE
```

### 2. Konfiguracja

Skopiuj przykładowy plik konfiguracji i ustaw swój klucz API:

```bash
cp .env.example .env
# Edytuj .env i ustaw OPENAI_API_KEY
```

### 3. Uruchomienie

```bash
make dev
```

To uruchomi:
- **Backend** (FastAPI) na http://localhost:8000
- **Frontend** (Next.js) na http://localhost:3000
- **PostgreSQL** z pgvector na porcie 5432
- **Redis** na porcie 6379

### 4. Generowanie Pierwszej Książki

1. Otwórz http://localhost:3000
2. Wybierz gatunek (np. Science Fiction)
3. Kliknij "🔥 Rozpal Kuźnię"
4. Obserwuj live progress generowania!

## 🏗️ Architektura

### Agenci AI

```
┌─────────────────────┐
│  🎭 MAIN ORCHESTRATOR │
│   (Reżyser Główny)    │
└──────────┬──────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    │             │          │          │
    ▼             ▼          ▼          ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ 🌍 WORLD│  │ 👥 CHAR │  │ 📖 PLOT │  │ ✍️ PROSE│
│  AGENT  │  │  AGENT  │  │  AGENT  │  │  AGENT  │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
```

### Stack Technologiczny

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL 16 + pgvector
- Redis
- OpenAI API
- SQLAlchemy + Alembic

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- WebSocket

## 📁 Struktura Projektu

```
narraforge/
├── 📁 docker/              # Docker configuration
├── 📁 backend/             # FastAPI backend
│   └── 📁 app/
│       ├── agents/         # AI Agents
│       ├── core/           # Core services
│       ├── models/         # Database models
│       ├── api/            # API routes
│       └── services/       # Business logic
├── 📁 frontend/            # Next.js frontend
├── 📁 outputs/             # Generated books
└── 📁 data/                # PostgreSQL data
```

## 🎨 Wspierane Gatunki

| Gatunek | Ikona | Typowa Długość | Złożoność |
|---------|-------|----------------|-----------|
| Science Fiction | 🚀 | 80-120k słów | ⭐⭐⭐⭐⭐ |
| Fantasy | 🐉 | 100-150k słów | ⭐⭐⭐⭐⭐ |
| Thriller | 🔪 | 70-90k słów | ⭐⭐⭐⭐ |
| Horror | 👻 | 60-80k słów | ⭐⭐⭐⭐ |
| Romans | 💕 | 70-100k słów | ⭐⭐⭐ |
| Kryminał | 🔍 | 70-90k słów | ⭐⭐⭐⭐ |

## 💰 System Skalowania Kosztów

NarraForge automatycznie wybiera optymalny model OpenAI dla każdego zadania:

- **MINI** (gpt-4o-mini): Formatowanie, metadane
- **STANDARD** (gpt-4o): Standardowe rozdziały
- **ADVANCED** (o1): Złożone twisty, filozofia
- **PREMIUM** (o1-pro): Finały, krytyczne naprawy

*Szacunkowy koszt wygenerowania książki: **$2-8***

## 🔧 Komendy

```bash
make dev        # Uruchom środowisko deweloperskie
make build      # Zbuduj wszystkie kontenery
make up         # Uruchom wszystkie usługi
make down       # Zatrzymaj wszystkie usługi
make logs       # Zobacz logi
make test       # Uruchom testy
make clean      # Wyczyść wszystko
```

## 📡 API Endpoints

```bash
GET  /api/v1/genres               # Lista gatunków
POST /api/v1/books/generate       # Rozpocznij generowanie
GET  /api/v1/books/{id}           # Pobierz książkę
GET  /api/v1/books/{id}/progress  # Pobierz postęp
POST /api/v1/books/{id}/export    # Eksportuj książkę
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 Licencja

MIT License

## 📧 Kontakt

- GitHub: [@Marksio90](https://github.com/Marksio90)
- Issues: https://github.com/Marksio90/NARRA_FORGE/issues

---

**🔥 Made with AI, for AI-powered storytelling**
