#!/bin/bash
#
# Build Docker containers with automatic type generation
#
# This script ensures all TypeScript types are up-to-date before building Docker containers.
# It's a convenience wrapper around docker-compose build.
#
# Usage:
#   ./scripts/build-with-types.sh [service...]
#
# Examples:
#   ./scripts/build-with-types.sh              # Build all services
#   ./scripts/build-with-types.sh frontend     # Build only frontend
#   ./scripts/build-with-types.sh backend frontend  # Build backend and frontend
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   NARRA FORGE V2 - Docker Build with Type Safety${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Step 1: Generate OpenAPI spec from backend
echo -e "${YELLOW}Step 1/3: Generating OpenAPI specification from backend...${NC}"
python scripts/generate_openapi_spec.py --output api-spec.json
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ OpenAPI spec generated: api-spec.json${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Could not generate OpenAPI spec (continuing with existing)${NC}"
fi
echo ""

# Step 2: Copy OpenAPI spec to frontend for type generation
echo -e "${YELLOW}Step 2/3: Copying OpenAPI spec to frontend...${NC}"
if [ -f api-spec.json ]; then
    cp api-spec.json frontend/api-spec.json
    echo -e "${GREEN}✅ OpenAPI spec copied to frontend/api-spec.json${NC}"
else
    echo -e "${YELLOW}⚠️  No api-spec.json found, frontend will use existing types${NC}"
fi
echo ""

# Step 3: Build Docker containers
echo -e "${YELLOW}Step 3/3: Building Docker containers...${NC}"
if [ $# -eq 0 ]; then
    # Build all services
    echo -e "${BLUE}Building all services...${NC}"
    docker-compose build
else
    # Build specified services
    echo -e "${BLUE}Building services: $@${NC}"
    docker-compose build "$@"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}   ✅ Build completed successfully!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. Start services: ${GREEN}docker-compose up -d${NC}"
    echo -e "  2. View logs: ${GREEN}docker-compose logs -f${NC}"
    echo -e "  3. Check health: ${GREEN}curl http://localhost:8000/health${NC}"
    echo ""
else
    echo ""
    echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}   ⚠️  Build failed - check errors above${NC}"
    echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
