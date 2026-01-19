# 🚀 NARRA_FORGE - Szybki Start

**Uniwersalny System Generowania Narracji** - od flash fiction do sagi, od fantasy do literary!

---

## ⚡ Instalacja (5 minut)

### 1. **Sklonuj repozytorium** (jeśli nie masz)
```bash
git clone https://github.com/Marksio90/NARRA_FORGE.git
cd NARRA_FORGE
```

### 2. **Zainstaluj zależności**
```bash
pip install -r requirements.txt
```

### 3. **Skonfiguruj klucz API**
```bash
# Skopiuj template
cp .env.example .env

# Edytuj .env i dodaj swój klucz OpenAI
# OPENAI_API_KEY=sk-proj-twoj-klucz-tutaj
```

**LUB** ustaw bezpośrednio w terminalu:
```bash
export OPENAI_API_KEY="sk-proj-twoj-klucz-tutaj"
```

---

## 🎯 Pierwsze Użycie (1 minuta)

### Uruchom przykład:
```bash
python przyklad_uzycia_pl.py
```

### LUB napisz własny kod:
```python
import asyncio
from narra_forge import NarrativeOrchestrator, get_default_config

async def generuj():
    config = get_default_config()
    orchestrator = NarrativeOrchestrator(config)

    # DOWOLNE zlecenie w języku naturalnym!
    wynik = await orchestrator.produce_narrative("""
        Napisz mroczne opowiadanie fantasy o alchemiku.
        Długość: 5000 słów.
    """)

    if wynik.success:
        print(f"✅ Gotowe! {wynik.total_word_count} słów")
        print(f"📁 Plik: {wynik.output_files['text_file']}")
    else:
        print(f"❌ Błąd: {wynik.errors}")

asyncio.run(generuj())
```

---

## 📖 UNIWERSALNOŚĆ - Działa dla WSZYSTKIEGO!

### 1. **Auto-detekcja** (system sam wszystko wykryje)
```python
wynik = await orchestrator.produce_narrative(
    "Historia o dziewczynie podróżującej w czasie przez sny."
)
# System wykryje: sci-fi/fantasy hybrid, nowela, ~20k słów
```

### 2. **Różne długości** (automatyczna adaptacja!)
```python
# Flash fiction (500 słów)
await orchestrator.produce_narrative("Krótka historia (500 słów) o ostatnim dniu na Ziemi")

# Opowiadanie (5k-15k słów)
await orchestrator.produce_narrative("Opowiadanie o detektywie w cyberpunkowej Warszawie")

# Nowela (20k-40k słów)
await orchestrator.produce_narrative("Nowela sci-fi o samotnej stacji kosmicznej")

# Powieść (50k-120k słów)
await orchestrator.produce_narrative("Powieść fantasy o wojnie bogów. 80,000 słów.")
```

### 3. **Różne gatunki** (każdy ma unique style!)
```python
# Fantasy (poetycki, metaforyczny)
await orchestrator.produce_narrative("Fantasy: czarodziej vs smok")

# Thriller (zwięzły, dynamiczny)
await orchestrator.produce_narrative("Thriller: seryjny morderca w Krakowie")

# Romance (emocjonalny, zmysłowy)
await orchestrator.produce_narrative("Romans: zakochani wampir i śmiertelniczka")

# Literary Fiction (wyrafinowany, głęboki)
await orchestrator.produce_narrative("Powieść literacka o kryzysie egzystencjalnym artysty")
```

### 4. **Różne tony** (automatyczna adaptacja stylu!)
```python
# Mroczny
await orchestrator.produce_narrative("Mroczne horror o nawiedzonej posiadłości")

# Lekki
await orchestrator.produce_narrative("Lekka komedia romantyczna")

# Filozoficzny
await orchestrator.produce_narrative("Filozoficzna refleksja o naturze świadomości")
```

---

## 🔧 Zaawansowana Konfiguracja

### Wybór modelu:
```python
from narra_forge import get_default_config

config = get_default_config()

# Użyj Claude Opus dla najwyższej jakości
config.default_model = "claude-opus"

# LUB mapuj modele dla poszczególnych etapów
config.stage_model_mapping["sequential_generation"] = "gpt-4-turbo"
config.stage_model_mapping["language_stylization"] = "claude-opus"

orchestrator = NarrativeOrchestrator(config)
```

### Jakość:
```python
# Wyższe standardy
config.min_coherence_score = 0.92  # Domyślnie: 0.85
config.enable_strict_validation = True
```

---

## 📊 Co Otrzymujesz?

Po generacji znajdziesz pliki w `data/output/[project_id]/`:

```
narracja.txt              - Pełny tekst (gotowy do publikacji)
narracja_audiobook.txt    - Wersja dla audiobooka
metadata.json             - Metadane (gatunek, słowa, etc.)
ekspansja.json            - Dane dla sequel/prequel
```

---

## 🎓 Przykłady w `przyklad_uzycia_pl.py`

Sprawdź plik `przyklad_uzycia_pl.py` dla kompletnych przykładów:
- ✅ Podstawowe opowiadanie
- ✅ Nowela sci-fi
- ✅ Thriller psychologiczny
- ✅ Uniwersalne API (różne formy i gatunki)

---

## ❓ Problemy?

### Brak klucza API:
```bash
export OPENAI_API_KEY="sk-proj-..."
# LUB
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Wolne działanie:
```python
# Użyj szybszych modeli dla niektórych etapów
config.stage_model_mapping["coherence_validation"] = "gpt-3.5-turbo"
```

### Niska jakość:
```python
# Użyj najlepszych modeli
config.default_model = "claude-opus"
config.min_coherence_score = 0.90
```

---

## 🚀 Gotowe!

System jest **UNIWERSALNY** - po prostu opisz co chcesz, a on:
1. ✅ Wykryje gatunek i formę
2. ✅ Dostosuje strukturę
3. ✅ Wygeneruje na najwyższym poziomie
4. ✅ Zwaliduje spójność
5. ✅ Wyda gotowy produkt

**NAPRAWDĘ działa dla WSZYSTKICH długości, gatunków i stylów!** 🎉

---

**Made with ❤️ by NARRA_FORGE Team**
