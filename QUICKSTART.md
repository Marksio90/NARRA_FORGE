# NARRA_FORGE - Quick Start

Szybki przewodnik uruchomienia platformy NARRA_FORGE z Docker Compose.

## 📋 Wymagania

- Docker 20.10+
- Docker Compose 2.0+
- OpenAI API key

## 🚀 Uruchomienie (3 kroki)

### 1. Konfiguracja

```bash
# Clone repo
git clone https://github.com/Marksio90/NARRA_FORGE.git
cd NARRA_FORGE

# Utwórz plik .env
cp .env.example .env

# Edytuj .env i dodaj swój klucz API
nano .env
# Ustaw: OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. Start

```bash
# Uruchom wszystkie serwisy (PostgreSQL, Redis, API, Worker, UI)
docker compose --profile dev up -d

# Zobacz logi
docker compose logs -f
```

### 3. Użytkowanie

Otwórz w przeglądarce:
- **UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 📝 Podstawowe Komendy

### Start/Stop

```bash
# Start wszystkich serwisów
docker compose --profile dev up -d

# Stop wszystkich serwisów
docker compose down

# Restart
docker compose restart
```

### Logi

```bash
# Wszystkie logi
docker compose logs -f

# Logi konkretnego serwisu
docker compose logs -f api
docker compose logs -f ui
docker compose logs -f worker

# Ostatnie 100 linii
docker compose logs --tail=100 api
```

### Status

```bash
# Status wszystkich kontenerów
docker compose ps

# Szczegółowe info
docker compose ps -a
```

### Rebuild

```bash
# Rebuild konkretnego serwisu
docker compose build api
docker compose build ui

# Rebuild i restart
docker compose up --build -d
```

### Wykonywanie Komend

```bash
# Testy backend
docker compose exec api uv run pytest tests/unit/ -v

# Shell w API
docker compose exec api bash

# Shell w UI
docker compose exec ui sh

# PostgreSQL shell
docker compose exec postgres psql -U user -d narra_forge

# Redis CLI
docker compose exec redis redis-cli
```

### Czyszczenie

```bash
# Stop i usuń kontenery
docker compose down

# Stop i usuń volumes (⚠️ usuwa dane!)
docker compose down -v

# Usuń nieużywane obrazy
docker system prune -a
```

## 🔍 Diagnostyka

### Health Checks

```bash
# Sprawdź API
curl http://localhost:8000/health

# Sprawdź UI
curl http://localhost:3000

# Sprawdź database
docker compose exec postgres pg_isready -U user -d narra_forge

# Sprawdź Redis
docker compose exec redis redis-cli ping
```

### Troubleshooting

**Problem: Kontener nie startuje**
```bash
# Zobacz logi błędu
docker compose logs api

# Restart konkretnego serwisu
docker compose restart api
```

**Problem: Brak połączenia z database**
```bash
# Sprawdź czy PostgreSQL działa
docker compose ps postgres

# Zobacz logi database
docker compose logs postgres
```

**Problem: UI nie łączy się z API**
```bash
# Sprawdź health API
curl http://localhost:8000/health

# Sprawdź sieć
docker network inspect narra-forge_narra-network

# Rebuild UI
docker compose build ui
docker compose up -d ui
```

## 📚 Więcej Informacji

- **Szczegółowa dokumentacja**: [DOCKER.md](DOCKER.md)
- **README projektu**: [README.md](README.md)
- **API Documentation**: http://localhost:8000/docs (po uruchomieniu)

## 🎯 Pierwszy Test

Po uruchomieniu:

1. Otwórz http://localhost:3000
2. Kliknij "Utwórz Nowe Zlecenie"
3. Wypełnij formularz:
   - Typ: Short Story
   - Gatunek: Fantasy
   - Inspiracja: "Opowiadanie o czarodzieju który odkrywa zapomniane królestwo"
   - Słowa: 2000
   - Budżet: $5.00
4. Kliknij "Utwórz Zlecenie"
5. Obserwuj progress w real-time!

## 🛠️ Development

### Backend Development

```bash
# Start tylko infrastruktury
docker compose up postgres redis -d

# Pracuj lokalnie (w backend/)
cd backend
uv sync
uv run uvicorn api.main:app --reload
```

### Frontend Development

```bash
# Start backend w Docker
docker compose --profile dev up postgres redis api worker -d

# Pracuj lokalnie (w ui/)
cd ui
npm install
npm run dev
```

## ⚠️ Ważne

- **OpenAI API Key**: Wymagany dla production use
- **Dane**: Przechowywane w Docker volumes (postgres_data, redis_data)
- **Backup**: `docker compose down` zachowuje dane, `docker compose down -v` usuwa wszystko
- **Port conflicts**: Upewnij się że porty 3000, 8000, 5432, 6379 są wolne

## 🆘 Pomoc

Jeśli masz problemy:
1. Sprawdź logi: `docker compose logs -f`
2. Zobacz status: `docker compose ps`
3. Przeczytaj [DOCKER.md](DOCKER.md) dla szczegółów
4. GitHub Issues: https://github.com/Marksio90/NARRA_FORGE/issues

---

**Wszystko działa ze standardowymi komendami `docker compose`! 🐋**
