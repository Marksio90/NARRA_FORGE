#!/bin/bash

# NARRA_FORGE Docker Development Helper Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_info "Checking requirements..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi

    print_info "✓ Docker and Docker Compose are installed"
}

start_all() {
    print_info "Starting all NARRA_FORGE services..."
    docker compose --profile dev up -d
    print_info "Services started!"
    print_info "UI available at: http://localhost:3000"
    print_info "API available at: http://localhost:8000"
    print_info "API docs at: http://localhost:8000/docs"
}

stop_all() {
    print_info "Stopping all services..."
    docker compose down
    print_info "Services stopped"
}

restart_all() {
    print_info "Restarting all services..."
    docker compose down
    docker compose --profile dev up -d
    print_info "Services restarted"
}

build_all() {
    print_info "Building all images..."
    docker compose build --no-cache
    print_info "Build complete"
}

logs_all() {
    docker compose logs -f
}

logs_api() {
    docker compose logs -f api
}

logs_ui() {
    docker compose logs -f ui
}

logs_worker() {
    docker compose logs -f worker
}

status() {
    print_info "Service status:"
    docker compose ps
}

health() {
    print_info "Health checks:"
    echo ""

    echo -n "API: "
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi

    echo -n "UI: "
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi

    echo -n "PostgreSQL: "
    if docker compose exec -T postgres pg_isready -U user -d narra_forge > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi

    echo -n "Redis: "
    if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
}

shell_api() {
    print_info "Opening API shell..."
    docker compose exec api bash
}

shell_ui() {
    print_info "Opening UI shell..."
    docker compose exec ui sh
}

shell_db() {
    print_info "Opening PostgreSQL shell..."
    docker compose exec postgres psql -U user -d narra_forge
}

test_backend() {
    print_info "Running backend tests..."
    docker compose exec api uv run pytest tests/unit/ -v
}

clean() {
    print_warn "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        docker compose down -v --remove-orphans
        print_info "Cleanup complete"
    else
        print_info "Cancelled"
    fi
}

show_help() {
    cat << EOF
NARRA_FORGE Docker Development Helper

Usage: ./docker-dev.sh [command]

Commands:
  start         Start all services
  stop          Stop all services
  restart       Restart all services
  build         Build all images
  status        Show service status
  health        Check health of all services
  logs          Show logs for all services
  logs-api      Show API logs
  logs-ui       Show UI logs
  logs-worker   Show worker logs
  shell-api     Open API shell
  shell-ui      Open UI shell
  shell-db      Open database shell
  test          Run backend tests
  clean         Remove all containers and volumes
  help          Show this help message

Examples:
  ./docker-dev.sh start
  ./docker-dev.sh logs-api
  ./docker-dev.sh health

EOF
}

# Main
case "${1:-help}" in
    start)
        check_requirements
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    build)
        build_all
        ;;
    status)
        status
        ;;
    health)
        health
        ;;
    logs)
        logs_all
        ;;
    logs-api)
        logs_api
        ;;
    logs-ui)
        logs_ui
        ;;
    logs-worker)
        logs_worker
        ;;
    shell-api)
        shell_api
        ;;
    shell-ui)
        shell_ui
        ;;
    shell-db)
        shell_db
        ;;
    test)
        test_backend
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
