#!/bin/bash
# Szybki test NARRA_FORGE przez Docker

echo "============================================"
echo "🐳 NARRA_FORGE - Test Docker"
echo "============================================"
echo ""

# Kolory
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Czy Docker działa
echo -e "${BLUE}[1/7] Sprawdzanie Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker nie jest zainstalowany${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker OK${NC}"
echo ""

# Test 2: Czy docker-compose działa
echo -e "${BLUE}[2/7] Sprawdzanie docker-compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose nie jest zainstalowany${NC}"
    exit 1
fi
echo -e "${GREEN}✅ docker-compose OK${NC}"
echo ""

# Test 3: Czy kontenery działają
echo -e "${BLUE}[3/7] Sprawdzanie kontenerów...${NC}"
if ! docker-compose ps | grep -q "narra-forge-api.*Up"; then
    echo -e "${RED}❌ Kontener API nie działa${NC}"
    echo -e "${YELLOW}Uruchom: docker-compose up -d narra-forge-api${NC}"
    exit 1
fi
echo -e "${GREEN}✅ API kontener działa${NC}"

if ! docker-compose ps | grep -q "narra-forge-ui.*Up"; then
    echo -e "${RED}❌ Kontener UI nie działa${NC}"
    echo -e "${YELLOW}Uruchom: docker-compose up -d narra-forge-ui${NC}"
    exit 1
fi
echo -e "${GREEN}✅ UI kontener działa${NC}"
echo ""

# Test 4: Czy API odpowiada
echo -e "${BLUE}[4/7] Testowanie API...${NC}"
sleep 2  # Daj chwilę na uruchomienie
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ API działa poprawnie${NC}"
else
    echo -e "${RED}❌ API nie odpowiada${NC}"
    echo -e "${YELLOW}Sprawdź logi: docker-compose logs narra-forge-api${NC}"
    exit 1
fi
echo ""

# Test 5: Czy UI odpowiada
echo -e "${BLUE}[5/7] Testowanie UI...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
    echo -e "${GREEN}✅ UI działa poprawnie${NC}"
else
    echo -e "${RED}❌ UI nie odpowiada${NC}"
    echo -e "${YELLOW}Sprawdź logi: docker-compose logs narra-forge-ui${NC}"
    exit 1
fi
echo ""

# Test 6: Sprawdź endpointy API
echo -e "${BLUE}[6/7] Testowanie endpointów API...${NC}"
endpoints=(
    "/health:Health Check"
    "/docs:API Documentation"
    "/api/projects:Projects List"
)

for endpoint_info in "${endpoints[@]}"; do
    IFS=':' read -r endpoint name <<< "$endpoint_info"
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$endpoint" | grep -q "200"; then
        echo -e "${GREEN}  ✅ $name ($endpoint)${NC}"
    else
        echo -e "${YELLOW}  ⚠️  $name ($endpoint) - może wymagać autoryzacji${NC}"
    fi
done
echo ""

# Test 7: Sprawdź użycie zasobów
echo -e "${BLUE}[7/7] Użycie zasobów...${NC}"
docker stats --no-stream narra-forge-api narra-forge-ui
echo ""

# Podsumowanie
echo "============================================"
echo -e "${GREEN}✅ Wszystkie podstawowe testy przeszły!${NC}"
echo "============================================"
echo ""
echo -e "${BLUE}📍 Dostępne serwisy:${NC}"
echo ""
echo -e "   🖥️  UI (Streamlit):       ${YELLOW}http://localhost:8501${NC}"
echo -e "   🔌 API:                   ${YELLOW}http://localhost:8000${NC}"
echo -e "   📖 API Docs (Swagger):    ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo "============================================"
echo ""
echo -e "${BLUE}💡 Przydatne komendy:${NC}"
echo ""
echo -e "   ${YELLOW}docker-compose logs -f narra-forge-api${NC}    # Logi API"
echo -e "   ${YELLOW}docker-compose logs -f narra-forge-ui${NC}     # Logi UI"
echo -e "   ${YELLOW}docker-compose restart${NC}                    # Restart"
echo -e "   ${YELLOW}docker-compose down${NC}                       # Zatrzymaj"
echo -e "   ${YELLOW}docker-compose exec narra-forge-api bash${NC}  # Wejdź do kontenera"
echo ""
echo "============================================"
echo ""
echo -e "${GREEN}🎬 Gotowe! Otwórz http://localhost:8501 w przeglądarce!${NC}"
echo ""
