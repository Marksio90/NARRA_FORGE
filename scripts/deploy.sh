#!/bin/bash
# NARRA_FORGE V2 Deployment Script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${GREEN}=== NARRA_FORGE V2 Deployment ===${NC}"
echo "Environment: $ENVIRONMENT"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
REQUIRED_VARS=(
    "DB_PASSWORD"
    "JWT_SECRET_KEY"
    "REDIS_PASSWORD"
    "OPENAI_API_KEY"
    "ANTHROPIC_API_KEY"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}Error: $var is not set in .env${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓ Environment variables verified${NC}"

# Pull latest code
echo -e "${YELLOW}Pulling latest code...${NC}"
git pull origin main

# Build and start services
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose -f $COMPOSE_FILE build --no-cache

echo -e "${YELLOW}Starting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"
if docker-compose -f $COMPOSE_FILE ps | grep -q "healthy"; then
    echo -e "${GREEN}✓ Services are healthy${NC}"
else
    echo -e "${RED}Warning: Some services may not be healthy${NC}"
    docker-compose -f $COMPOSE_FILE ps
fi

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker-compose -f $COMPOSE_FILE exec -T backend alembic upgrade head
echo -e "${GREEN}✓ Migrations complete${NC}"

# Show running services
echo ""
echo -e "${GREEN}=== Running Services ===${NC}"
docker-compose -f $COMPOSE_FILE ps

# Show logs (last 50 lines)
echo ""
echo -e "${GREEN}=== Recent Logs ===${NC}"
docker-compose -f $COMPOSE_FILE logs --tail=50

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo "Frontend: https://yourdomain.com"
echo "API: https://api.yourdomain.com"
echo "Grafana: https://yourdomain.com:3000"
echo ""
echo "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "To stop: docker-compose -f $COMPOSE_FILE down"
