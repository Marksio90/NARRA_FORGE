# Build stage - install dependencies with build tools
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage - slim image without build tools
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    dos2unix \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user for security
RUN groupadd -r narraforge && useradd -r -g narraforge -d /app -s /sbin/nologin narraforge

# Copy application code
COPY . .

# Copy and make entrypoint script executable
COPY docker-entrypoint.sh /usr/local/bin/
RUN dos2unix /usr/local/bin/docker-entrypoint.sh && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

# Create output directory and set permissions
RUN mkdir -p /app/output && chown -R narraforge:narraforge /app

# Switch to non-root user
USER narraforge

# Expose port
EXPOSE 8000

# Set entrypoint to run migrations before starting app
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
