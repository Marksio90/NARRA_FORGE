#!/bin/bash
# Health Endpoint Test Script for NarraForge
# Tests all three health check endpoints

set -e

echo "🏥 Testing NarraForge Health Endpoints"
echo "========================================"
echo ""

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local endpoint=$1
    local description=$2

    echo "Testing: ${description}"
    echo "Endpoint: ${BACKEND_URL}${endpoint}"
    echo "---"

    response=$(curl -s -w "\n%{http_code}" "${BACKEND_URL}${endpoint}")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Status: ${http_code} OK${NC}"
        echo "Response:"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "${RED}✗ Status: ${http_code} FAILED${NC}"
        echo "Response:"
        echo "$body"
    fi

    echo ""
    echo "========================================"
    echo ""
}

# Check if backend is reachable
echo "Checking if backend is reachable..."
if curl -s --connect-timeout 5 "${BACKEND_URL}/health/live" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is reachable${NC}"
    echo ""
else
    echo -e "${RED}✗ Backend is not reachable at ${BACKEND_URL}${NC}"
    echo ""
    echo "Make sure Docker services are running:"
    echo "  docker compose up -d"
    echo ""
    exit 1
fi

# Test all health endpoints
test_endpoint "/health/live" "Liveness Check (Is app running?)"
test_endpoint "/health/ready" "Readiness Check (Is app ready for requests?)"
test_endpoint "/health" "Full Health Check (All services status)"

echo ""
echo "📊 Health Check Summary"
echo "========================================"
echo ""
echo "Endpoints tested:"
echo "  1. /health/live  - Basic liveness (should always return 200 if app is running)"
echo "  2. /health/ready - Readiness check (returns 200 if ready to process requests)"
echo "  3. /health       - Full health check (shows status of all services)"
echo ""
echo "Expected behavior:"
echo "  - /health/live should always return: {\"alive\": true, \"message\": \"Application is running\"}"
echo "  - /health/ready returns ready:true only if:"
echo "      • PostgreSQL is connected"
echo "      • Redis is connected"
echo "      • OpenAI API key is configured"
echo "  - /health shows status of:"
echo "      • PostgreSQL database"
echo "      • Redis cache/broker"
echo "      • OpenAI API configuration"
echo "      • Anthropic API configuration (optional)"
echo ""
echo "💡 If /health/ready shows ready:false due to missing OpenAI API key:"
echo "   1. Create/edit .env file in project root"
echo "   2. Add: OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE"
echo "   3. Restart services: docker compose restart narraforge-backend"
echo ""
