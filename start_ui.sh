#!/bin/bash
# Start NARRA_FORGE Streamlit UI

echo "🖥️  Uruchamianie NARRA_FORGE UI..."
echo ""

# Sprawdź czy API działa
echo "Sprawdzanie połączenia z API..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API działa"
else
    echo "⚠️  API nie odpowiada!"
    echo "Uruchom najpierw API:"
    echo "  ./start_api.sh"
    echo "lub:"
    echo "  docker-compose up -d narra-forge-api"
    echo ""
    echo "Kontynuuję uruchamianie UI..."
fi

echo ""
echo "Uruchamianie UI na http://localhost:8501 ..."
echo ""
echo "Naciśnij Ctrl+C aby zatrzymać"
echo ""

streamlit run narra_forge/ui/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
