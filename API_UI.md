# NARRA_FORGE - API & UI Documentation

## 📚 Spis treści

1. [Szybki start](#szybki-start)
2. [REST API](#rest-api)
3. [Streamlit UI](#streamlit-ui)
4. [WebSocket](#websocket)
5. [System Iteracji i Rewizji](#system-iteracji-i-rewizji)
6. [Export do ePub i PDF](#export-do-epub-i-pdf)
7. [Przykłady użycia](#przykłady-użycia)
8. [Deployment](#deployment)

---

## 🚀 Szybki start

### Uruchomienie z Docker Compose

```bash
# 1. Ustaw zmienne środowiskowe
cp .env.example .env
# Edytuj .env i dodaj OPENAI_API_KEY

# 2. Uruchom wszystko
docker-compose up -d narra-forge-api narra-forge-ui

# 3. Otwórz w przeglądarce
# - UI: http://localhost:8501
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Uruchomienie lokalne (bez Dockera)

```bash
# 1. Zainstaluj zależności
pip install -r requirements.txt

# 2. Terminal 1: API Server
python -m uvicorn narra_forge.api.server:app --reload

# 3. Terminal 2: Streamlit UI
streamlit run narra_forge/ui/streamlit_app.py

# 4. Otwórz w przeglądarce
# - UI: http://localhost:8501
# - API: http://localhost:8000
```

---

## 🔌 REST API

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00",
  "active_projects": 3
}
```

---

#### 2. Rozpocznij generację narracji
```http
POST /api/generate
```

**Request Body:**
```json
{
  "brief": "Stwórz mroczne opowiadanie science fiction...",
  "form": "short_story",
  "genre": "sci_fi",
  "world_scale": "intimate",
  "thematic_focus": ["survival", "morality"],
  "expansion_potential": "standalone",
  "preferred_model": "gpt-4-turbo",
  "temperature": 0.7
}
```

**Parameters:**

| Parametr | Typ | Wymagane | Opis |
|----------|-----|----------|------|
| `brief` | string | ✅ | Opis zlecenia narracyjnego |
| `form` | string | ❌ | `short_story`, `novella`, `novel`, `epic` |
| `genre` | string | ❌ | `sci_fi`, `fantasy`, `horror`, `thriller`, `drama`, `mystery` |
| `world_scale` | string | ❌ | `intimate`, `regional`, `global`, `cosmic` |
| `thematic_focus` | array | ❌ | Lista tematów (np. `["survival", "morality"]`) |
| `expansion_potential` | string | ❌ | `standalone`, `series`, `universe` |
| `preferred_model` | string | ❌ | Model AI (domyślnie: `gpt-4-turbo`) |
| `temperature` | float | ❌ | 0.0-1.0 (domyślnie: 0.7) |

**Response:**
```json
{
  "project_id": "8b0061ba-d6af-4da8-9ea3-5c641348627e",
  "status": "queued",
  "message": "Projekt dodany do kolejki. Generacja rozpocznie się wkrótce.",
  "status_url": "/api/status/8b0061ba-d6af-4da8-9ea3-5c641348627e",
  "websocket_url": "/ws/8b0061ba-d6af-4da8-9ea3-5c641348627e"
}
```

---

#### 3. Pobierz status projektu
```http
GET /api/status/{project_id}
```

**Response:**
```json
{
  "project_id": "8b0061ba-d6af-4da8-9ea3-5c641348627e",
  "status": "processing",
  "current_stage": "SEQUENTIAL_GENERATION",
  "progress": 0.6,
  "stages_completed": [
    "BRIEF_INTERPRETATION",
    "WORLD_ARCHITECTURE",
    "CHARACTER_ARCHITECTURE",
    "NARRATIVE_STRUCTURE",
    "SEGMENT_PLANNING",
    "SEQUENTIAL_GENERATION"
  ],
  "stages_failed": [],
  "estimated_time_remaining": null,
  "created_at": "2024-01-15T12:00:00",
  "started_at": "2024-01-15T12:00:05",
  "completed_at": null,
  "output_files": null,
  "metadata": {},
  "error": null
}
```

**Status values:**
- `queued` - W kolejce
- `processing` - W trakcie przetwarzania
- `completed` - Ukończone
- `failed` - Nieudane

---

#### 4. Lista wszystkich projektów
```http
GET /api/projects?status=completed&limit=50
```

**Query Parameters:**
| Parametr | Typ | Opis |
|----------|-----|------|
| `status` | string | Filtruj po statusie (`queued`, `processing`, `completed`, `failed`) |
| `limit` | integer | Maksymalna liczba wyników (domyślnie: 50) |

**Response:**
```json
{
  "total": 15,
  "projects": [
    {
      "id": "8b0061ba-d6af-4da8-9ea3-5c641348627e",
      "status": "completed",
      "stages_completed": [...],
      "stages_failed": [],
      "created_at": "2024-01-15T12:00:00",
      "started_at": "2024-01-15T12:00:05",
      "completed_at": "2024-01-15T12:05:30",
      ...
    }
  ]
}
```

---

#### 5. Usuń projekt
```http
DELETE /api/projects/{project_id}
```

**Response:**
```json
{
  "message": "Projekt 8b0061ba-d6af-4da8-9ea3-5c641348627e usunięty"
}
```

**Note:** Nie można usunąć projektów w trakcie przetwarzania (`status: "processing"`).

---

## 🌐 WebSocket

### Połączenie
```
ws://localhost:8000/ws/{project_id}
```

### Wiadomości

#### Server → Client: Status Update
```json
{
  "type": "status",
  "data": {
    "id": "8b0061ba-d6af-4da8-9ea3-5c641348627e",
    "status": "processing",
    "current_stage": "SEQUENTIAL_GENERATION",
    "progress": 0.6,
    ...
  }
}
```

#### Server → Client: Update
```json
{
  "type": "update",
  "data": {
    "id": "8b0061ba-d6af-4da8-9ea3-5c641348627e",
    "status": "completed",
    "stages_completed": [...],
    ...
  }
}
```

### Przykład (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/8b0061ba-d6af-4da8-9ea3-5c641348627e');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === 'update') {
    console.log('Status update:', message.data);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## 🖥️ Streamlit UI

### Funkcjonalności

#### 1. **Nowa Generacja** 🎬
- Formularz do tworzenia nowych narracji
- Wszystkie parametry konfiguracyjne
- Zaawansowane opcje (model AI, temperature)

#### 2. **Monitor** 📊
- Real-time monitoring postępu
- Wizualizacja 10 etapów pipeline'u
- Automatyczne odświeżanie
- Metryki (postęp %, etapy ukończone, czas trwania)

#### 3. **Wszystkie Projekty** 📚
- Lista wszystkich projektów
- Filtrowanie po statusie
- Szybkie przełączanie do monitoringu
- Usuwanie ukończonych projektów

### UI Layout

```
┌─────────────────────────────────────────────────┐
│              📚 NARRA_FORGE                     │
│   Autonomiczny Wieloświatowy System Generowania │
│              Narracji                            │
├─────────────┬───────────────────────────────────┤
│             │                                   │
│  📋 Menu    │         [Zawartość strony]        │
│             │                                   │
│  🎬 Nowa    │                                   │
│  📊 Monitor │                                   │
│  📚 Projekty│                                   │
│             │                                   │
│  ───────    │                                   │
│             │                                   │
│  ✅ API     │                                   │
│  Połączone  │                                   │
│             │                                   │
└─────────────┴───────────────────────────────────┘
```

---

## 📖 Przykłady użycia

### Python (requests)

```python
import requests
import time

# 1. Rozpocznij generację
response = requests.post('http://localhost:8000/api/generate', json={
    "brief": """
    Stwórz mroczne opowiadanie science fiction osadzone w umierającym
    systemie gwiezdnym. Główny bohater to ostatni pilot transportowy,
    który odkrywa tajemniczy ładunek mogący ocalić lub zniszczyć
    pozostałych przy życiu ludzi.
    """,
    "form": "short_story",
    "genre": "sci_fi",
    "world_scale": "intimate",
    "thematic_focus": ["survival", "morality"],
    "temperature": 0.75
})

project = response.json()
project_id = project['project_id']

print(f"✅ Projekt utworzony: {project_id}")

# 2. Monitoruj postęp
while True:
    status = requests.get(f'http://localhost:8000/api/status/{project_id}').json()

    print(f"Status: {status['status']} - Postęp: {int(status['progress']*100)}%")

    if status['status'] in ['completed', 'failed']:
        break

    time.sleep(5)

# 3. Sprawdź wyniki
if status['status'] == 'completed':
    print(f"✅ Generacja ukończona!")
    print(f"Pliki wyjściowe: {status['output_files']}")
else:
    print(f"❌ Błąd: {status['error']}")
```

### curl

```bash
# Rozpocznij generację
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "brief": "Stwórz mroczne opowiadanie...",
    "form": "short_story",
    "genre": "sci_fi"
  }'

# Pobierz status
curl http://localhost:8000/api/status/{project_id}

# Lista projektów
curl "http://localhost:8000/api/projects?status=completed"

# Usuń projekt
curl -X DELETE http://localhost:8000/api/projects/{project_id}
```

---

## 🚀 Deployment

### Docker Compose (Produkcja)

```yaml
version: '3.8'

services:
  narra-forge-api:
    image: narra-forge:latest
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    restart: always

  narra-forge-ui:
    image: narra-forge:latest
    ports:
      - "8501:8501"
    depends_on:
      - narra-forge-api
    restart: always
```

### Uruchomienie

```bash
docker-compose up -d narra-forge-api narra-forge-ui
```

### Sprawdzenie statusu

```bash
docker-compose ps
docker-compose logs -f narra-forge-api
docker-compose logs -f narra-forge-ui
```

---

## 🔧 Konfiguracja

### Zmienne środowiskowe

```bash
# .env
OPENAI_API_KEY=sk-proj-xxx...  # WYMAGANE
ANTHROPIC_API_KEY=sk-ant-xxx...  # OPCJONALNE (backup)
```

### Porty

- **API**: `8000`
- **UI**: `8501`

### Volumes

- `./data` - Baza danych SQLite (pamięć)
- `./output` - Wygenerowane narracje
- `./logs` - Logi systemowe

---

## 📊 Pipeline (10 Etapów)

1. **BRIEF_INTERPRETATION** - Interpretacja zlecenia
2. **WORLD_ARCHITECTURE** - Architektura świata
3. **CHARACTER_ARCHITECTURE** - Architektura postaci
4. **NARRATIVE_STRUCTURE** - Struktura narracyjna
5. **SEGMENT_PLANNING** - Planowanie segmentów
6. **SEQUENTIAL_GENERATION** - Generacja sekwencyjna
7. **COHERENCE_CONTROL** - Kontrola koherencji
8. **LANGUAGE_STYLIZATION** - Stylizacja językowa
9. **EDITORIAL_REVIEW** - Redakcja wydawnicza
10. **FINAL_OUTPUT** - Finalne wyjście

---

## 🔄 System Iteracji i Rewizji

System iteracji pozwala na poprawianie i regenerację wygenerowanych narracji od wybranego etapu pipeline'u. Każda rewizja może tworzyć nową wersję lub nadpisywać istniejącą.

### Kluczowe funkcje

- ✅ **Regeneracja od dowolnego etapu** - Wybierz etap, od którego chcesz ponowić generację
- ✅ **Wersjonowanie** - Twórz nowe wersje lub nadpisuj istniejące
- ✅ **Snapshots kontekstu** - Automatyczne zapisywanie stanu po każdym etapie
- ✅ **Instrukcje rewizji** - Dodaj wskazówki dla agentów (np. "Zmień ton na bardziej mroczny")
- ✅ **Porównywanie wersji** - Porównuj różne wersje narracji
- ✅ **Modyfikacje kontekstu** - Ręcznie zmodyfikuj parametry przed regeneracją

### Architektura

#### RevisionSystem

Główna klasa zarządzająca rewizjami:

```python
class RevisionSystem:
    def save_context_snapshot(
        project_id: str,
        stage: PipelineStage,
        context: Dict[str, Any],
        version: int = 1
    )
    # Zapisuje snapshot kontekstu po etapie
    # Format: data/revisions/{project_id}/v{version}_stage{num}_{name}.json

    def load_context_snapshot(
        project_id: str,
        stage: PipelineStage,
        version: int = 1
    ) -> Dict[str, Any]
    # Wczytuje kontekst z wybranego etapu

    def get_latest_version(project_id: str) -> int
    # Zwraca numer najnowszej wersji

    def list_versions(project_id: str) -> List[Dict]
    # Lista wszystkich wersji z informacjami o etapach

    def compare_versions(
        project_id: str,
        version1: int,
        version2: int,
        stage: PipelineStage
    ) -> Dict
    # Porównuje dwie wersje na danym etapie
```

#### Struktura snapshota

```json
{
  "project_id": "abc-123",
  "version": 1,
  "stage": "WORLD_ARCHITECTURE",
  "stage_number": 2,
  "timestamp": "2024-01-15T12:30:45",
  "context": {
    "brief": {...},
    "world": {...},
    "user_request": "...",
    "start_time": "2024-01-15T12:00:00"
  }
}
```

### API Endpoints

#### 1. Rozpocznij rewizję

```http
POST /api/revise
```

**Request Body:**
```json
{
  "project_id": "abc-123",
  "from_stage": "CHARACTER_ARCHITECTURE",
  "instructions": "Zmień postaci, aby były bardziej kontrastowe charakterologicznie",
  "context_modifications": {
    "character_count": 5
  },
  "create_new_version": true
}
```

**Parameters:**

| Parametr | Typ | Wymagane | Opis |
|----------|-----|----------|------|
| `project_id` | string | ✅ | ID projektu do rewizji |
| `from_stage` | string | ✅ | Etap od którego rozpocząć regenerację |
| `instructions` | string | ❌ | Dodatkowe instrukcje dla agentów |
| `context_modifications` | object | ❌ | Modyfikacje kontekstu (np. parametrów) |
| `create_new_version` | boolean | ❌ | Czy utworzyć nową wersję (domyślnie: true) |

**Możliwe wartości `from_stage`:**
- `BRIEF_INTERPRETATION`
- `WORLD_ARCHITECTURE`
- `CHARACTER_ARCHITECTURE`
- `NARRATIVE_STRUCTURE`
- `SEGMENT_PLANNING`
- `SEQUENTIAL_GENERATION`
- `COHERENCE_CONTROL`
- `LANGUAGE_STYLIZATION`
- `EDITORIAL_REVIEW`
- `FINAL_OUTPUT`

**Response:**
```json
{
  "success": true,
  "message": "Revision started",
  "project_id": "abc-123",
  "version": 2,
  "from_stage": "CHARACTER_ARCHITECTURE",
  "status": "processing"
}
```

**Proces rewizji:**
1. System wczytuje kontekst z etapu poprzedzającego `from_stage`
2. Aplikuje `context_modifications` jeśli podano
3. Dodaje `instructions` do kontekstu
4. Wykonuje wszystkie etapy od `from_stage` do końca
5. Zapisuje snapshots po każdym etapie
6. Zwraca finalny wynik

---

#### 2. Lista wersji projektu

```http
GET /api/versions/{project_id}
```

**Response:**
```json
{
  "project_id": "abc-123",
  "total_versions": 3,
  "versions": [
    {
      "version": 3,
      "stages": [
        {
          "stage": "BRIEF_INTERPRETATION",
          "stage_number": 1,
          "timestamp": "2024-01-15T14:00:00"
        },
        {
          "stage": "WORLD_ARCHITECTURE",
          "stage_number": 2,
          "timestamp": "2024-01-15T14:05:00"
        }
        // ... więcej etapów
      ],
      "created_at": "2024-01-15T14:00:00"
    },
    {
      "version": 2,
      "stages": [...],
      "created_at": "2024-01-15T13:00:00"
    },
    {
      "version": 1,
      "stages": [...],
      "created_at": "2024-01-15T12:00:00"
    }
  ]
}
```

---

#### 3. Porównaj wersje

```http
GET /api/compare/{project_id}?version1=1&version2=2&stage=WORLD_ARCHITECTURE
```

**Parameters:**

| Parametr | Typ | Wymagane | Opis |
|----------|-----|----------|------|
| `version1` | int | ✅ | Pierwsza wersja do porównania |
| `version2` | int | ✅ | Druga wersja do porównania |
| `stage` | string | ❌ | Etap do porównania (domyślnie: FINAL_OUTPUT) |

**Response:**
```json
{
  "project_id": "abc-123",
  "version1": 1,
  "version2": 2,
  "stage": "WORLD_ARCHITECTURE",
  "differences": [
    {
      "path": "world.name",
      "type": "value_change",
      "from": "Krawędź Izolacji",
      "to": "Granica Samotności"
    },
    {
      "path": "world.tone",
      "type": "value_change",
      "from": "dystopijny",
      "to": "apokaliptyczny"
    },
    {
      "path": "world.rules.physics",
      "type": "added",
      "value": "zmieniona grawitacja"
    }
  ]
}
```

### Użycie w Streamlit UI

#### Strona Rewizji (🔄 Rewizja)

1. **Wybór projektu**
   - Lista ukończonych projektów z listy rozwijanej
   - Automatyczne wczytanie historii wersji po wyborze

2. **Historia wersji**
   - Wyświetlenie wszystkich wersji projektu
   - Rozwijalne sekcje z informacjami o etapach
   - Timestamp każdej wersji

3. **Formularz rewizji**
   - **Wybór etapu**: Dropdown z 10 etapami pipeline'u
   - **Instrukcje rewizji**: Textarea na dodatkowe wskazówki
   - **Utwórz nową wersję**: Checkbox (domyślnie: włączone)
   - Przycisk "🔄 Rozpocznij rewizję"

4. **Porównywanie wersji**
   - Wybór dwóch wersji do porównania
   - Wybór etapu do porównania
   - Wyświetlenie różnic w formie tabelarycznej

### Przykłady użycia

#### Przykład 1: Zmiana postaci

```python
import requests

# Rewizja: Zmień postaci na bardziej kontrastowe
response = requests.post("http://localhost:8000/api/revise", json={
    "project_id": "abc-123",
    "from_stage": "CHARACTER_ARCHITECTURE",
    "instructions": "Stwórz postaci o skrajnie różnych charakterach i motywacjach",
    "create_new_version": True
})

print(f"Utworzono wersję: {response.json()['version']}")
```

#### Przykład 2: Zmiana tonu narracji

```python
# Rewizja: Zmień ton na bardziej mroczny
response = requests.post("http://localhost:8000/api/revise", json={
    "project_id": "abc-123",
    "from_stage": "LANGUAGE_STYLIZATION",
    "instructions": "Zastosuj znacznie mroczniejszy ton narracji, zwiększ atmosferę niepokoju",
    "create_new_version": True
})
```

#### Przykład 3: Modyfikacja świata

```python
# Rewizja: Zmień skalę świata
response = requests.post("http://localhost:8000/api/revise", json={
    "project_id": "abc-123",
    "from_stage": "WORLD_ARCHITECTURE",
    "context_modifications": {
        "world_scale": "epic"  # Zmień z "intimate" na "epic"
    },
    "instructions": "Rozszerz świat na skalę galaktyczną",
    "create_new_version": True
})
```

#### Przykład 4: Porównanie wersji

```python
# Porównaj wersję 1 i 2 na etapie WORLD_ARCHITECTURE
response = requests.get(
    "http://localhost:8000/api/compare/abc-123",
    params={
        "version1": 1,
        "version2": 2,
        "stage": "WORLD_ARCHITECTURE"
    }
)

differences = response.json()["differences"]
for diff in differences:
    print(f"{diff['path']}: {diff['from']} -> {diff['to']}")
```

### Najlepsze praktyki

#### 1. Kiedy tworzyć nową wersję?
- ✅ **Twórz nową wersję** gdy:
  - Chcesz zachować poprzednią wersję
  - Eksperymentujesz z różnymi podejściami
  - Robisz znaczące zmiany w kierunku narracji

- ❌ **Nadpisuj wersję** gdy:
  - Poprawiasz drobne błędy
  - Kontynuujesz niedokończoną generację
  - Nie potrzebujesz historii zmian

#### 2. Wybór etapu rewizji
- **Wczesne etapy (1-3)**: Zmiana świata, postaci, podstawowych założeń
- **Środkowe etapy (4-6)**: Zmiana struktury, przebiegu wydarzeń
- **Późne etapy (7-10)**: Zmiany stylistyczne, językowe, edytorskie

#### 3. Instrukcje rewizji
- Bądź konkretny: "Zwiększ konflikt między bohaterami" zamiast "Popraw postacie"
- Podaj przykłady: "Główny bohater powinien być bardziej cyniczny, jak Rick z Rick and Morty"
- Skupiaj się na jednej zmianie na raz

#### 4. Modyfikacje kontekstu
- Użyj gdy wiesz dokładnie jaki parametr zmienić
- Dostępne modyfikacje:
  ```python
  {
    "world_scale": "intimate" | "small" | "medium" | "large" | "epic",
    "character_count": int,
    "thematic_focus": ["theme1", "theme2"],
    "temperature": float,  # Kontrola kreatywności LLM
    "tone": str  # Dodatkowe wskazówki tonalne
  }
  ```

### Monitoring rewizji

Rewizje działają jako background tasks, więc możesz:

1. **Sprawdzić status** w sekcji "📊 Monitor" w UI
2. **Śledzić postęp** przez WebSocket updates
3. **Porównać wyniki** po zakończeniu w sekcji "🔄 Rewizja"

### Struktura plików

```
data/revisions/
└── abc-123/                    # project_id
    ├── v1_stage1_BRIEF_INTERPRETATION.json
    ├── v1_stage2_WORLD_ARCHITECTURE.json
    ├── v1_stage3_CHARACTER_ARCHITECTURE.json
    ├── ...
    ├── v2_stage1_BRIEF_INTERPRETATION.json
    ├── v2_stage2_WORLD_ARCHITECTURE.json
    └── ...
```

Każdy snapshot zawiera pełny kontekst produkcji na danym etapie, co pozwala na wznowienie generacji z dowolnego punktu.

---

## 📥 Export do ePub i PDF

System exportu pozwala na publikację wygenerowanych narracji w formacie ePub (e-booki) i PDF (druk/universal). Każdy export zachowuje metadane, formatowanie i strukturę narracji.

### Obsługiwane formaty

#### ePub
- **Przeznaczenie**: E-readery (Kindle, Kobo, iBooks), aplikacje mobilne
- **Funkcje**:
  - Metadane książki (tytuł, autor, język, identyfikator)
  - Rozdziały jako pliki HTML
  - Spis treści (TOC)
  - Stylowanie CSS (czcionki, marginesy, wcięcia)
  - Automatyczne formatowanie dialogów
- **Kompatybilność**: EPUB 3.0 standard

#### PDF
- **Przeznaczenie**: Druk, podgląd uniwersalny, archiwizacja
- **Funkcje**:
  - Strona tytułowa z metadanymi
  - Opcjonalny spis treści
  - Formatowanie akapitów (justowanie, wcięcia)
  - Numeracja stron
  - Stylizacja rozdziałów
  - Obsługa dialogów (kursywa, wcięcia)
- **Format**: A4, marginesy 2.5cm

### Architektura modułów

#### EpubExporter (`narra_forge/export/epub_exporter.py`)

```python
from narra_forge.export import EpubExporter

exporter = EpubExporter()

file_path = exporter.export(
    narrative_data={
        "output": {...},  # Treść narracji
        "metadata": {...}  # Metadane projektu
    },
    output_path="output/narracja.epub",
    metadata={
        "title": "Tytuł Narracji",
        "author": "Autor",
        "description": "Opis",
        "language": "pl"
    }
)
```

**Kluczowe metody:**
- `_prepare_metadata()` - Przygotowanie metadanych książki
- `_create_chapters()` - Tworzenie rozdziałów HTML
- `_extract_segments()` - Wyciąganie segmentów z danych narracji
- `_format_text()` - Formatowanie tekstu (akapity, dialogi)
- `_get_default_css()` - Domyślne stylowanie CSS

#### PdfExporter (`narra_forge/export/pdf_exporter.py`)

```python
from narra_forge.export import PdfExporter

exporter = PdfExporter()

file_path = exporter.export(
    narrative_data={...},
    output_path="output/narracja.pdf",
    metadata={
        "title": "Tytuł",
        "author": "Autor"
    },
    include_toc=True  # Dodaj spis treści
)
```

**Kluczowe metody:**
- `_create_title_page()` - Strona tytułowa
- `_create_toc()` - Spis treści
- `_create_chapters()` - Rozdziały z formatowaniem
- `_add_page_number()` - Numeracja stron

### API Endpoints

#### 1. Export narracji

```http
POST /api/export
```

**Request Body:**
```json
{
  "project_id": "abc-123",
  "format": "epub",
  "version": 1,
  "metadata": {
    "title": "Moja Narracja",
    "author": "Jan Kowalski",
    "description": "Krótki opis..."
  },
  "include_toc": false
}
```

**Parameters:**

| Parametr | Typ | Wymagane | Opis |
|----------|-----|----------|------|
| `project_id` | string | ✅ | ID projektu do exportu |
| `format` | string | ✅ | Format: `"epub"` lub `"pdf"` |
| `version` | int | ❌ | Numer wersji (domyślnie: najnowsza) |
| `metadata` | object | ❌ | Metadane (title, author, description) |
| `include_toc` | boolean | ❌ | Tylko PDF: czy dodać spis treści (domyślnie: false) |

**Response:**
```json
{
  "success": true,
  "message": "Export zakończony pomyślnie",
  "file_id": "abc-123_v1_epub_a1b2c3d4",
  "download_url": "/api/download/abc-123_v1_epub_a1b2c3d4",
  "format": "epub",
  "file_size": 125678
}
```

---

#### 2. Pobierz plik

```http
GET /api/download/{file_id}
```

**Parameters:**
- `file_id` - ID pliku zwrócony przez `/api/export`

**Response:**
- Plik do pobrania (ePub lub PDF)
- Content-Type: `application/epub+zip` lub `application/pdf`
- Filename: `narracja_{project_id}.{format}`

---

#### 3. Lista exportów projektu

```http
GET /api/exports/{project_id}
```

**Response:**
```json
{
  "project_id": "abc-123",
  "total_exports": 3,
  "exports": [
    {
      "file_id": "abc-123_v2_pdf_x9y8z7w6",
      "format": "pdf",
      "version": "v2",
      "size": 234567,
      "created_at": "2024-01-15T14:30:00",
      "download_url": "/api/download/abc-123_v2_pdf_x9y8z7w6"
    },
    {
      "file_id": "abc-123_v1_epub_a1b2c3d4",
      "format": "epub",
      "version": "v1",
      "size": 125678,
      "created_at": "2024-01-15T12:00:00",
      "download_url": "/api/download/abc-123_v1_epub_a1b2c3d4"
    }
  ]
}
```

### Użycie w Streamlit UI

#### Strona Projektów (📚 Wszystkie Projekty)

1. **Przycisk Export**
   - Dostępny dla ukończonych projektów
   - Otwiera dialog exportu

2. **Dialog exportu**
   - **Wybór formatu**: ePub lub PDF (radio buttons)
   - **Metadane**:
     - Tytuł (text input)
     - Autor (text input, domyślnie: "NARRA_FORGE")
     - Opis (textarea)
   - **Opcje PDF**: Checkbox "Dodaj spis treści"
   - Przyciski: "📥 Exportuj" / "❌ Anuluj"

3. **Po exportie**
   - Wyświetla sukces i rozmiar pliku
   - Link do pobrania pliku
   - Lista istniejących exportów projektu

4. **Lista istniejących exportów**
   - Pokazuje wszystkie poprzednie exporty
   - Format, wersja, rozmiar, data utworzenia
   - Link do pobrania każdego pliku

### Przykłady użycia

#### Przykład 1: Export do ePub przez API

```python
import requests

# Export projektu do ePub
response = requests.post("http://localhost:8000/api/export", json={
    "project_id": "abc-123",
    "format": "epub",
    "metadata": {
        "title": "Opowieść z Przyszłości",
        "author": "AI Narrator",
        "description": "Mroczna opowieść science fiction o samotności w kosmosie"
    }
})

result = response.json()
print(f"Export utworzony: {result['file_id']}")
print(f"Rozmiar: {result['file_size'] / 1024:.1f} KB")
print(f"Download URL: {result['download_url']}")
```

#### Przykład 2: Export do PDF ze spisem treści

```python
# Export projektu do PDF ze spisem treści
response = requests.post("http://localhost:8000/api/export", json={
    "project_id": "abc-123",
    "format": "pdf",
    "metadata": {
        "title": "Zbiór Opowiadań",
        "author": "NARRA_FORGE"
    },
    "include_toc": True  # Dodaj spis treści
})

result = response.json()
download_url = f"http://localhost:8000{result['download_url']}"
print(f"Pobierz PDF: {download_url}")
```

#### Przykład 3: Lista wszystkich exportów

```python
# Pobierz listę exportów dla projektu
response = requests.get("http://localhost:8000/api/exports/abc-123")
exports_data = response.json()

print(f"Znaleziono {exports_data['total_exports']} exportów:")
for exp in exports_data['exports']:
    print(f"  - {exp['format'].upper()}: {exp['size'] / 1024:.1f} KB ({exp['created_at']})")
    print(f"    Download: {exp['download_url']}")
```

#### Przykład 4: Download pliku w Python

```python
import requests

# Pobierz plik
file_id = "abc-123_v1_epub_a1b2c3d4"
response = requests.get(f"http://localhost:8000/api/download/{file_id}")

# Zapisz lokalnie
with open("narracja.epub", "wb") as f:
    f.write(response.content)

print(f"Pobrano: {len(response.content)} bajtów")
```

### Struktura plików

```
data/exports/
└── abc-123_v1_epub_a1b2c3d4.epub
└── abc-123_v1_pdf_x9y8z7w6.pdf
└── abc-123_v2_epub_q5r6s7t8.epub
```

Nazwa pliku: `{project_id}_v{version}_{format}_{random_id}.{format}`

### Formatowanie tekstu

#### Akapity
- Automatyczne wykrywanie podziału na akapity (podwójny enter)
- Justowanie tekstu
- Wcięcie pierwszej linii (1.5em w ePub, 20pt w PDF)
- Brak wcięcia po nagłówkach

#### Dialogi
- Automatyczne wykrywanie (linie zaczynające się od `—`, `–`, `-`)
- Stylowanie:
  - ePub: Kursywa, lewe wcięcie 2em
  - PDF: Kursywa, lewe wcięcie 1cm

#### Rozdziały
- Każdy segment narracji = osobny rozdział
- Tytuły centrowane
- Automatyczny page break (PDF) / nowy plik (ePub)

### Najlepsze praktyki

#### 1. Metadane
- **Zawsze podawaj tytuł**: Poprawia doświadczenie czytania
- **Autor**: Jeśli publikujesz publicznie, zmień z "NARRA_FORGE" na swoje nazwisko
- **Opis**: Krótkie 1-2 zdania, max 300 znaków

#### 2. Format
- **ePub**: Preferuj dla:
  - E-readerów (Kindle, Kobo)
  - Aplikacji mobilnych
  - Elastycznego fontu i rozmiaru
- **PDF**: Preferuj dla:
  - Druku fizycznego
  - Archiwizacji
  - Dokładnego layoutu

#### 3. Spis treści
- **ePub**: Zawsze generowany automatycznie
- **PDF**: Włącz `include_toc=True` tylko dla dłuższych form (novella, novel)

#### 4. Wersjonowanie
- Każdy export może być z innej wersji projektu
- Możesz wyexportować v1, v2, v3 osobno i porównać
- Stare exporty nie są automatycznie usuwane

### Ograniczenia

1. **Rozmiar pliku**:
   - ePub: ~100-500 KB dla typowej narracji
   - PDF: ~200 KB - 2 MB (zależnie od długości)

2. **Obrazy**:
   - Brak wsparcia dla okładek (planowane w przyszłości)
   - Brak ilustracji w tekście

3. **Formatowanie zaawansowane**:
   - Brak wsparcia dla stopek/nagłówków niestandardowych
   - Brak stylów per-rozdział

4. **Metadane**:
   - Brak wsparcia dla ISBN, wydawcy, kategorii (można dodać ręcznie po exportie)

### Troubleshooting

#### Export nie działa
```bash
# Sprawdź czy katalog exports istnieje
ls -la data/exports/

# Sprawdź logi API
docker-compose logs -f narra-forge-api
```

#### Plik jest uszkodzony
- **ePub**: Zwaliduj używając https://validator.idpf.org/
- **PDF**: Otwórz w Adobe Reader lub innym profesjonalnym czytniku

#### Brak linkdownload w UI
- Sprawdź czy API działa: `curl http://localhost:8000/health`
- Sprawdź konsole przeglądarki (F12)

#### Czcionki nie wyświetlają się poprawnie
- **ePub**: E-reader używa własnych czcionek (to normalne)
- **PDF**: Zainstaluj dodatkowe czcionki systemowe

---

## 🛠️ Troubleshooting

### API nie odpowiada
```bash
# Sprawdź status
docker-compose ps narra-forge-api

# Zobacz logi
docker-compose logs narra-forge-api

# Restart
docker-compose restart narra-forge-api
```

### UI nie łączy się z API
- Sprawdź czy API działa: `curl http://localhost:8000/health`
- Sprawdź logi UI: `docker-compose logs narra-forge-ui`
- Zweryfikuj czy porty nie są zajęte

### Błąd pamięci
- Zwiększ limity Docker
- Użyj lżejszego modelu (GPT-3.5 Turbo zamiast GPT-4)

---

## 📞 Support

- **Issues**: https://github.com/Marksio90/NARRA_FORGE/issues
- **Dokumentacja**: README.md, DOKUMENTACJA_PL.md
- **API Docs (Swagger)**: http://localhost:8000/docs

---

**NARRA_FORGE v1.0.0** - Autonomiczny Wieloświatowy System Generowania Narracji
