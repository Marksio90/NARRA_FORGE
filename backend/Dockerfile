FROM python:3.11.14-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .

# Install dependencies
RUN uv sync --all-extras --no-dev

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /artifacts /logs

# Expose port
EXPOSE 8000

# Default command (overridden in compose.yaml)
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
