# NarraForge Backend Dockerfile
# Multi-stage build for development and production

# ==================== Base Stage ====================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 narraforge && \
    mkdir -p /app /app/artifacts /app/logs && \
    chown -R narraforge:narraforge /app

WORKDIR /app

# ==================== Development Stage ====================
FROM base as development

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files
COPY --chown=narraforge:narraforge pyproject.toml ./

# Install dependencies only (not the package itself in editable mode)
# The source code will be mounted via volumes in docker-compose
RUN uv pip install --system \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.34.0" \
    "python-multipart>=0.0.20" \
    "websockets>=14.1" \
    "sqlalchemy>=2.0.36" \
    "alembic>=1.14.0" \
    "asyncpg>=0.30.0" \
    "pgvector>=0.3.6" \
    "redis>=5.2.0" \
    "celery>=5.4.0" \
    "langgraph>=0.2.70" \
    "langchain>=0.3.20" \
    "langchain-core>=0.3.30" \
    "langchain-openai>=0.3.10" \
    "langchain-community>=0.3.20" \
    "openai>=1.59.0" \
    "tiktoken>=0.8.0" \
    "pydantic>=2.10.0" \
    "pydantic-settings>=2.7.0" \
    "email-validator>=2.2.0" \
    "python-dotenv>=1.0.1" \
    "httpx>=0.28.1" \
    "tenacity>=9.0.0" \
    "python-docx>=1.1.2" \
    "markdown>=3.7" \
    "python-dateutil>=2.9.0" \
    "structlog>=24.4.0"

# Switch to app user
USER narraforge

# Expose port
EXPOSE 8000

# Default command (can be overridden in compose.yaml)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==================== Production Stage ====================
FROM base as production

# Install uv
RUN pip install uv

# Copy application code first
COPY --chown=narraforge:narraforge . .

# Install dependencies and package
RUN uv pip install --system .

# Switch to app user
USER narraforge

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
