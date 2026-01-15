# NARRA_FORGE - ARCHITEKTURA V2
# System Batch Production dla Narracji Wydawniczych

```
WERSJA: 2.0.0-batch
DATA: 2026-01-15
STATUS: Specyfikacja techniczna
```

---

## 🎯 DEFINICJA SYSTEMU

**NARRA_FORGE V2** to:
- **BATCH ENGINE** do produkcji narracji wydawniczych
- **NIE chatbot, NIE streaming, NIE interaktywny**
- **Zamknięty cykl**: wejście → pełna analiza → pełna produkcja → wynik końcowy
- **OpenAI-only**: Wyłącznie modele OpenAI (gpt-4o-mini + gpt-4o)
- **Docker-first**: Wszystkie testy w Docker

---

## 🔧 TECHNOLOGIE (NIEZMIENNE)

### Dostawca AI
```
WYŁĄCZNIE: OpenAI API
ZABRONIONE: Anthropic, Claude, inne providery
```

### Modele OpenAI

| Model | Zastosowanie | Priorytet |
|-------|-------------|-----------|
| `gpt-4o-mini` | Analiza, planning, walidacja, struktury | ⭐ WYSOKI |
| `gpt-4o` | Generacja narracji, redakcja literacka | TYLKO gdy konieczne |

**Zasada optymalizacji kosztowej:**
- Mini WSZĘDZIE gdzie to możliwe
- GPT-4o TYLKO dla właściwej narracji literackiej

---

## 📐 ARCHITEKTURA MODUŁOWA

```
narra_forge/
│
├── core/                    # Rdzeń systemu
│   ├── config.py           # Konfiguracja (OpenAI, modele)
│   ├── orchestrator.py     # Batch Orchestrator (główny silnik)
│   ├── types.py            # Typy danych (dataclasses)
│   └── pipeline.py         # Definicja 10-etapowego pipeline
│
├── models/                  # Abstrakcja modeli AI
│   ├── base.py             # Interface dla modeli
│   ├── openai_client.py    # Klient OpenAI (JEDYNY backend)
│   └── model_router.py     # Router: mini vs gpt-4o
│
├── memory/                  # Potrójny system pamięci
│   ├── structural.py       # Światy, postacie, reguły (SZKIELET)
│   ├── semantic.py         # Wydarzenia, motywy, relacje (TREŚĆ)
│   ├── evolutionary.py     # Zmiany w czasie (EWOLUCJA)
│   └── storage.py          # Persistence (SQLite)
│
├── agents/                  # 10 wyspecjalizowanych agentów
│   ├── base.py             # BaseAgent z access do memory + modeli
│   ├── a01_brief_interpreter.py     # Etap 1: Interpretacja
│   ├── a02_world_architect.py       # Etap 2: Świat
│   ├── a03_character_architect.py   # Etap 3: Postacie
│   ├── a04_structure_designer.py    # Etap 4: Struktura
│   ├── a05_segment_planner.py       # Etap 5: Plan segmentów
│   ├── a06_sequential_generator.py  # Etap 6: Generacja
│   ├── a07_coherence_validator.py   # Etap 7: Walidacja
│   ├── a08_language_stylizer.py     # Etap 8: Stylizacja PL
│   ├── a09_editorial_reviewer.py    # Etap 9: Redakcja
│   └── a10_output_processor.py      # Etap 10: Finalizacja
│
├── world/                   # Multi-world / Multi-IP
│   ├── world_manager.py    # Zarządzanie światami
│   ├── world_schema.py     # Schemat świata (IP)
│   └── world_linker.py     # Linkowanie uniwersów
│
├── ui/                      # Interfejs użytkownika
│   ├── batch_ui.py         # Prosty UI produkcyjny (CLI/Web)
│   └── job_monitor.py      # Monitor statusu produkcji
│
└── utils/
    ├── token_counter.py    # Liczenie tokenów (oszczędność)
    ├── cost_tracker.py     # Tracking kosztów
    └── validators.py       # Walidatory pomocnicze
```

---

## 🔄 PIPELINE PRODUKCYJNY (10 ETAPÓW)

### Typ przetwarzania: **BATCH (nie streaming)**

```python
# CAŁY proces działa jako JEDEN ZAMKNIĘTY CYKL
# Zwraca wynik dopiero po zakończeniu WSZYSTKICH etapów

def produce_narrative_batch(brief: str) -> NarrativeOutput:
    """
    Batch production - JEDEN cykl, PEŁNY wynik.
    NIE streamuje, NIE zwraca cząstkowych rezultatów.
    """

    # ETAP 1: Interpretacja (gpt-4o-mini)
    brief_analysis = BriefInterpreter.analyze(brief)

    # ETAP 2: Architektura świata (gpt-4o-mini)
    world = WorldArchitect.design_world(brief_analysis)

    # ETAP 3: Architektura postaci (gpt-4o-mini)
    characters = CharacterArchitect.design_characters(world, brief_analysis)

    # ETAP 4: Struktura narracyjna (gpt-4o-mini)
    structure = StructureDesigner.design_structure(brief_analysis, world)

    # ETAP 5: Plan segmentów (gpt-4o-mini)
    segments = SegmentPlanner.plan_segments(structure, characters, world)

    # ETAP 6: Generacja sekwencyjna (gpt-4o) ← TUTAJ GŁÓWNY KOSZT
    narrative_text = SequentialGenerator.generate_all_segments(segments)

    # ETAP 7: Kontrola koherencji (gpt-4o-mini)
    validation = CoherenceValidator.validate(narrative_text, world, characters)
    if not validation.passed:
        # Retry lub fail
        raise CoherenceError(validation.issues)

    # ETAP 8: Stylizacja językowa (gpt-4o)
    stylized_text = LanguageStylizer.stylize_polish(narrative_text)

    # ETAP 9: Redakcja (gpt-4o-mini)
    final_text = EditorialReviewer.review(stylized_text)

    # ETAP 10: Finalizacja (local processing)
    output = OutputProcessor.finalize(
        text=final_text,
        world=world,
        characters=characters,
        metadata=brief_analysis
    )

    return output  # Zwracamy TYLKO po zakończeniu WSZYSTKICH etapów
```

---

## 🧠 POTRÓJNY SYSTEM PAMIĘCI

### 1. Pamięć Strukturalna (Structural Memory)
**Typ:** Relacyjna (SQLite)
**Przechowuje:**
- Światy (worlds)
- Postacie (characters)
- Reguły uniwersów (rules)
- Archetypy (archetypes)

**Schemat:**
```sql
CREATE TABLE worlds (
    world_id TEXT PRIMARY KEY,
    name TEXT,
    reality_laws JSON,  -- Prawa rzeczywistości
    boundaries JSON,    -- Granice (space/time/dimensional)
    anomalies JSON,     -- Celowe wyjątki
    core_conflict TEXT,
    existential_theme TEXT,
    created_at TIMESTAMP
);

CREATE TABLE characters (
    character_id TEXT PRIMARY KEY,
    world_id TEXT REFERENCES worlds(world_id),
    name TEXT,
    internal_trajectory JSON,  -- Dynamiczna trajektoria
    contradictions JSON,        -- Wewnętrzne sprzeczności
    cognitive_limits JSON,      -- Ograniczenia poznawcze
    evolution_capacity REAL,    -- Zdolność do zmiany
    created_at TIMESTAMP
);
```

### 2. Pamięć Semantyczna (Semantic Memory)
**Typ:** Graph + Embeddings
**Przechowuje:**
- Wydarzenia (events)
- Motywy (motifs)
- Relacje (relationships)
- Konflikty (conflicts)

**Format:**
```python
SemanticNode = {
    "id": "event_001",
    "type": "event",
    "content": "Odkrycie tajemnicy mistrza",
    "embedding": [0.123, 0.456, ...],  # OpenAI embeddings
    "connections": ["character_001", "location_005"],
    "significance": 0.87,
    "timestamp_in_story": 1234
}
```

### 3. Pamięć Ewolucyjna (Evolutionary Memory)
**Typ:** Timeline-based
**Przechowuje:**
- Zmiany stanów świata
- Ewolucje postaci
- Przemiany motywów
- Historia decyzji

**Schemat:**
```python
EvolutionEntry = {
    "entity_id": "character_001",
    "entity_type": "character",
    "timestamp": "2024-03-15T10:30:00",
    "change_type": "psychological_shift",
    "before_state": {...},
    "after_state": {...},
    "trigger": "event_015",
    "significance": 0.92
}
```

---

## 🌍 MULTI-WORLD / MULTI-IP

### Zasada
- Każdy świat = IP (Intellectual Property)
- Światy mogą być niezależne lub powiązane
- Historie mogą się odbywać w jednym lub wielu światach
- System obsługuje ekspansję uniwersów

### API
```python
# Tworzenie świata
world = world_manager.create_world(
    name="Królestwo Eternal",
    genre="dark_fantasy",
    reality_laws={...},
    boundaries={...}
)

# Produkcja w konkretnym świecie
narrative = orchestrator.produce_narrative(
    brief="Historia młodego alchemika...",
    world_id=world.world_id
)

# Linkowanie światów (multiverse)
world_manager.link_worlds(
    world_id_a="fantasy_001",
    world_id_b="scifi_002",
    link_type="dimensional_gate"
)

# Produkcja cross-universe
narrative = orchestrator.produce_narrative(
    brief="Podróż między wymiarami...",
    world_ids=["fantasy_001", "scifi_002"]
)
```

---

## 💰 OPTYMALIZACJA KOSZTOWA

### Zasady
1. **Streszczenia > Pełne teksty**
   - Nigdy nie wstrzykuj całych tekstów do promptów
   - Używaj streszczeń, struktur, list key points

2. **Struktury > Proza**
   - Analiza działa na strukturach (JSON, listy)
   - Proza tylko w etapach 6, 8

3. **Pamięć > Kontekst**
   - Nie duplikuj kontekstu w każdym wywołaniu
   - Używaj memory systemu do retrievalu

4. **Mini > GPT-4o**
   - Wszystkie etapy analityczne: gpt-4o-mini
   - Tylko generacja narracji: gpt-4o

### Token tracking
```python
# Każde wywołanie tracka tokeny
call_result = model.generate(
    prompt=prompt,
    track_cost=True
)

# Agregacja kosztów per job
job_cost = {
    "total_tokens": 125000,
    "mini_tokens": 80000,      # ~80% tokenów
    "gpt4_tokens": 45000,       # ~36% tokenów (ale ~90% kosztu)
    "total_cost_usd": 2.34
}
```

---

## 🐳 DOCKER-FIRST APPROACH

### Filozofia
- Docker = główne środowisko deweloperskie i testowe
- WSZYSTKIE testy muszą przejść w Docker
- Dopiero potem deployment gdzie indziej

### Stack
```yaml
# docker-compose.yml
services:
  narra_forge:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./output:/app/output
      - ./data:/app/data
    ports:
      - "8000:8000"  # API (opcjonalne)
```

### Testing w Docker
```bash
# Build
docker-compose build

# Test funkcjonalny
docker-compose run narra_forge python test_batch_production.py

# Test jakości
docker-compose run narra_forge python test_narrative_quality.py

# Test kosztowy
docker-compose run narra_forge python test_cost_tracking.py

# Test pełnego pipeline
docker-compose run narra_forge python test_full_pipeline.py
```

---

## 🎨 UX (PROSTY, PRODUKCYJNY)

### Zasada
**Użytkownik NIE pisze treści. Użytkownik ZLECA produkcję.**

### Interfejs
```
═══════════════════════════════════════════
         NARRA_FORGE - Batch Producer
═══════════════════════════════════════════

[1] TYP PRODUKCJI
    ○ Opowiadanie (5k-10k słów)
    ○ Nowela (10k-40k słów)
    ○ Powieść (40k-120k słów)
    ○ Saga (wielotomowa)

[2] GATUNEK
    ○ Fantasy
    ○ Sci-Fi
    ○ Horror
    ○ Thriller
    ○ Hybryda: [_________]

[3] INSPIRACJA (opcjonalnie)
    [____________________________________________]
    [____________________________________________]

[4] ŚWIAT (opcjonalnie)
    ○ Nowy świat
    ○ Istniejący: [wybierz z listy]

═══════════════════════════════════════════
[URUCHOM PRODUKCJĘ]
═══════════════════════════════════════════

Status: Oczekuje...
```

### Po uruchomieniu
```
═══════════════════════════════════════════
         PRODUKCJA W TOKU
═══════════════════════════════════════════

Job ID: NARR_20260115_183045

✓ Etap 1/10: Interpretacja zlecenia      [OK]
✓ Etap 2/10: Architektura świata         [OK]
✓ Etap 3/10: Architektura postaci        [OK]
✓ Etap 4/10: Struktura narracyjna        [OK]
✓ Etap 5/10: Plan segmentów              [OK]
⚙ Etap 6/10: Generacja tekstu            [W TOKU - 45%]
  Etap 7/10: Kontrola koherencji         [OCZEKUJE]
  Etap 8/10: Stylizacja językowa         [OCZEKUJE]
  Etap 9/10: Redakcja wydawnicza         [OCZEKUJE]
  Etap 10/10: Finalizacja                [OCZEKUJE]

Szacowany czas: ~8 minut
Koszt: ~$1.20 USD
═══════════════════════════════════════════
```

### Po zakończeniu
```
═══════════════════════════════════════════
         PRODUKCJA ZAKOŃCZONA
═══════════════════════════════════════════

✓ Narracja gotowa!

Pliki:
  📄 output/NARR_20260115_183045/narrative.txt
  🎧 output/NARR_20260115_183045/audiobook.txt
  📊 output/NARR_20260115_183045/metadata.json
  🌍 output/NARR_20260115_183045/world_export.json

Statystyki:
  Słowa: 8,547
  Tokeny użyte: 142,300
  Koszt: $1.18 USD
  Czas: 7m 32s
  Jakość: 0.94/1.0

[POBIERZ PLIKI] [NOWA PRODUKCJA] [EKSPANSJA]
═══════════════════════════════════════════
```

---

## 📊 METRYKI JAKOŚCI (AUTOMATYCZNE)

### Walidacja obowiązkowa
```python
QualityMetrics = {
    "coherence_score": 0.92,        # Min: 0.85
    "logical_consistency": True,    # Wymagane
    "psychological_consistency": True,  # Wymagane
    "temporal_consistency": True,   # Wymagane
    "language_quality": 0.89,       # Min: 0.80
    "narrative_weight": 0.91        # Min: 0.75
}

# Jeśli którakolwiek metryka FAIL -> produkcja NIE JEST zwrócona
# System retries lub failuje z diagnostyką
```

---

## 🚀 DEPLOYMENT FLOW

```
1. DEVELOPMENT (local)
   ↓
2. TESTING (Docker)
   ├─ Test funkcjonalny
   ├─ Test jakości narracyjnej
   ├─ Test kosztowy
   └─ Test wydajnościowy
   ↓
3. STAGING (Docker w środowisku staging)
   ↓
4. PRODUCTION (dowolne środowisko)
```

**Zasada:** Nic nie idzie do produkcji bez pełnego przejścia testów w Docker.

---

## 🔒 BEZPIECZEŃSTWO

### API Keys
```bash
# .env
OPENAI_API_KEY=sk-proj-...

# NIE commituj .env do git
# Używaj .env.example jako template
```

### Rate limiting
```python
# Automatyczny rate limiting dla OpenAI
RATE_LIMITS = {
    "gpt-4o-mini": {
        "rpm": 500,    # requests per minute
        "tpm": 200000  # tokens per minute
    },
    "gpt-4o": {
        "rpm": 100,
        "tpm": 80000
    }
}
```

---

## 📈 SCALABILITY

### Concurrent jobs
```python
# System obsługuje wiele jednoczesnych produkcji
# Każda produkcja = osobny job z osobnym ID

jobs = [
    orchestrator.produce_narrative_async(brief_1),
    orchestrator.produce_narrative_async(brief_2),
    orchestrator.produce_narrative_async(brief_3),
]

results = await asyncio.gather(*jobs)
```

### Long-running jobs
```python
# Dla długich form (powieści, sagi)
# Job może trwać 30-60 minut
# System musi obsłużyć:
# - persistence stanu
# - resume po crashu
# - progress tracking
```

---

## 🎯 PRIORYTETY IMPLEMENTACJI

### Faza 1: FUNDAMENT (Tydzień 1)
1. ✅ Struktura projektu
2. ✅ Docker setup
3. ✅ OpenAI client + model router
4. ✅ Konfiguracja
5. ✅ Typy danych

### Faza 2: CORE (Tydzień 2)
6. ✅ Potrójny system pamięci
7. ✅ World manager
8. ✅ Orchestrator (batch engine)

### Faza 3: AGENCI (Tydzień 3-4)
9. ✅ Wszystkie 10 agentów
10. ✅ Pipeline integration

### Faza 4: UX + TESTING (Tydzień 5)
11. ✅ Prosty UI
12. ✅ Testy Docker
13. ✅ Dokumentacja

---

## 🧪 TESTING STRATEGY

### Testy funkcjonalne
```bash
# Każdy agent osobno
pytest tests/test_agents/

# Cały pipeline
pytest tests/test_pipeline.py

# Integracja
pytest tests/test_integration.py
```

### Testy jakości
```bash
# Generuje narracje testowe i ocenia jakość
python tests/quality_tests/test_narrative_quality.py
```

### Testy kosztowe
```bash
# Sprawdza, czy koszty mieszczą się w budżecie
python tests/cost_tests/test_token_usage.py
```

---

## 📚 DOKUMENTACJA

### Dla użytkowników
- `README.md` - Quick start
- `USER_GUIDE.md` - Pełny przewodnik użytkownika

### Dla developerów
- `ARCHITECTURE_V2.md` - Ten dokument
- `API_REFERENCE.md` - Dokumentacja API
- `AGENT_SPECS.md` - Specyfikacja każdego agenta

---

## ⚡ KLUCZOWE ZASADY (PRZYPOMNENIE)

1. **OpenAI ONLY** - żadnych innych providerów
2. **Batch processing** - NIE streaming
3. **Docker-first** - testy w Docker lub wcale
4. **Mini domyślnie** - GPT-4o tylko dla narracji
5. **Streszczenia > Pełne teksty** - oszczędność tokenów
6. **Jakość nienaruszalna** - skala NIE obniża jakości
7. **Jeden cykl** - pełna produkcja, pełny wynik
8. **Multi-world** - obsługa wielu uniwersów
9. **Prosty UX** - nie chatbot, nie narzędzie, SILNIK

---

**To nie jest eksperyment. To jest system produkcyjny.**

**Zaprojektowany. Zbudowany. Działający.**

---

*Koniec specyfikacji architektury V2*
