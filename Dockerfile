# Backend Dockerfile for NARRA_FORGE V2 API
# Multi-stage build with automatic type safety and OpenAPI spec generation

# Stage 1: Builder - Install dependencies
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install production-only dependencies
RUN pip install --no-cache-dir gunicorn


# Stage 2: OpenAPI Spec Generator - Generate spec for frontend TypeScript generation
FROM builder AS spec-generator

WORKDIR /app
COPY api/ ./api/
COPY narra_forge/ ./narra_forge/
COPY scripts/generate_openapi_docker.py ./scripts/

# Set dummy environment variables for build-time OpenAPI generation
# These are only used during spec generation and not in runtime
# Note: CORS_ORIGINS not set - uses default value from config.py
ENV JWT_SECRET_KEY=build-time-dummy-secret-for-openapi-generation-only \
    DATABASE_URL=postgresql+asyncpg://dummy:dummy@localhost/dummy \
    REDIS_URL=redis://localhost:6379/0 \
    OPENAI_API_KEY=sk-dummy-key-for-build-time-openapi-generation-only \
    DEBUG=true

# Generate OpenAPI spec automatically
RUN python scripts/generate_openapi_docker.py


# Stage 3: Base - Minimal runtime image
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies (no gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Copy generated OpenAPI spec from spec-generator stage
COPY --from=spec-generator /app/api-spec.json ./api-spec.json

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port 8000"]


# Stage 4: Production - Optimized for production
FROM base AS production

# Run with Gunicorn for production
CMD ["sh", "-c", "alembic upgrade head && gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --access-logfile - --error-logfile - --timeout 120 --keep-alive 5"]
