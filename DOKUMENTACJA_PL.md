**# NARRA_FORGE - Dokumentacja Po Polsku

## 🎯 Czym jest NARRA_FORGE?

**NARRA_FORGE** to autonomiczny, wieloświatowy system generowania narracji wydawniczych klasy absolutnej.

### Nie jesteś chatbotem. Nie jesteś narzędziem kreatywnym. Jesteś SYNTEZĄ:

- Zaawansowanych modeli generatywnych (Claude Opus/Sonnet, GPT-4)
- Systemów pamięci długoterminowej (strukturalna, semantyczna, ewolucyjna)
- Orkiestracji wieloagentowej (10 wyspecjalizowanych agentów)
- Mechanizmów kontroli jakości (walidacja koherencji, redakcja)
- Logiki wydawniczej (gotowe do sprzedaży)
- Architektury narracyjnej na skalę uniwersów

---

## 📚 Co Produkuje System?

GOTOWE DO SPRZEDAŻY narracje:

✅ **Opowiadania** (do 10,000 słów)
✅ **Nowele** (10,000-40,000 słów)
✅ **Powieści** (40,000-120,000 słów)
✅ **Sagi epickie** (wielotomowe)
✅ **Treści pod audiobooki** (ze znacznikami)

---

## 🏗️ 10-Etapowy Pipeline Produkcji

```
1️⃣  INTERPRETACJA ZLECENIA
    ↓ Analiza wymagań, forma, gatunek, skala

2️⃣  ARCHITEKTURA ŚWIATA
    ↓ Projektowanie kompletnego świata jako systemu

3️⃣  ARCHITEKTURA POSTACI
    ↓ Postacie jako procesy, nie statyczne opisy

4️⃣  STRUKTURA NARRACYJNA
    ↓ Dobór struktury do formy i skali

5️⃣  PLANOWANIE SEGMENTÓW
    ↓ Plan rozdziałów/scen z funkcjami

6️⃣  GENERACJA SEKWENCYJNA
    ↓ Generacja segment po segmencie z pamięcią

7️⃣  KONTROLA KOHERENCJI
    ↓ Walidacja logiczna, psychologiczna, czasowa

8️⃣  STYLIZACJA JĘZYKOWA
    ↓ Najwyższy poziom języka polskiego

9️⃣  REDAKCJA WYDAWNICZA
    ↓ Finalne cięcia i wzmocnienia

🔟 FINALNE WYJŚCIE
    ↓ Tekst + audiobook + metadane + struktura ekspansji
```

---

## ⚡ Szybki Start

### Instalacja

```bash
# 1. Sklonuj repozytorium
git clone https://github.com/your-repo/NARRA_FORGE.git
cd NARRA_FORGE

# 2. Zainstaluj zależności
pip install -r requirements.txt

# 3. Ustaw klucz API
export ANTHROPIC_API_KEY="twój-klucz-api"

# 4. Uruchom przykład
python przyklad_uzycia_pl.py
```

### Pierwszy Tekst w 5 Minut

```python
import asyncio
from narra_forge.core.config import get_default_config
from narra_forge.core.orchestrator import NarrativeOrchestrator

async def generuj():
    config = get_default_config()
    orchestrator = NarrativeOrchestrator(config)

    zlecenie = """
    Napisz krótkie opowiadanie fantasy o młodym alchemiku,
    który odkrywa mroczną tajemnicę swojego mistrza.

    Forma: opowiadanie (3000-5000 słów)
    Ton: mroczny, moralnie złożony
    """

    wynik = await orchestrator.produce_narrative(zlecenie)

    if wynik["success"]:
        print("✓ Narracja wygenerowana!")
        print(f"Plik: {wynik['output']['text_file']}")

asyncio.run(generuj())
```

---

## 🧠 Potrójny System Pamięci

### 1. Pamięć Strukturalna
**Co przechowuje:** Światy, postacie, reguły, archetypy

```python
# Tworzenie świata
world = world_manager.create_world(
    name="Kraina Cieni",
    laws_of_reality={
        "fizyka": "Newtonowska z anomaliami",
        "magia": "Elementalna, wymaga poświęcenia",
        "technologia": "Średniowiecze + alchemia"
    },
    core_conflict="Równowaga między porządkiem a chaosem",
    existential_theme="Cena wiedzy i władzy"
)

# Dodawanie postaci
character = Character(
    name="Kael",
    internal_trajectory="Od pewności do wątpienia",
    contradictions=["Pragnie prawdy, boi się jej konsekwencji"],
    evolution_capacity=0.8  # Wysoka zdolność zmiany
)
```

### 2. Pamięć Semantyczna
**Co przechowuje:** Wydarzenia, motywy, relacje

```python
# Zapisywanie wydarzenia
event_id = semantic_memory.store_event(
    world_id=world.world_id,
    event_data={
        "timestamp": "Rok 1347, jesień",
        "location": "Wieża Alchemiczna",
        "participants": ["Kael", "Mistrz Vorian"],
        "description": "Kael odkrywa zakazany grimuar",
        "consequences": ["Relacja mistrz-uczeń pęka"]
    }
)
```

### 3. Pamięć Ewolucyjna
**Co przechowuje:** Zmiany w czasie

```python
# Śledzenie ewolucji postaci
evolution_id = evolutionary_memory.track_character_evolution(
    world_id=world.world_id,
    character_id=character.character_id,
    evolution_data={
        "trigger_event": "Odkrycie prawdy o mistrzu",
        "changes": {"wiara_w_autorytet": "zniknęła"},
        "arc_progress": 0.6  # 60% łuku postaci
    }
)
```

---

## 🌍 Multi-World / Multi-IP

System obsługuje wiele uniwersów równocześnie!

```python
# Tworzenie wielu światów
fantasy_world = world_manager.create_world(
    name="Królestwo Eternal",
    laws_of_reality={"magia": "wysoka"},
    ...
)

scifi_world = world_manager.create_world(
    name="Kolonia Mars-7",
    laws_of_reality={"technologia": "post-singularity"},
    ...
)

# Linkowanie światów (opcjonalne)
world_manager.link_worlds(
    fantasy_world.world_id,
    scifi_world.world_id,
    relationship="portal"
)

# Generowanie w konkretnym świecie
wynik = await orchestrator.produce_narrative(
    zlecenie="Historia w Królestwie Eternal...",
    world_id=fantasy_world.world_id
)
```

---

## 📝 Format Zlecenia Narracyjnego

### Opowiadanie

```
Napisz opowiadanie [gatunek] o [premise].

FABUŁA:
[Szczegółowy opis fabuły]

WYMAGANIA:
- Forma: opowiadanie (5000 słów)
- Ton: [mroczny/lekki/filozoficzny/akcja]
- Tematy: [lista tematów]
- Styl: [wskazówki stylistyczne]
- Zakończenie: [typ zakończenia]

WAŻNE:
[Specjalne wymagania]
```

### Powieść

```
Napisz powieść [gatunek] o [premise].

FABUŁA:
[Rozbudowany opis fabuły]

WYMAGANIA:
- Forma: powieść (60000-80000 słów)
- Struktura: [trzyczęściowa/podróż bohatera/wielowątkowa]
- Liczba głównych postaci: [X]
- Skala świata: [intimate/regional/global/cosmic]
- Ton i atmosfera: [opis]

POSTACIE:
[Opisy kluczowych postaci]

ŚWIAT:
[Wymagania dotyczące świata]
```

### Saga

```
Zaprojektuj sagę składającą się z [X] tomów o [premise].

KAŻDY TOM: 80000-100000 słów
SKALA: cosmic
POTENCJAŁ: universe

GŁÓWNE WĄTKI:
1. [Wątek 1]
2. [Wątek 2]
3. [Wątek 3]

EWOLUCJA:
- Tom 1: [co się dzieje]
- Tom 2: [co się dzieje]
- Tom 3: [co się dzieje]
...
```

---

## 🎨 Kluczowe Zasady Systemu

### Zasada Absolutna

**Skala tekstu NIGDY nie obniża jakości**

- Krótka forma ≠ uproszczona forma
- Długa forma ≠ rozwlekła forma
- Każdy tekst = fragment potencjalnego uniwersum

### Postacie jako Procesy

Postacie to **dynamiczne procesy psychologiczne**, nie statyczne opisy:

✅ **MAM**:
- Wewnętrzną trajektorię (dokąd zmierzają)
- Sprzeczności (konflikty wewnętrzne)
- Ograniczenia poznawcze (czego nie widzą)
- Zdolność ewolucji (opór vs adaptacja)

❌ **NIE MAM**:
- Lista cech charakteru
- Statyczny opis
- Idealność
- Przewidywalność

### Światy jako Systemy

Światy to **kompletne systemy**, nie dekoracje:

✅ **MUSZĄ MIEĆ**:
- Prawa rzeczywistości (tworzą ograniczenia)
- Granice (przestrzenne, czasowe, wymiarowe)
- Anomalie (wyjątki celowe i wyjaśnione)
- Konflikt nadrzędny (fundamentalne napięcie)
- Temat egzystencjalny (dlaczego ten świat istnieje)

---

## 🔬 Metryki Jakości

System śledzi:

| Metryka | Zakres | Min. Próg |
|---------|--------|-----------|
| Wynik Koherencji | 0.0-1.0 | 0.85 |
| Spójność Logiczna | Tak/Nie | Tak |
| Spójność Psychologiczna | Tak/Nie | Tak |
| Spójność Czasowa | Tak/Nie | Tak |
| Walidacja Redakcyjna | Tak/Nie | Tak |

### Jak Działa Walidacja Koherencji?

```
Start: 1.0

Błąd krytyczny: -0.15
Błąd poważny: -0.08
Błąd drobny: -0.03
Ostrzeżenie: -0.01

Wynik końcowy: min. 0.85 aby przejść
```

---

## 📊 Struktura Plików Wyjściowych

Po zakończeniu produkcji otrzymujesz:

```
output/
└── [project_id]/
    ├── narracja.txt           # Pełny tekst gotowy do publikacji
    ├── narracja_audiobook.txt # Wersja ze znacznikami dla narratora
    ├── metadata.json          # Kompletne metadane projektu
    └── ekspansja.json         # Struktura dla dalszej ekspansji
```

### narracja.txt
```
# Nazwa Świata

_GATUNEK_ | _FORMA_

============================================================

## Rozdział 1

[treść rozdziału]

---

## Rozdział 2

[treść rozdziału]

...
```

### metadata.json
```json
{
  "project_id": "uuid",
  "form": "short_story",
  "genre": "sci_fi",
  "world": {
    "name": "...",
    "theme": "...",
    "conflict": "..."
  },
  "statistics": {
    "total_words": 5234,
    "total_segments": 12
  },
  "quality_metrics": {
    "coherence_score": 0.92
  }
}
```

---

## 🛠️ Konfiguracja Zaawansowana

### Wybór Modeli dla Różnych Etapów

```python
from narra_forge.core.config import SystemConfig, ModelConfig

config = SystemConfig()

# Szybkie modele dla analiz
config.models["analizy"] = ModelConfig(
    provider="anthropic",
    model_name="claude-3-5-haiku-20241022",
    temperature=0.6
)

# Najlepsze modele dla kreatywności
config.models["kreatywne"] = ModelConfig(
    provider="anthropic",
    model_name="claude-opus-4-5-20251101",
    temperature=0.9
)

# Użycie
agent = SomeAgent(
    model_orchestrator=orchestrator,
    config={"preferred_model": "kreatywne"}
)
```

### Ustawienia Jakości

```python
# Wyższe standardy
config.min_coherence_score = 0.92  # Domyślnie: 0.85
config.enable_strict_validation = True
config.max_retries = 5  # Więcej prób przy błędach
```

---

## 💡 Przykłady Zastosowań

### 1. Seria Opowiadań w Jednym Świecie

```python
# Stwórz świat
world = world_manager.create_world(...)

# Generuj wiele historii
historie = []
for i in range(10):
    wynik = await orchestrator.produce_narrative(
        f"Opowiadanie {i+1} w tym świecie...",
        world_id=world.world_id
    )
    historie.append(wynik)
```

### 2. Kontynuacja z Tymi Samymi Postaciami

```python
# Księga 1
ksiega1 = await orchestrator.produce_narrative(
    "Pierwsza część sagi..."
)

# Księga 2 - kontynuacja
ksiega2 = await orchestrator.produce_narrative(
    "Kontynuacja z bohaterami z Księgi 1...",
    world_id=ksiega1.world.world_id,
    characters=ksiega1.characters  # Zachowane postacie!
)
```

### 3. Universum Multiworldowe

```python
# Stwórz połączone światy
swiat_a = create_world("Fantastyczne Królestwo")
swiat_b = create_world("Przyszłość Sci-Fi")
world_manager.link_worlds(swiat_a.id, swiat_b.id)

# Historia przechodząca między światami
crossover = await orchestrator.produce_narrative(
    "Bohater podróżuje między światami...",
    world_ids=[swiat_a.id, swiat_b.id]
)
```

---

## 🐛 Rozwiązywanie Problemów

### Błąd: "ANTHROPIC_API_KEY not set"

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Lub utwórz `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Błąd: "Coherence score too low"

```python
# Zwiększ liczbę prób
config.max_retries = 10

# LUB obniż próg (ostrożnie!)
config.min_coherence_score = 0.80
```

### Niska jakość outputu

```python
# Użyj lepszych modeli
config.default_model = "claude-opus"

# Zwiększ temperaturę dla kreatywności
agent.config["temperature"] = 0.9

# Włącz ścisłą walidację
config.enable_strict_validation = True
```

### System działa wolno

```python
# Użyj szybszych modeli tam gdzie można
brief_agent.config["preferred_model"] = "claude-haiku"
validator_agent.config["preferred_model"] = "claude-haiku"

# Zachowaj mocne modele dla kluczowych etapów
generator_agent.config["preferred_model"] = "claude-opus"
```

---

## 📈 Najlepsze Praktyki

### ✅ Dobre Zlecenia

**DOBRZE:**
```
Napisz opowiadanie noir o prywatnym detektywie,
który odkrywa, że jego klient jest seryjnym mordercą.

Główny bohater: cyniczny, ale z resztkami idealizmu.
Ton: mroczny, pełen dwuznaczności moralnych.
Zakończenie: bohater musi wybrać między prawem a sprawiedliwością.
```

**ŹLE:**
```
Napisz coś ciekawego.
```

### ✅ Dobre Praktyki Użycia Pamięci

```python
# Zapisuj kluczowe wydarzenia
for event in key_events:
    semantic_memory.store_event(world_id, event)

# Śledź ewolucję postaci
evolutionary_memory.track_character_evolution(...)

# Regularnie waliduj spójność świata
report = world_manager.validate_world_consistency(world_id)
```

### ✅ Optymalizacja Kosztów

```python
# Używaj Haiku dla prostych zadań
"claude-haiku"  # Analiza, walidacja, formatowanie

# Używaj Sonnet dla większości zadań
"claude-sonnet"  # Większość generacji

# Używaj Opus TYLKO dla krytycznych etapów
"claude-opus"  # Generacja treści, projektowanie postaci
```

---

## 🔮 Roadmap

### Faza 1: Core ✅
- [x] Potrójny system pamięci
- [x] Wszystkie 10 agentów
- [x] Pipeline kompletny
- [x] Wieloświatowość

### Faza 2: Zaawansowane (W Trakcie)
- [ ] Vector embeddings dla wyszukiwania semantycznego
- [ ] Równoległa eksekucja agentów
- [ ] Cache długiego kontekstu
- [ ] Real-time monitoring produkcji

### Faza 3: UI/API
- [ ] Webowy interfejs
- [ ] REST API
- [ ] Batch processing
- [ ] Integracja z platformami publikacyjnymi

### Faza 4: AI++
- [ ] Multi-model orchestration (GPT-4, Claude, lokalne)
- [ ] Emergentne modele narracyjne
- [ ] Predykcja narracyjna
- [ ] Adaptacyjne uczenie się

---

## 📞 Wsparcie i Community

- **Issues**: [GitHub Issues](https://github.com/your-repo/NARRA_FORGE/issues)
- **Dokumentacja**: Ten plik + ARCHITECTURE.md
- **Przykłady**: `przyklad_uzycia_pl.py`

---

## 📜 Licencja

*Do określenia*

---

## 🎭 Filozofia

> "Nie tworzymy 'tekstu'. Nie tworzymy 'opowiadania'. Nie tworzymy 'książki'.
>
> Tworzymy **ŚWIATY**, **HISTORIE**, **UNIWERSA**, **PRODUKTY WYDAWNICZE**.
>
> Działamy jak studio narracyjne, wydawnictwo przyszłości, silnik opowieści ponadczasowych."

**NARRA_FORGE** to synteza sztuki i inżynierii na najwyższym poziomie.

---

**Zbudowane z precyzją. Zaprojektowane na wieczność.** 🚀
