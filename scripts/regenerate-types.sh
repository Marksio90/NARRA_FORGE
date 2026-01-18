#!/bin/bash
#
# Regenerate TypeScript types from OpenAPI schema
#
# This script is the AUTOMATION BRIDGE between backend and frontend.
# It ensures TypeScript types are always synchronized with Pydantic schemas.
#
# Usage:
#   ./scripts/regenerate-types.sh [--local]
#
# Options:
#   --local   Generate from local JSON file instead of running API server
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔄 Regenerating TypeScript types from OpenAPI schema..."

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if --local flag is provided
USE_LOCAL=false
if [[ "$1" == "--local" ]]; then
    USE_LOCAL=true
fi

if [ "$USE_LOCAL" = true ]; then
    echo -e "${BLUE}Using local OpenAPI spec file${NC}"

    # Generate OpenAPI spec from FastAPI
    echo -e "${YELLOW}Step 1: Generating OpenAPI spec from FastAPI...${NC}"
    cd "$PROJECT_ROOT/api"
    python -c "
import json
from api.main import app

spec = app.openapi()
with open('../api-spec.json', 'w') as f:
    json.dump(spec, f, indent=2)
print('✅ OpenAPI spec saved to api-spec.json')
" || {
        echo -e "${RED}❌ Failed to generate OpenAPI spec${NC}"
        exit 1
    }

    # Generate TypeScript types from local file
    echo -e "${YELLOW}Step 2: Generating TypeScript types from local spec...${NC}"
    cd "$PROJECT_ROOT/frontend"
    npm run generate:types:local || {
        echo -e "${RED}❌ Failed to generate TypeScript types${NC}"
        exit 1
    }
else
    echo -e "${BLUE}Using live API server${NC}"

    # Check if API server is running
    echo -e "${YELLOW}Step 1: Checking if API server is running...${NC}"
    if ! curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${RED}❌ API server is not running on http://localhost:8000${NC}"
        echo -e "${YELLOW}Please start the API server first or use --local flag${NC}"
        echo -e "${BLUE}To start API server: cd api && uvicorn api.main:app --reload${NC}"
        exit 1
    fi

    # Generate TypeScript types from live API
    echo -e "${YELLOW}Step 2: Generating TypeScript types from live API...${NC}"
    cd "$PROJECT_ROOT/frontend"
    npm run generate:types || {
        echo -e "${RED}❌ Failed to generate TypeScript types${NC}"
        exit 1
    }
fi

# Run TypeScript type check
echo -e "${YELLOW}Step 3: Running TypeScript type check...${NC}"
npm run type-check || {
    echo -e "${RED}❌ TypeScript type check failed${NC}"
    echo -e "${YELLOW}There are type errors in the frontend code.${NC}"
    echo -e "${YELLOW}Please fix them before committing.${NC}"
    exit 1
}

echo -e "${GREEN}✅ TypeScript types regenerated and validated successfully!${NC}"
echo -e "${BLUE}Generated file: frontend/src/types/api-generated.ts${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo -e "  1. Review the generated types in ${BLUE}frontend/src/types/api-generated.ts${NC}"
echo -e "  2. Update your frontend code to use these types"
echo -e "  3. Run ${BLUE}npm run type-check${NC} to verify everything compiles"
echo -e "  4. Commit both backend schema changes and generated frontend types"
