.PHONY: dev build up down logs test clean migrate migration help

# Default target
help:
	@echo "🔥 NarraForge - Kuźnia Bestsellerów AI"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev        - Start development environment"
	@echo "  make build      - Build all containers"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View logs"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean everything"
	@echo "  make migrate    - Run database migrations"
	@echo "  make migration  - Create new migration"

# Development
dev:
	docker-compose -f docker/docker-compose.yml up --build

# Production build
build:
	docker-compose -f docker/docker-compose.yml build

# Start services
up:
	docker-compose -f docker/docker-compose.yml up -d

# Stop services
down:
	docker-compose -f docker/docker-compose.yml down

# View logs
logs:
	docker-compose -f docker/docker-compose.yml logs -f

# Run tests
test:
	docker-compose -f docker/docker-compose.yml exec narraforge-backend pytest

# Clean everything
clean:
	docker-compose -f docker/docker-compose.yml down -v
	docker system prune -f

# Database migrations
migrate:
	docker-compose -f docker/docker-compose.yml exec narraforge-backend alembic upgrade head

# Create new migration
migration:
	@read -p "Migration name: " name; \
	docker-compose -f docker/docker-compose.yml exec narraforge-backend alembic revision --autogenerate -m "$$name"
