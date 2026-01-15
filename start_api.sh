#!/bin/bash
# Start NARRA_FORGE API Server

echo "🚀 Uruchamianie NARRA_FORGE API Server..."
echo ""

# Sprawdź czy .env istnieje
if [ ! -f .env ]; then
    echo "⚠️  Brak pliku .env!"
    echo "Skopiuj .env.example do .env i dodaj klucze API:"
    echo "  cp .env.example .env"
    echo ""
    exit 1
fi

# Sprawdź czy OPENAI_API_KEY jest ustawiony
source .env
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY nie jest ustawiony w .env!"
    echo "Dodaj klucz OpenAI do .env:"
    echo "  OPENAI_API_KEY=sk-proj-xxx..."
    echo ""
    exit 1
fi

echo "✅ Konfiguracja OK"
echo ""

# Uruchom API
echo "Uruchamianie API na http://localhost:8000 ..."
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Naciśnij Ctrl+C aby zatrzymać"
echo ""

python -m uvicorn narra_forge.api.server:app --host 0.0.0.0 --port 8000 --reload
