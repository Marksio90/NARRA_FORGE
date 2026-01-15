# 🧪 NARRA_FORGE - Przewodnik Testowania

Kompletny przewodnik testowania NARRA_FORGE lokalnie przez Docker.

---

## 🚀 Szybki Start (5 minut)

```bash
# 1. Sklonuj repo (jeśli jeszcze nie masz)
git clone https://github.com/Marksio90/NARRA_FORGE.git
cd NARRA_FORGE

# 2. Ustaw klucz OpenAI
cp .env.example .env
nano .env  # Dodaj: OPENAI_API_KEY=sk-proj-xxx...

# 3. Uruchom wszystko
./start_all.sh

# 4. Test automatyczny
./test_docker.sh

# 5. Otwórz w przeglądarce
# http://localhost:8501
```

---

## 📋 Wymagania

### Wymagane:
- Docker >= 20.10
- Docker Compose >= 1.29
- Klucz OpenAI API (https://platform.openai.com/api-keys)

### Opcjonalne:
- curl (do testów)
- Python 3.11+ (do testów bez Dockera)

---

## 🐳 Testowanie przez Docker

### 1. Podstawowe uruchomienie

```bash
# Najprostszy sposób
./start_all.sh

# Lub ręcznie
docker-compose up -d narra-forge-api narra-forge-ui
```

### 2. Weryfikacja statusu

```bash
# Sprawdź kontenery
docker-compose ps

# Powinno pokazać:
# NAME                 STATUS    PORTS
# narra-forge-api      Up        0.0.0.0:8000->8000/tcp
# narra-forge-ui       Up        0.0.0.0:8501->8501/tcp
```

### 3. Test automatyczny

```bash
./test_docker.sh
```

Skrypt sprawdza:
- ✅ Docker i docker-compose
- ✅ Status kontenerów
- ✅ API health check
- ✅ UI responsywność
- ✅ Wszystkie kluczowe endpointy
- ✅ Użycie zasobów

### 4. Monitorowanie

```bash
# Logi API (real-time)
docker-compose logs -f narra-forge-api

# Logi UI (real-time)
docker-compose logs -f narra-forge-ui

# Wszystkie logi
docker-compose logs -f

# Ostatnie 100 linii
docker-compose logs --tail=100

# Filtruj po błędach
docker-compose logs | grep ERROR
```

### 5. Debug w kontenerze

```bash
# Wejdź do kontenera API
docker-compose exec narra-forge-api bash

# W kontenerze możesz:
cd /app
python -c "from narra_forge.core.orchestrator import NarrativeOrchestrator; print('OK')"
ls -la data/
cat logs/narra_forge.log

# Wyjście: exit
```

---

## 🧪 Testy Manualne

### Test 1: API Health Check

```bash
curl http://localhost:8000/health

# Powinno zwrócić:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T12:00:00",
#   "active_projects": 0
# }
```

### Test 2: API Documentation

Otwórz w przeglądarce:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

### Test 3: Streamlit UI

Otwórz w przeglądarce:
- http://localhost:8501

Sprawdź czy widzisz:
- ✅ Nagłówek "NARRA_FORGE"
- ✅ Menu boczne z opcjami
- ✅ Status API (✅ API połączone)

### Test 4: Generacja narracji (pełny workflow)

**W UI (http://localhost:8501):**

1. Przejdź do **🎬 Nowa Generacja**
2. Wpisz brief:
   ```
   Stwórz krótkie opowiadanie science fiction o astronaucie
   który odkrywa tajemniczą wiadomość na opuszczonej stacji kosmicznej.
   ```
3. Ustaw parametry:
   - Forma: `short_story`
   - Gatunek: `sci_fi`
   - Skala świata: `intimate`
4. Kliknij **🚀 Rozpocznij generację**
5. Przejdź do **📊 Monitor**
6. Obserwuj postęp generacji
7. Po zakończeniu przejdź do **📚 Wszystkie Projekty**
8. Zobacz wynik

**Przez API (curl):**

```bash
# Rozpocznij generację
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "brief": "Krótkie opowiadanie sci-fi o astronaucie",
    "form": "short_story",
    "genre": "sci_fi",
    "world_scale": "intimate"
  }'

# Zapisz project_id z odpowiedzi
PROJECT_ID="xxx-yyy-zzz"

# Sprawdź status
curl http://localhost:8000/api/status/$PROJECT_ID

# Lista projektów
curl http://localhost:8000/api/projects
```

### Test 5: System rewizji

**W UI:**

1. Po wygenerowaniu narracji, przejdź do **🔄 Rewizja**
2. Wybierz projekt z listy
3. Zobacz historię wersji
4. Wybierz etap (np. CHARACTER_ARCHITECTURE)
5. Dodaj instrukcje: "Zmień postaci na bardziej kontrastowe"
6. Kliknij **🔄 Rozpocznij rewizję**
7. Monitoruj w **📊 Monitor**

**Przez API:**

```bash
# Rozpocznij rewizję
curl -X POST http://localhost:8000/api/revise \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "xxx-yyy-zzz",
    "from_stage": "CHARACTER_ARCHITECTURE",
    "instructions": "Zmień postaci na bardziej kontrastowe",
    "create_new_version": true
  }'

# Lista wersji
curl http://localhost:8000/api/versions/xxx-yyy-zzz

# Porównaj wersje
curl "http://localhost:8000/api/compare/xxx-yyy-zzz?version1=1&version2=2&stage=CHARACTER_ARCHITECTURE"
```

### Test 6: Export do ePub/PDF

**W UI:**

1. Przejdź do **📚 Wszystkie Projekty**
2. Dla ukończonego projektu kliknij **📥 Export**
3. Wybierz format (ePub lub PDF)
4. Uzupełnij metadane:
   - Tytuł: "Moja Pierwsza Narracja"
   - Autor: "Jan Kowalski"
5. Kliknij **📥 Exportuj**
6. Pobierz plik przez link
7. Otwórz w czytniku (Calibre dla ePub, Adobe Reader dla PDF)

**Przez API:**

```bash
# Export do ePub
curl -X POST http://localhost:8000/api/export \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "xxx-yyy-zzz",
    "format": "epub",
    "metadata": {
      "title": "Moja Narracja",
      "author": "Jan Kowalski"
    }
  }'

# Zapisz file_id z odpowiedzi
FILE_ID="xxx-yyy-zzz_v1_epub_abc123"

# Pobierz plik
curl -o narracja.epub http://localhost:8000/api/download/$FILE_ID

# Lub otwórz w przeglądarce:
# http://localhost:8000/api/download/xxx-yyy-zzz_v1_epub_abc123
```

---

## 🔧 Troubleshooting

### Problem: Kontenery nie startują

```bash
# Sprawdź logi
docker-compose logs

# Restart
docker-compose down
docker-compose up -d

# Rebuild jeśli zmieniałeś kod
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Problem: Brak połączenia z API

```bash
# Sprawdź czy port 8000 jest wolny
lsof -i :8000

# Sprawdź czy kontener działa
docker-compose ps narra-forge-api

# Sprawdź logi
docker-compose logs narra-forge-api

# Restart API
docker-compose restart narra-forge-api
```

### Problem: UI nie ładuje się

```bash
# Sprawdź czy port 8501 jest wolny
lsof -i :8501

# Sprawdź status
docker-compose ps narra-forge-ui

# Logi
docker-compose logs narra-forge-ui

# Restart UI
docker-compose restart narra-forge-ui
```

### Problem: Błąd "OPENAI_API_KEY not set"

```bash
# Sprawdź .env
cat .env | grep OPENAI_API_KEY

# Upewnij się że klucz jest prawidłowy
# Jeśli nie:
nano .env  # Dodaj OPENAI_API_KEY=sk-proj-xxx...

# Restart kontenerów
docker-compose restart
```

### Problem: Generacja się zawiesza

```bash
# Sprawdź logi w czasie rzeczywistym
docker-compose logs -f narra-forge-api

# Sprawdź użycie zasobów
docker stats

# Jeśli brakuje pamięci, zwiększ limit w docker-compose.yml
# Lub zrestartuj Docker Desktop
```

### Problem: Import error / brak modułu

```bash
# Rebuild z czystą cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Sprawdź czy requirements.txt jest aktualny
docker-compose exec narra-forge-api pip list
```

---

## 📊 Testy Wydajnościowe

### Test obciążenia API

```bash
# Zainstaluj apache-bench
sudo apt-get install apache2-utils

# Test 100 requestów, 10 równocześnie
ab -n 100 -c 10 http://localhost:8000/health

# Wyniki powinny pokazać:
# - Requests per second: >100
# - Time per request: <100ms
```

### Test pamięci

```bash
# Monitor użycia pamięci
watch -n 1 'docker stats --no-stream narra-forge-api'

# Po generacji narracji pamięć nie powinna przekraczać 2GB
```

---

## 🔒 Testy Bezpieczeństwa

### Test ekspozycji sekretów

```bash
# Sprawdź czy .env nie jest w repo
git ls-files | grep .env  # Powinno być puste

# Sprawdź logi czy nie wyświetlają kluczy
docker-compose logs | grep -i "api.*key"  # Nie powinno nic znaleźć
```

### Test portów

```bash
# Sprawdź otwarte porty
netstat -tulpn | grep -E "8000|8501"

# Powinny być widoczne tylko localhost (127.0.0.1)
# NIE powinno być 0.0.0.0 w produkcji
```

---

## 📝 Checklist Przed Produkcją

- [ ] Wszystkie testy z `./test_docker.sh` przechodzą
- [ ] Wygenerowano testową narrację end-to-end
- [ ] Przetestowano rewizję narracji
- [ ] Przetestowano export do ePub i PDF
- [ ] Sprawdzono logi pod kątem błędów
- [ ] Zweryfikowano użycie zasobów (RAM < 2GB)
- [ ] .env nie jest w repozytorium
- [ ] Klucze API są bezpiecznie przechowywane
- [ ] Dokumentacja jest aktualna

---

## 🎯 Następne Kroki

Po pomyślnych testach:

1. **Testuj różne briefs**: Spróbuj różnych gatunków, skal, motywów
2. **Eksperymentuj z rewizją**: Testuj różne etapy i instrukcje
3. **Porównuj wersje**: Użyj systemu porównywania wersji
4. **Eksportuj w różnych formatach**: Testuj ePub i PDF z metadanymi
5. **Monitoruj wydajność**: Obserwuj czasy generacji i użycie zasobów

---

## 📞 Wsparcie

Problemy? Sprawdź:
- GitHub Issues: https://github.com/Marksio90/NARRA_FORGE/issues
- Dokumentacja: `API_UI.md`
- Logi: `docker-compose logs -f`
