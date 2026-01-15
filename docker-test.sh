#!/bin/bash
# Docker testing script for NARRA_FORGE

set -e

echo "═══════════════════════════════════════════"
echo "  NARRA_FORGE - Docker Test Suite"
echo "═══════════════════════════════════════════"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "   Copy .env.example to .env and add your OPENAI_API_KEY"
    exit 1
fi

# Load environment
source .env

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set in .env"
    exit 1
fi

echo "✓ Environment configured"
echo ""

# Build image
echo "Building Docker image..."
docker-compose build narra_forge
echo "✓ Image built"
echo ""

# Run tests
echo "Running test suite..."
docker-compose run --rm narra_forge_test
echo "✓ Tests passed"
echo ""

echo "═══════════════════════════════════════════"
echo "  All tests passed! ✓"
echo "═══════════════════════════════════════════"
