# NARRA_FORGE Examples

Przykłady użycia systemu produkcji narracji.

## Przygotowanie

```bash
# 1. Zainstaluj NARRA_FORGE
pip install -e ..

# 2. Skonfiguruj API key
cp ../.env.example ../.env
# Edytuj .env i dodaj OPENAI_API_KEY

# 3. Uruchom przykład
python example_short_story.py
```

---

## Przykłady

### 1. Short Story (Opowiadanie)
**Plik:** `example_short_story.py`

Prosta produkcja opowiadania fantasy (5k-10k słów).

```bash
python example_short_story.py
```

**Czas:** ~2-5 minut
**Koszt:** ~$0.50-$2.00

---

### 2. Novella Sci-Fi (Nowela)
**Plik:** `example_novella_scifi.py`

Produkcja dłuższej noweli science fiction (10k-40k słów).

```bash
python example_novella_scifi.py
```

**Czas:** ~5-15 minut
**Koszt:** ~$2.00-$8.00

---

### 3. Programmatic API Usage
**Plik:** `example_programmatic_api.py`

Zaawansowane użycie - pełna kontrola nad konfiguracją, komponentami, tracking.

```bash
python example_programmatic_api.py
```

Pokazuje:
- Custom configuration
- Explicit component initialization
- Multi-world support
- Detailed cost analysis
- Memory querying

---

## Struktura Outputu

Każda produkcja tworzy folder w `output/`:

```
output/
└── job_abc123def456/
    ├── narrative.txt          # Finalna narracja
    ├── audiobook.txt          # Wersja z znacznikami narratora
    ├── metadata.json          # Metadata (cost, quality, etc.)
    └── world_export.json      # Eksport świata (IP)
```

---

## Koszty (szacunkowe)

| Typ produkcji | Word count | Czas | Koszt (USD) |
|---------------|------------|------|-------------|
| Short Story   | 5k-10k     | 2-5 min | $0.50-$2.00 |
| Novella       | 10k-40k    | 5-15 min | $2.00-$8.00 |
| Novel         | 40k-120k   | 20-60 min | $8.00-$30.00 |

*Koszty zależą od kompleksności i jakości*

---

## Wskazówki

### Optymalizacja kosztów
```python
config = NarraForgeConfig()
config.max_cost_per_job = 5.0  # Limit
```

### Wyższa jakość
```python
config.min_coherence_score = 0.95  # Wyższe wymagania
```

### Użycie istniejącego świata (sequel)
```python
brief = ProductionBrief(
    production_type=ProductionType.SHORT_STORY,
    genre=Genre.FANTASY,
    world_id="world_abc123",  # Użyj istniejącego świata
    inspiration="Kontynuacja..."
)
```

---

## Troubleshooting

### Problem: "OPENAI_API_KEY not set"
**Rozwiązanie:** Dodaj klucz do `.env`:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
```

### Problem: Zbyt wysoki koszt
**Rozwiązanie:** Ogranicz max_cost_per_job:
```python
config.max_cost_per_job = 2.0
```

### Problem: Niska jakość
**Rozwiązanie:** Podnieś wymagania:
```python
config.min_coherence_score = 0.90
config.enable_strict_validation = True
```

---

## CLI Alternative

Zamiast kodu Python, możesz użyć CLI:

```bash
# Tryb interaktywny
narra-forge

# Tryb bezpośredni
narra-forge --type short_story --genre fantasy --inspiration "..."

# Lista zadań
narra-forge --list-jobs
```

---

Więcej informacji: [USER_GUIDE.md](../USER_GUIDE.md)
