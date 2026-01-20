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

# Install dependencies with uv
RUN uv pip install --system -e .

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

# Copy dependency files
COPY --chown=narraforge:narraforge pyproject.toml ./

# Install production dependencies only
RUN uv pip install --system .

# Copy application code
COPY --chown=narraforge:narraforge . .

# Switch to app user
USER narraforge

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
