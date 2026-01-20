# 📚 NARRAFORGE - Autonomiczna Kuźnia Literacka

**Multi-Agentowa Platforma do Tworzenia Pełnometrażowych Książek Bestsellerowych**

NarraForge to zaawansowana, w pełni autonomiczna platforma wykorzystująca multi-agentową orkiestrację AI do tworzenia pełnometrażowych książek na poziomie profesjonalnym. System samodzielnie projektuje świat, tworzy postacie, konstruuje fabułę i pisze hipnotyzującą prozę - użytkownik wybiera tylko gatunek.

## 🌟 Kluczowe Cechy

- **🤖 8 Wyspecjalizowanych Agentów AI** - każdy ekspert w swojej dziedzinie
- **🎯 Pełna Autonomiczność** - AI decyduje o wszystkim: długości, postaciach, fabule, świecie
- **📊 Inteligentne Skalowanie Modeli** - automatyczny dobór GPT-4o-mini/4o/4 zależnie od złożoności
- **🔄 15-Etapowy Pipeline** - od koncepcji po profesjonalny eksport
- **💰 Inteligentna Symulacja Kosztów** - dokładna predykcja przed rozpoczęciem
- **🎭 8 Gatunków Literackich** - Sci-Fi, Fantasy, Thriller, Horror, Romans, Dramat, Komedia, Kryminał
- **📖 Eksport Multi-Format** - DOCX, EPUB, PDF, Markdown
- **🔍 RAG + pgvector** - perfekcyjna spójność fabularna
- **📡 Real-time Progress** - WebSocket monitoring każdego kroku

## 🚀 Szybki Start

### Wymagania

- Docker Engine 24+
- Docker Compose v2
- Min. 8GB RAM
- Min. 20GB wolnej przestrzeni dyskowej
- OpenAI API Key z dostępem do GPT-4

### Instalacja

```bash
# 1. Sklonuj repozytorium
git clone https://github.com/yourusername/narraforge.git
cd narraforge

# 2. Skonfiguruj zmienne środowiskowe
cp .env.example .env
# Edytuj .env i dodaj swój OPENAI_API_KEY

# 3. Uruchom wszystkie serwisy
docker-compose up -d
```

### Dostęp do Aplikacji

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower (Celery)**: http://localhost:5555

## 📚 System Multi-Agentowy

1. **ORCHESTRATOR** - Główny koordynator
2. **WORLD_ARCHITECT** - Projektowanie uniwersum
3. **CHARACTER_SMITH** - Tworzenie postaci
4. **PLOT_MASTER** - Architektura fabuły
5. **PROSE_WEAVER** - Pisanie prozy
6. **CONTINUITY_GUARDIAN** - Strażnik spójności
7. **STYLE_MASTER** - Redakcja stylu
8. **GENRE_EXPERT** - Weryfikacja gatunku

---

**📚 NARRAFORGE - Gdzie AI staje się Autorem 📚**
