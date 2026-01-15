# NARRA_FORGE V2 🚀

**Autonomiczny Batch Engine do Produkcji Narracji Wydawniczych**

[![Status](https://img.shields.io/badge/status-foundation-yellow.svg)](README.md)
[![Version](https://img.shields.io/badge/version-2.0.0--foundation-blue.svg)](README.md)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](README.md)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI%20Only-orange.svg)](README.md)

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

### ⏳ FAZA 2: AGENCI (NASTĘPNA)

W kolejnej iteracji:

- [ ] Implementacja wszystkich 10 agentów
- [ ] Pełne prompty w języku polskim
- [ ] Rzeczywista generacja narracji
- [ ] Walidacja jakości
- [ ] Logika retry i error handling

### 📅 FAZA 3: POLISH

- [ ] Prosty UI (CLI/Web)
- [ ] Kompletne testy
- [ ] Dokumentacja użytkownika
- [ ] Optymalizacja wydajności

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

**Uwaga:** To wersja foundation. Agenci są placeholderami. Rzeczywista generacja narracji zostanie dodana w Fazie 2.

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

### To jest wersja FOUNDATION

1. **Agenci są placeholderami.** Symulują pracę, ale nie generują prawdziwych narracji.

2. **Pełna implementacja w Fazie 2.** Następna iteracja doda:
   - Wszystkie 10 agentów z pełnymi promptami
   - Rzeczywistą generację narracji (polski język)
   - Walidację jakości
   - Error handling

3. **Architektura jest kompletna.** Fundament jest solidny i gotowy na agentów.

4. **System kosztów działa.** Tracking tokenów i kosztów jest funkcjonalny, choć obecnie symulowany.

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

### ⏳ Faza 2: AGENCI (NASTĘPNA - 2-3 tygodnie)
- [ ] Agent 01: Brief Interpreter (analiza zlecenia)
- [ ] Agent 02: World Architect (budowa świata)
- [ ] Agent 03: Character Architect (tworzenie postaci)
- [ ] Agent 04: Structure Designer (struktura narracyjna)
- [ ] Agent 05: Segment Planner (planowanie segmentów)
- [ ] Agent 06: Sequential Generator (generacja narracji)
- [ ] Agent 07: Coherence Validator (walidacja spójności)
- [ ] Agent 08: Language Stylizer (stylizacja polska)
- [ ] Agent 09: Editorial Reviewer (redakcja)
- [ ] Agent 10: Output Processor (finalizacja)
- [ ] Pełne prompty systemowe w języku polskim
- [ ] Walidacja jakości (coherence, logic, psychology, time)
- [ ] Retry logic i error handling

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

## ⭐ Status: FOUNDATION COMPLETE

**Fundament gotowy. Architektura solidna. Gotowy na agentów.**

**Następny krok:** Faza 2 - Implementacja wszystkich 10 agentów z pełnymi promptami.

---

**Zbudowane z precyzją. Zaprojektowane na wieczność.** 🚀

**NARRA_FORGE V2** - Synteza sztuki i inżynierii.
