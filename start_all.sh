#!/bin/bash
# Start całego NARRA_FORGE (API + UI) przez Docker Compose

echo "============================================================"
echo "        NARRA_FORGE - Uruchomienie Kompletne"
echo "============================================================"
echo ""

# Sprawdź czy .env istnieje
if [ ! -f .env ]; then
    echo "⚠️  Brak pliku .env!"
    echo ""
    echo "Tworzenie .env z .env.example..."
    cp .env.example .env
    echo "✅ Plik .env utworzony"
    echo ""
    echo "❗ WYMAGANE: Dodaj klucz OpenAI API do .env:"
    echo "   OPENAI_API_KEY=sk-proj-xxx..."
    echo ""
    echo "Edytuj .env i uruchom ponownie:"
    echo "   nano .env"
    echo "   ./start_all.sh"
    echo ""
    exit 1
fi

# Sprawdź czy OPENAI_API_KEY jest ustawiony
source .env
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY nie jest ustawiony w .env!"
    echo ""
    echo "Dodaj klucz OpenAI do .env:"
    echo "   OPENAI_API_KEY=sk-proj-xxx..."
    echo ""
    echo "Pobierz klucz: https://platform.openai.com/api-keys"
    echo ""
    exit 1
fi

echo "✅ Konfiguracja OK"
echo ""
echo "Uruchamianie serwisów..."
echo ""

# Build jeśli potrzebne
if ! docker images | grep -q narra-forge; then
    echo "📦 Budowanie obrazu Docker (pierwsze uruchomienie)..."
    docker-compose build
    echo ""
fi

# Uruchom serwisy
echo "🚀 Uruchamianie API i UI..."
docker-compose up -d narra-forge-api narra-forge-ui

echo ""
echo "⏳ Czekam na uruchomienie serwisów..."
sleep 5

echo ""
echo "============================================================"
echo "✅ NARRA_FORGE uruchomione!"
echo "============================================================"
echo ""
echo "📍 Dostępne serwisy:"
echo ""
echo "   🖥️  UI (Streamlit):       http://localhost:8501"
echo "   🔌 API:                   http://localhost:8000"
echo "   📖 API Docs (Swagger):    http://localhost:8000/docs"
echo ""
echo "============================================================"
echo ""
echo "📊 Status serwisów:"
docker-compose ps narra-forge-api narra-forge-ui
echo ""
echo "============================================================"
echo ""
echo "💡 Przydatne komendy:"
echo ""
echo "   Sprawdź logi API:    docker-compose logs -f narra-forge-api"
echo "   Sprawdź logi UI:     docker-compose logs -f narra-forge-ui"
echo "   Zatrzymaj wszystko:  docker-compose down"
echo "   Restart:             docker-compose restart"
echo ""
echo "============================================================"
echo ""
echo "🎬 Gotowe! Otwórz http://localhost:8501 w przeglądarce!"
echo ""
