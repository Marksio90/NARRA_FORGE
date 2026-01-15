# NARRA_FORGE 🚀

**Autonomiczny Wieloświatowy System Generowania Narracji Klasy Absolutnej**

[![Polski](https://img.shields.io/badge/język-Polski-red.svg)](README.md)
[![English](https://img.shields.io/badge/lang-English-blue.svg)](README_EN.md)

---

## 📖 Czym Jest NARRA_FORGE?

**NARRA_FORGE** to nie chatbot. To nie narzędzie kreatywne. To nie pojedynczy model.

To **SYNTEZA**:
- 🧠 Zaawansowanych modeli generatywnych (Claude Opus/Sonnet, GPT-4)
- 💾 Systemów pamięci długoterminowej (strukturalna, semantyczna, ewolucyjna)
- 🤖 Orkiestracji wieloagentowej (10 wyspecjalizowanych agentów)
- ✅ Mechanizmów kontroli jakości
- 📚 Logiki wydawniczej
- 🌍 Architektury narracyjnej na skalę uniwersów

---

## 🎯 Co Produkuje?

Narracje **GOTOWE DO SPRZEDAŻY**:

- ✍️ **Opowiadania** (do 10,000 słów)
- 📕 **Nowele** (10,000-40,000 słów)
- 📗 **Powieści** (40,000-120,000 słów)
- 📚 **Sagi epickie** (wielotomowe)
- 🎧 **Audiobooki** (ze znacznikami dla narratora)

**WSZYSTKIE na najwyższym poziomie jakości** - niezależnie od długości!

---

## ⚡ Szybki Start

```bash
# 1. Instalacja
pip install -r requirements.txt

# 2. Klucz API
export ANTHROPIC_API_KEY="twój-klucz"

# 3. Uruchom przykład
python przyklad_uzycia_pl.py
```

### Twoja Pierwsza Narracja w 3 Minuty:

```python
import asyncio
from narra_forge.core.config import get_default_config
from narra_forge.core.orchestrator import NarrativeOrchestrator

async def generuj():
    config = get_default_config()
    orchestrator = NarrativeOrchestrator(config)

    zlecenie = """
    Napisz mroczne opowiadanie fantasy o młodym alchemiku,
    który odkrywa straszną tajemnicę swojego mistrza.

    Forma: opowiadanie (5000 słów)
    Ton: mroczny, moralnie złożony
    """

    wynik = await orchestrator.produce_narrative(zlecenie)

    if wynik["success"]:
        print(f"✅ Gotowe! Plik: {wynik['output']['text_file']}")

asyncio.run(generuj())
```

---

## 🏗️ Pipeline Produkcji (10 Etapów)

```
1️⃣  Interpretacja Zlecenia      →  Analiza wymagań
2️⃣  Architektura Świata         →  Kompletny system świata
3️⃣  Architektura Postaci        →  Postacie jako procesy
4️⃣  Struktura Narracyjna        →  Dobór struktury
5️⃣  Planowanie Segmentów        →  Plan rozdziałów/scen
6️⃣  Generacja Sekwencyjna       →  Pisanie z pamięcią
7️⃣  Kontrola Koherencji         →  Walidacja spójności
8️⃣  Stylizacja Językowa         →  Najwyższy poziom PL
9️⃣  Redakcja Wydawnicza         →  Finalne cięcia
🔟 Finalne Wyjście             →  Tekst + audiobook + meta
```

---

## 🧠 Potrójny System Pamięci

### 1. **Pamięć Strukturalna**
Światy, postacie, reguły, archetypy - SZKIELET uniwersów

### 2. **Pamięć Semantyczna**
Wydarzenia, motywy, relacje - ŻYWA TREŚĆ historii

### 3. **Pamięć Ewolucyjna**
Jak światy i postacie się ZMIENIAJĄ w czasie

---

## 🌍 Multi-World / Multi-IP

System obsługuje **wiele uniwersów równocześnie**:

```python
# Twórz wiele światów
fantasy_world = world_manager.create_world("Królestwo Eternal", ...)
scifi_world = world_manager.create_world("Kolonia Mars-7", ...)

# Linkuj je (opcjonalnie)
world_manager.link_worlds(fantasy_world.id, scifi_world.id)

# Generuj w konkretnym świecie
wynik = await orchestrator.produce_narrative(
    "Historia w Królestwie Eternal...",
    world_id=fantasy_world.world_id
)
```

---

## 🎨 Kluczowe Zasady

### ⭐ Zasada Absolutna

**Skala tekstu NIGDY nie obniża jakości**

- Krótka forma ≠ uproszczona forma
- Długa forma ≠ rozwlekła forma
- Każdy tekst = fragment potencjalnego uniwersum

### 👤 Postacie jako Procesy

Nie statyczne opisy, ale **dynamiczne procesy psychologiczne**:
- Wewnętrzne trajektorie
- Sprzeczności i konflikty
- Ograniczenia poznawcze
- Zdolność ewolucji

### 🌍 Światy jako Systemy

Nie dekoracje, ale **kompletne systemy**:
- Prawa rzeczywistości (tworzą ograniczenia)
- Granice przestrzenne/czasowe/wymiarowe
- Anomalie (celowe wyjątki)
- Konflikt nadrzędny
- Temat egzystencjalny

---

## 📊 Metryki Jakości

| Metryka | Min. Próg |
|---------|-----------|
| Wynik Koherencji | 0.85/1.0 |
| Spójność Logiczna | ✅ TAK |
| Spójność Psychologiczna | ✅ TAK |
| Spójność Czasowa | ✅ TAK |

---

## 📁 Co Otrzymujesz?

Po produkcji otrzymujesz:

```
output/[project_id]/
├── narracja.txt           # Tekst publikacyjny
├── narracja_audiobook.txt # Wersja z znacznikami
├── metadata.json          # Kompletne metadane
└── ekspansja.json         # Struktura ekspansji
```

---

## 📚 Dokumentacja

- 📖 **[DOKUMENTACJA_PL.md](DOKUMENTACJA_PL.md)** - Pełna dokumentacja po polsku
- 🚀 **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- 🏗️ **[ARCHITECTURE.md](ARCHITECTURE.md)** - Dokumentacja techniczna
- 💻 **[przyklad_uzycia_pl.py](przyklad_uzycia_pl.py)** - Kompletny przykład

---

## 🔬 Technologie

- **Python 3.11+**
- **Claude Opus 4.5 / Sonnet 4.5** - Główne modele
- **OpenAI GPT-4** - Alternatywa/fallback
- **SQLite** - Persistent memory
- **Architektura model-agnostic** - Gotowa na przyszłość

---

## 💎 Charakterystyka

### ✅ Ma:
- Kompletny pipeline 10-etapowy
- Wszystkie agenty zaimplementowane
- Polski system prompt dla każdego agenta
- Walidacja koherencji
- Pamięć długoterminowa
- Multi-world support
- Format audiobook
- Metadane i ekspansja

### 🚀 Gotowe:
- Generowanie opowiadań
- Generowanie nowel
- Generowanie powieści
- Generowanie sag
- Wieloświatowość
- Produkcja publikacyjna

---

## 🎯 Przykłady Zastosowań

### 📖 Seria w Jednym Świecie
```python
world = world_manager.create_world(...)
for i in range(10):
    story = await produce_narrative(f"Historia {i}...", world_id=world.id)
```

### 📚 Kontynuacja z Postaciami
```python
book1 = await produce_narrative("Księga 1...")
book2 = await produce_narrative(
    "Księga 2...",
    world_id=book1.world.id,
    characters=book1.characters  # TE SAME postacie!
)
```

### 🌌 Multi-Universe
```python
world_a = create_world("Fantasy")
world_b = create_world("Sci-Fi")
link_worlds(world_a.id, world_b.id)

crossover = await produce_narrative(
    "Podróż między światami...",
    world_ids=[world_a.id, world_b.id]
)
```

---

## 🛠️ Konfiguracja

### Wybór Modeli
```python
# Szybkie dla analiz
config.models["haiku"] = ModelConfig(...)

# Kreatywne dla generacji
config.models["opus"] = ModelConfig(...)

# Użycie
agent.config["preferred_model"] = "opus"
```

### Jakość
```python
config.min_coherence_score = 0.92  # Wyższe standardy
config.enable_strict_validation = True
config.max_retries = 5
```

---

## 🐛 Troubleshooting

### Brak klucza API
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Niska jakość
```python
config.default_model = "claude-opus"
config.min_coherence_score = 0.90
```

### Wolne działanie
```python
# Szybkie modele dla analiz
validator.config["preferred_model"] = "claude-haiku"

# Mocne modele dla generacji
generator.config["preferred_model"] = "claude-opus"
```

---

## 🗺️ Roadmap

### ✅ Faza 1: Core (GOTOWE)
- [x] Wszystkie 10 agentów
- [x] Potrójny system pamięci
- [x] Multi-world support
- [x] Kompletny pipeline

### 🔄 Faza 2: Advanced (W Trakcie)
- [ ] Vector embeddings
- [ ] Parallel execution
- [ ] Long context caching
- [ ] Real-time monitoring

### 📅 Faza 3: UI/API
- [ ] Web interface
- [ ] REST API
- [ ] Batch processing
- [ ] Integracje wydawnicze

---

## 🎭 Filozofia

> _"Nie tworzymy 'tekstu'. Nie tworzymy 'opowiadania'._
>
> _Tworzymy **ŚWIATY**, **HISTORIE**, **UNIWERSA**, **PRODUKTY WYDAWNICZE**._
>
> _Działamy jak studio narracyjne, wydawnictwo przyszłości, silnik opowieści ponadczasowych."_

---

## 📜 Licencja

*Do określenia*

---

## 🤝 Wsparcie

- **Issues**: [GitHub Issues](https://github.com/Marksio90/NARRA_FORGE/issues)
- **Pull Requests**: Mile widziane!
- **Dokumentacja**: DOKUMENTACJA_PL.md

---

## ⭐ Status Projektu

```
✅ PRODUCTION READY dla:
   - Opowiadania (short stories)
   - Nowele (novellas)
   - Powieści (novels)
   - Sagi (epics)
   - Multi-world narratives
   - Audiobook format
```

---

**Zbudowane z precyzją. Zaprojektowane na wieczność.** 🚀

**NARRA_FORGE** - Synteza sztuki i inżynierii na najwyższym poziomie.
