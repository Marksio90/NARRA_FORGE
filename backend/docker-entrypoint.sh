#!/bin/bash
set -e

echo "🚀 Starting NarraForge Backend..."

# Extract database connection params from DATABASE_URL
# Format: postgresql://user:pass@host:port/dbname
DB_HOST="narraforge-postgres"
DB_PORT="5432"
DB_USER="${POSTGRES_USER:-narraforge}"
DB_PASS="${POSTGRES_PASSWORD:-narraforge_password}"
DB_NAME="${POSTGRES_DB:-narraforge}"

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "✅ PostgreSQL is ready!"

# Note: Database tables will be created automatically by SQLAlchemy
# when the FastAPI application starts (via init_db() in main.py)
# All schema is defined in models - no manual migrations needed

# Start the application
echo "🎯 Starting application with command: $@"
exec "$@"
