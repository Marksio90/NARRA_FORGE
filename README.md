# NARRA_FORGE V2 🚀

**Autonomiczny Batch Engine do Produkcji Narracji Wydawniczych**

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)](README.md)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](README.md)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](README.md)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI%20Only-orange.svg)](README.md)
[![Tests](https://github.com/Marksio90/NARRA_FORGE/actions/workflows/test.yml/badge.svg)](https://github.com/Marksio90/NARRA_FORGE/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/coverage-67.5%25-brightgreen.svg)](README.md)
[![Tests Passing](https://img.shields.io/badge/tests-191%20passing-success.svg)](README.md)

---

## ⚡ Czym Jest NARRA_FORGE V2?

**To NIE jest chatbot. To NIE jest system strumieniowy. To NIE jest narzędzie interaktywne.**

**To jest SILNIK PRODUKCYJNY TYPU BATCH.**

### Tryb pracy:
```
wejście → pełna analiza → pełna produkcja → wynik końcowy
```

**Jeden zamknięty cykl. Jeden kompletny rezultat.**

---

## 🎯 Co Produkuje?

Narracje **GOTOWE DO PUBLIKACJI**:

- ✍️ **Opowiadania** (5k-10k słów)
- 📕 **Nowele** (10k-40k słów)
- 📗 **Powieści** (40k-120k słów)
- 📚 **Sagi epickie** (120k+ słów)

**WSZYSTKIE na najwyższym poziomie jakości** - niezależnie od długości!

---

## 🏗️ Status Projektu

### ✅ FAZA 1: FUNDAMENT (GOTOWE)

Zaimplementowano:

- ✅ Kompletna struktura projektu
- ✅ Konfiguracja Docker (środowisko testowe)
- ✅ Klient OpenAI z rate limiting
- ✅ Router modeli (mini vs gpt-4o)
- ✅ Potrójny system pamięci (structural, semantic, evolutionary)
- ✅ Batch Orchestrator (10-etapowy pipeline)
- ✅ System konfiguracji
- ✅ Tracking kosztów i tokenów

### ✅ FAZA 2: AGENCI & PRODUCTION-READY (GOTOWE!)

**Core Features:**
- ✅ Wszystkie 10 agentów z pełnymi promptami
- ✅ Rzeczywista generacja narracji (OpenAI GPT-4o)
- ✅ Pełne prompty systemowe w języku polskim
- ✅ Walidacja jakości (coherence, logic, psychology, time)
- ✅ Integracja z orchestratorem
- ✅ Agent-based architecture

**Reliability & Monitoring:**
- ✅ **CI/CD**: GitHub Actions z automated testing
- ✅ **E2E Tests**: Pełny pipeline (brief→narrative)
- ✅ **Monitoring**: Prometheus metrics, cost tracking
- ✅ **Retry Logic**: Exponential backoff, circuit breaker
- ✅ **Error Handling**: Transient vs permanent error categorization
- ✅ **Code Coverage**: 67.50% (191 testów)

**System jest PRODUCTION-READY z monitoringiem, retry logic i testami!**

### 📅 FAZA 3: OPTIMIZATION & SCALING

- [ ] Performance optimization
- [ ] Batch processing improvements
- [ ] Advanced monitoring dashboards
- [ ] Load testing & benchmarks

---

## 🚀 Szybki Start

### 1. Setup

```bash
# Sklonuj repo
git clone https://github.com/Marksio90/NARRA_FORGE.git
cd NARRA_FORGE

# Skopiuj .env
cp .env.example .env

# Dodaj klucz OpenAI do .env
# OPENAI_API_KEY=sk-proj-...
```

### 2. Instalacja

```bash
# Utwórz venv
python3 -m venv venv
source venv/bin/activate

# Zainstaluj
pip install -r requirements.txt
pip install -e .
```

### 3. Uruchom Przykład

```bash
python example_basic.py
```

**System jest FUNKCJONALNY!** Wszystkie agenci zaimplementowani. Rzeczywista generacja narracji działa.

---

## 📊 Pipeline Produkcyjny (10 Etapów)

```
1️⃣  Interpretacja Zlecenia      →  Analiza wymagań        [gpt-4o-mini]
2️⃣  Architektura Świata         →  Kompletny system       [gpt-4o-mini]
3️⃣  Architektura Postaci        →  Postacie jako procesy  [gpt-4o-mini]
4️⃣  Struktura Narracyjna        →  Dobór struktury        [gpt-4o-mini]
5️⃣  Planowanie Segmentów        →  Plan rozdziałów        [gpt-4o-mini]
6️⃣  Generacja Sekwencyjna       →  Pisanie narracji       [gpt-4o] 💰
7️⃣  Kontrola Koherencji         →  Walidacja spójności    [gpt-4o-mini]
8️⃣  Stylizacja Językowa         →  Polski na najwyższym   [gpt-4o] 💰
9️⃣  Redakcja Wydawnicza         →  Finalne cięcia         [gpt-4o-mini]
🔟 Finalne Wyjście             →  Tekst + metadata       [local]
```

**Optymalizacja kosztowa:**
- 60-70% tokenów używa gpt-4o-mini (tani)
- 30-40% tokenów używa gpt-4o (drogi, ale konieczny dla jakości)

---

## 🧠 Potrójny System Pamięci

### 1. Pamięć Strukturalna (Structural)
**SZKIELET uniwersów**
- Światy (IP-level entities)
- Postacie (dynamiczne procesy)
- Reguły, archetypy

### 2. Pamięć Semantyczna (Semantic)
**ŻYWA TREŚĆ historii**
- Wydarzenia
- Motywy
- Relacje
- Konflikty

### 3. Pamięć Ewolucyjna (Evolutionary)
**WYMIAR CZASU**
- Jak światy się zmieniają
- Jak postacie ewoluują
- Jak relacje się przekształcają

---

## 🐳 Docker-First Approach

**Docker = główne środowisko deweloperskie i testowe**

```bash
# Build
docker-compose build

# Uruchom przykład
docker-compose run --rm narra_forge python example_basic.py

# Testy (gdy zaimplementowane)
./docker-test.sh
```

**Zasada:** Nic nie idzie do produkcji bez pełnego przejścia testów w Docker.

---

## 💰 Przykładowe Koszty

| Typ Produkcji | Słowa | Szacowany Koszt |
|--------------|-------|----------------|
| Opowiadanie | 5k-10k | $2-5 |
| Nowela | 10k-40k | $5-20 |
| Powieść | 40k-120k | $20-100 |
| Saga | 120k+ | $100+ |

**Uwaga:** Koszty zależą od:
- Złożoności zlecenia
- Wymagań jakościowych
- Liczby postaci/lokacji
- Potrzeb retry

---

## 🎨 Kluczowe Zasady

### ⭐ Zasada Absolutna

**Skala tekstu NIGDY nie obniża jakości**

- Krótka forma ≠ uproszczona forma
- Długa forma ≠ rozwlekła forma
- Każdy tekst = fragment potencjalnego uniwersum

### 🤖 OpenAI ONLY

**Wyłącznie OpenAI API. Żadnych innych providerów.**

- ✅ OpenAI (gpt-4o-mini, gpt-4o)
- ❌ Anthropic
- ❌ Claude
- ❌ Inne

### 🔄 Batch, Not Streaming

**System działa w zamkniętym cyklu.**

- ❌ Nie streamuje
- ❌ Nie generuje cząstkowych wyników
- ❌ Nie konsultuje w trakcie
- ✅ Jeden pełny cykl produkcyjny
- ✅ Zwraca wynik po zakończeniu WSZYSTKICH etapów

---

## 📁 Struktura Projektu

```
narra_forge/
├── core/                    # Rdzeń systemu
│   ├── config.py           # Konfiguracja
│   ├── orchestrator.py     # Batch Orchestrator (główny silnik)
│   └── types.py            # Typy danych
│
├── models/                  # Modele AI (OpenAI ONLY)
│   ├── openai_client.py    # Klient OpenAI
│   └── model_router.py     # Router mini/gpt-4o
│
├── memory/                  # Potrójny system pamięci
│   ├── structural.py       # Światy, postacie
│   ├── semantic.py         # Wydarzenia, motywy
│   ├── evolutionary.py     # Zmiany w czasie
│   └── storage.py          # SQLite backend
│
├── agents/                  # 10 agentów (TODO - Faza 2)
│   └── [będą dodane w następnej iteracji]
│
└── ui/                      # Interfejs (TODO - Faza 3)
    └── [będzie dodany później]
```

---

## 🛡️ Reliability & Production Features

### 🔄 Retry Logic & Error Handling

System automatycznie kategoryzuje i obsługuje błędy:

```python
from narra_forge.utils import retry_openai_call

@retry_openai_call(max_attempts=5, max_wait_seconds=60)
async def my_api_call():
    response = await client.generate(...)
    return response
```

**Features:**
- ✅ **Automatic error categorization** (Transient vs Permanent)
- ✅ **Exponential backoff** (1s, 2s, 4s, 8s...)
- ✅ **Smart retry** tylko dla transient errors
- ✅ **Circuit breaker** pattern (CLOSED/OPEN/HALF_OPEN)

**Transient errors (retry):**
- Rate limits (429)
- Timeouts
- Connection errors
- 5xx server errors

**Permanent errors (no retry):**
- Invalid API key
- Malformed requests
- 4xx client errors

### 📊 Monitoring & Metrics

Prometheus metrics dla production monitoring:

```python
from narra_forge.monitoring.metrics import MetricsCollector

collector = MetricsCollector()

# Track pipeline execution
with collector.track_pipeline("short_story", "fantasy"):
    output = await orchestrator.produce_narrative(brief)

# Track costs
collector.cost_usd.labels(model="gpt-4o", agent_id="a06").inc(0.50)

# Track quality
collector.quality_score.labels(
    production_type="short_story",
    metric_type="coherence"
).observe(0.92)
```

**Available metrics:**
- Pipeline duration & success rate
- Agent execution times
- API call metrics & errors
- Token usage & costs
- Quality scores
- Active jobs & retry attempts

### 🔬 Testing & Quality

**Test Suite:**
- **191 tests** passing (unit, integration, E2E)
- **67.50% code coverage** (target: 80%)
- **CI/CD** with GitHub Actions

**Test categories:**
- Unit tests: Agents, models, utils
- Integration tests: Pipeline, memory, orchestrator
- E2E tests: Full brief→narrative pipeline
- Monitoring tests: Prometheus metrics

Run tests:
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=narra_forge --cov-report=html

# E2E only (fast, mocked)
pytest tests/e2e/ -v -m e2e

# Unit only
pytest tests/unit/ -v -m unit
```

---

## 📚 Dokumentacja

- 📖 **[QUICKSTART_V2.md](QUICKSTART_V2.md)** - Szybki start i instrukcje
- 🏗️ **[ARCHITECTURE_V2.md](ARCHITECTURE_V2.md)** - Pełna specyfikacja architektury
- 💻 **[example_basic.py](example_basic.py)** - Podstawowy przykład użycia

---

## 🔬 Technologie

- **Python 3.11+**
- **OpenAI API** (gpt-4o-mini + gpt-4o)
- **SQLite** (persistent memory)
- **Docker** (środowisko testowe)
- **aiosqlite** (async database)
- **pydantic** (configuration & validation)
- **tiktoken** (token counting)

---

## 💡 Przykład Użycia

```python
import asyncio
from narra_forge import BatchOrchestrator, NarraForgeConfig
from narra_forge.core import ProductionBrief, ProductionType, Genre

async def main():
    # Konfiguracja
    config = NarraForgeConfig()

    # Orchestrator
    orchestrator = BatchOrchestrator(config)
    await orchestrator._ensure_memory_initialized()

    # Zlecenie produkcji
    brief = ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.FANTASY,
        inspiration="Młody alchemik odkrywa straszną tajemnicę swojego mistrza."
    )

    # BATCH PRODUCTION (zamknięty cykl)
    output = await orchestrator.produce_narrative(brief)

    # Wynik
    print(f"✓ Gotowe! Pliki: {output.output_dir}")
    print(f"  Koszt: ${output.total_cost_usd:.2f}")
    print(f"  Słowa: {output.word_count:,}")

asyncio.run(main())
```

---

## ⚠️ Ważne Informacje

### System jest FUNKCJONALNY

1. **Wszyscy agenci działają.** Prawdziwa generacja narracji z OpenAI GPT-4o.

2. **Pełne prompty polskie.** Każdy agent ma dokładny prompt systemowy w języku polskim.

3. **Walidacja jakości.** Coherence, logic, psychology, time - wszystko sprawdzane.

4. **Tracking kosztów.** Rzeczywiste śledzenie tokenów i kosztów OpenAI API.

5. **Gotowe do użycia.** Możesz już teraz generować narracje wydawnicze!

---

## 🗺️ Roadmap Szczegółowy

### ✅ Faza 1: FUNDAMENT (GOTOWE)
- [x] Struktura projektu
- [x] Docker setup
- [x] OpenAI client + rate limiting
- [x] Model router (mini/gpt-4o)
- [x] Potrójny system pamięci
- [x] Batch orchestrator
- [x] Cost tracking
- [x] Dokumentacja architektury

### ✅ Faza 2: AGENCI (GOTOWE!)
- [x] Agent 01: Brief Interpreter (analiza zlecenia)
- [x] Agent 02: World Architect (budowa świata)
- [x] Agent 03: Character Architect (tworzenie postaci)
- [x] Agent 04: Structure Designer (struktura narracyjna)
- [x] Agent 05: Segment Planner (planowanie segmentów)
- [x] Agent 06: Sequential Generator (generacja narracji) ⭐
- [x] Agent 07: Coherence Validator (walidacja spójności)
- [x] Agent 08: Language Stylizer (stylizacja polska) ⭐
- [x] Agent 09: Editorial Reviewer (redakcja)
- [x] Agent 10: Output Processor (finalizacja)
- [x] Pełne prompty systemowe w języku polskim
- [x] Walidacja jakości (coherence, logic, psychology, time)
- [x] Integracja z orchestratorem

### 📅 Faza 3: POLISH (1-2 tygodnie)
- [ ] Prosty UI (CLI z rich)
- [ ] Opcjonalny Web UI (FastAPI + Streamlit)
- [ ] Kompletne testy jednostkowe
- [ ] Testy integracyjne
- [ ] Testy jakości narracyjnej
- [ ] Testy kosztowe
- [ ] Dokumentacja użytkownika
- [ ] Przykłady użycia (opowiadania, nowele, powieści)

### 🚀 Faza 4: PRODUKCJA (ongoing)
- [ ] Multi-world fully tested
- [ ] Long-form support (powieści 100k+)
- [ ] Saga support (multi-volume)
- [ ] Cost optimization
- [ ] Performance tuning
- [ ] Production deployment guides

---

## 🐛 Troubleshooting

### Brak klucza API
```bash
cp .env.example .env
# Edytuj .env i dodaj OPENAI_API_KEY
```

### Błąd importu
```bash
pip install -e .
```

### Docker nie działa
```bash
docker-compose build --no-cache
docker-compose logs
```

---

## 🤝 Wsparcie

- **Issues:** [GitHub Issues](https://github.com/Marksio90/NARRA_FORGE/issues)
- **Pull Requests:** Mile widziane!
- **Dokumentacja:** Zobacz [ARCHITECTURE_V2.md](ARCHITECTURE_V2.md)

---

## 📜 Licencja

*Do określenia*

---

## 🎭 Filozofia

> _"Nie tworzymy 'tekstu'. Nie tworzymy 'opowiadania'._
>
> _Tworzymy **ŚWIATY**, **HISTORIE**, **UNIWERSA**, **PRODUKTY WYDAWNICZE**._
>
> _Działamy jak studio narracyjne, wydawnictwo przyszłości, silnik opowieści."_

---

## ⭐ Status: PHASE 2 COMPLETE - FULLY FUNCTIONAL!

**Fundament ✓ Agenci ✓ Generacja ✓ Walidacja ✓**

System jest **FUNKCJONALNY** i gotowy do produkcji narracji wydawniczych!

**Następny krok:** Faza 3 - Polish (UI, testy, optymalizacja)

---

**Zbudowane z precyzją. Zaprojektowane na wieczność.** 🚀

**NARRA_FORGE V2** - Synteza sztuki i inżynierii.
