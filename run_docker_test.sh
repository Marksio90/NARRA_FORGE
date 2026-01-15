#!/bin/bash

# NARRA_FORGE - Skrypt uruchomieniowy Docker
# Automatyzuje proces testowania w kontenerze Docker

set -e  # Exit on error

echo "============================================================"
echo "NARRA_FORGE - Automatyczne Testowanie w Docker"
echo "============================================================"
echo ""

# Kolory dla outputu
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Sprawdź czy Docker jest zainstalowany
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker nie jest zainstalowany!${NC}"
    echo "  Zainstaluj Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker zainstalowany${NC}"

# Sprawdź czy Docker Compose jest zainstalowany
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose nie jest zainstalowany!${NC}"
    echo "  Zainstaluj Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose zainstalowany${NC}"

# Sprawdź czy Docker daemon działa
if ! docker info &> /dev/null; then
    echo -e "${RED}✗ Docker daemon nie działa!${NC}"
    echo "  Uruchom Docker:"
    echo "    Linux: sudo systemctl start docker"
    echo "    MacOS: open -a Docker"
    exit 1
fi
echo -e "${GREEN}✓ Docker daemon działa${NC}"

# Sprawdź czy plik .env istnieje
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ Brak pliku .env${NC}"
    echo "  Tworzę plik .env z szablonu..."

    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}✓ Utworzono .env z .env.example${NC}"
        echo -e "${YELLOW}  WAŻNE: Wypełnij ANTHROPIC_API_KEY w pliku .env${NC}"
        echo ""
        read -p "Czy chcesz teraz edytować .env? (t/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Tt]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo -e "${RED}✗ Brak .env.example${NC}"
        exit 1
    fi
fi

# Sprawdź czy ANTHROPIC_API_KEY jest ustawiony
source .env
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ]; then
    echo -e "${RED}✗ ANTHROPIC_API_KEY nie jest ustawiony w .env${NC}"
    echo "  Edytuj plik .env i dodaj swój klucz API"
    exit 1
fi
echo -e "${GREEN}✓ ANTHROPIC_API_KEY ustawiony${NC}"

echo ""
echo "============================================================"
echo "Rozpoczynam testowanie..."
echo "============================================================"
echo ""

# Build image
echo "[1/3] Building Docker image..."
docker-compose build

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Build nie powiódł się${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Build zakończony${NC}"
echo ""

# Run test
echo "[2/3] Uruchamianie testów..."
docker-compose run --rm narra-forge python test_docker.py

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Testy nie przeszły${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Testy przeszły pomyślnie${NC}"
echo ""

# Opcjonalnie: uruchom przykład
echo "[3/3] Opcjonalnie: Uruchomić pełny przykład?"
echo -e "${YELLOW}  Uwaga: To wywoła rzeczywiste API i zużyje tokeny (~$0.10-0.20)${NC}"
read -p "  Uruchomić? (t/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Tt]$ ]]; then
    echo ""
    echo "Uruchamianie przykładu użycia..."
    docker-compose run --rm narra-forge python przyklad_uzycia_pl.py

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Przykład zakończył się błędem${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Przykład zakończony${NC}"
fi

echo ""
echo "============================================================"
echo -e "${GREEN}✅ WSZYSTKO DZIAŁA POPRAWNIE!${NC}"
echo "============================================================"
echo ""
echo "Dostępne komendy:"
echo "  docker-compose run --rm narra-forge python test_docker.py"
echo "  docker-compose run --rm narra-forge python przyklad_uzycia_pl.py"
echo "  docker-compose run --rm narra-forge-dev bash"
echo ""
echo "Dokumentacja: DOCKER.md"
echo ""
