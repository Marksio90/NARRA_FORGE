# NARRA_FORGE - Instrukcje Docker 🐳

## 📋 Wymagania

- Docker (wersja 20.10+)
- Docker Compose (wersja 2.0+)
- Klucz API Anthropic

---

## ⚡ Szybki Start

### 1. Przygotowanie

```bash
# Sklonuj repozytorium (jeśli jeszcze nie masz)
git clone https://github.com/Marksio90/NARRA_FORGE.git
cd NARRA_FORGE

# Utwórz plik .env z kluczem API
echo "ANTHROPIC_API_KEY=twój-klucz-api" > .env
```

### 2. Build i Test

```bash
# Zbuduj obraz Docker
docker-compose build

# Uruchom test systemu
docker-compose up narra-forge

# Lub bezpośrednio
docker-compose run --rm narra-forge
```

### 3. Spodziewany Wynik

Powinieneś zobaczyć:

```
============================================================
NARRA_FORGE - Test Kontenera Docker
============================================================

[Test 1] Sprawdzanie struktury katalogów...
  ✓ narra_forge/ istnieje
  ✓ data/ istnieje
  ✓ output/ istnieje
  ✓ logs/ istnieje

[Test 2] Sprawdzanie importów...
  ✓ narra_forge.core.types
  ✓ narra_forge.core.config
  ✓ narra_forge.core.orchestrator
  ✓ narra_forge.memory.base
  ✓ Wszystkie 10 agentów
  ✓ narra_forge.world.world_manager

[Test 3] Sprawdzanie konfiguracji...
  ✓ Konfiguracja załadowana
  ✓ Domyślny model: claude-sonnet
  ✓ Liczba modeli: 4
  ✓ Min. coherence score: 0.85

[Test 4] Sprawdzanie zmiennych środowiskowych...
  ✓ ANTHROPIC_API_KEY: sk-ant-...xyz

[Test 5] Test systemu pamięci...
  ✓ SQLiteMemorySystem zainicjalizowany
  ✓ Zapis i odczyt z pamięci działa

[Test 6] Test typów danych...
  ✓ WorldBible: Test World
  ✓ Character: Test Character
  ✓ ProjectBrief: short_story, fantasy

============================================================
✅ WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE
============================================================
```

---

## 🎯 Użycie

### Test Podstawowy (bez API)

```bash
# Uruchom test struktury i importów
docker-compose run --rm narra-forge python test_docker.py
```

### Uruchomienie Przykładu (z API)

```bash
# Uwaga: To wywoła rzeczywiste API i zużyje tokeny!
docker-compose run --rm narra-forge python przyklad_uzycia_pl.py
```

### Tryb Interaktywny (Development)

```bash
# Uruchom shell w kontenerze
docker-compose run --rm narra-forge-dev bash

# W kontenerze możesz:
python test_docker.py
python przyklad_uzycia_pl.py
python -c "from narra_forge.core.config import get_default_config; print(get_default_config())"
```

---

## 📁 Volumes (Persystencja Danych)

Dane są zapisywane w lokalnych katalogach:

```
./data/    → /app/data    (bazy danych SQLite)
./output/  → /app/output  (wygenerowane narracje)
./logs/    → /app/logs    (logi systemowe)
```

Pliki utworzone w kontenerze będą dostępne na hoście.

---

## 🔧 Konfiguracja

### Zmienne Środowiskowe

Plik `.env`:
```bash
# Wymagane
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# Opcjonalne
OPENAI_API_KEY=sk-xxx
```

### Customizacja docker-compose.yml

```yaml
services:
  narra-forge:
    environment:
      # Dodatkowe zmienne
      - DEBUG=true
      - LOG_LEVEL=DEBUG

    # Zmień komendę
    command: python moj_skrypt.py

    # Dodaj porty (jeśli planujesz API)
    ports:
      - "8000:8000"
```

---

## 🐛 Troubleshooting

### Problem: "docker: command not found"

```bash
# Zainstaluj Docker
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install docker.io docker-compose

# MacOS:
brew install docker docker-compose
```

### Problem: "permission denied"

```bash
# Dodaj użytkownika do grupy docker
sudo usermod -aG docker $USER
# Wyloguj się i zaloguj ponownie
```

### Problem: "ANTHROPIC_API_KEY not set"

```bash
# Sprawdź czy plik .env istnieje
cat .env

# Jeśli nie, utwórz go:
echo "ANTHROPIC_API_KEY=twój-klucz" > .env

# Lub przekaż bezpośrednio:
ANTHROPIC_API_KEY=twój-klucz docker-compose run narra-forge
```

### Problem: "Cannot connect to the Docker daemon"

```bash
# Uruchom Docker daemon
sudo systemctl start docker

# Lub na MacOS
open -a Docker
```

### Problem: Build trwa bardzo długo

```bash
# Użyj cache
docker-compose build --parallel

# Lub build bez cache (czysty build)
docker-compose build --no-cache
```

---

## 📊 Testowanie Kompletne

### Test 1: Struktura i Importy (BEZPŁATNY)

```bash
docker-compose run --rm narra-forge python test_docker.py
```

**Czas:** ~5 sekund
**Koszt:** 0 PLN
**Sprawdza:** Czy wszystko jest poprawnie zainstalowane

### Test 2: Generacja Mini-Narracji (PŁATNY)

Stwórz plik `test_mini.py`:

```python
import asyncio
from narra_forge.core.config import get_default_config
from narra_forge.core.orchestrator import NarrativeOrchestrator

async def main():
    orchestrator = NarrativeOrchestrator(get_default_config())

    zlecenie = """
    Napisz bardzo krótki fragment (200 słów) o космонауcie na Marsie.
    """

    wynik = await orchestrator.produce_narrative(zlecenie)
    print("✅ Test zakończony:", wynik["success"])

asyncio.run(main())
```

```bash
docker-compose run --rm narra-forge python test_mini.py
```

**Czas:** ~2-3 minuty
**Koszt:** ~$0.10-0.20
**Sprawdza:** Czy cały pipeline działa

### Test 3: Pełna Narracja (PŁATNY)

```bash
docker-compose run --rm narra-forge python przyklad_uzycia_pl.py
```

**Czas:** ~10-20 minut
**Koszt:** ~$1-3
**Sprawdza:** Kompletny system, generacja ~5000 słów

---

## 🔄 Workflow Developerski

### 1. Edytuj kod lokalnie

```bash
# Kod jest w ./narra_forge/
vim narra_forge/agents/my_new_agent.py
```

### 2. Test w kontenerze

```bash
# Rebuild image
docker-compose build

# Test
docker-compose run --rm narra-forge python test_docker.py
```

### 3. Debug interaktywny

```bash
# Wejdź do kontenera
docker-compose run --rm narra-forge-dev bash

# W kontenerze
python -i
>>> from narra_forge.core.config import get_default_config
>>> config = get_default_config()
>>> print(config)
```

---

## 🚀 Produkcja

### Build Image Produkcyjny

```bash
# Tag z wersją
docker build -t narra-forge:1.0.0 .

# Push do registry (opcjonalnie)
docker tag narra-forge:1.0.0 your-registry/narra-forge:1.0.0
docker push your-registry/narra-forge:1.0.0
```

### Uruchomienie Produkcyjne

```bash
# Z docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Lub bezpośrednio
docker run -d \
  --name narra-forge \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  narra-forge:1.0.0
```

---

## 📈 Monitorowanie

### Logi

```bash
# Logi w czasie rzeczywistym
docker-compose logs -f narra-forge

# Ostatnie 100 linii
docker-compose logs --tail=100 narra-forge
```

### Status

```bash
# Sprawdź działające kontenery
docker-compose ps

# Statystyki
docker stats narra-forge-app
```

### Wejście do Kontenera

```bash
# Bash
docker-compose exec narra-forge bash

# Python REPL
docker-compose exec narra-forge python
```

---

## 🧹 Czyszczenie

```bash
# Stop kontenerów
docker-compose down

# Stop + usuń volumes
docker-compose down -v

# Usuń image
docker rmi narra-forge:latest

# Czyszczenie kompletne
docker system prune -a
```

---

## 💡 Pro Tips

### 1. Szybszy Build

```bash
# Multi-stage build (dodaj do Dockerfile)
FROM python:3.11-slim as builder
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```

### 2. Cache Dependencies

```bash
# Skopiuj requirements.txt osobno
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### 3. Health Check

```yaml
# W docker-compose.yml
healthcheck:
  test: ["CMD", "python", "-c", "import narra_forge"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 📚 Dodatkowe Zasoby

- [Dokumentacja Docker](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**NARRA_FORGE w Dockerze - gotowy do produkcji!** 🐳🚀
