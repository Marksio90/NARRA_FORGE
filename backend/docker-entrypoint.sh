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

# Apply SQL migrations
echo "📦 Applying database migrations..."
MIGRATIONS_DIR="/app/migrations"

if [ -d "$MIGRATIONS_DIR" ]; then
    for migration in "$MIGRATIONS_DIR"/*.sql; do
        if [ -f "$migration" ]; then
            filename=$(basename "$migration")
            # Skip init.sql as it's handled by postgres entrypoint
            if [ "$filename" != "init.sql" ]; then
                echo "  Applying: $filename"
                PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration" 2>/dev/null || true
            fi
        fi
    done
    echo "✅ Migrations complete!"
else
    echo "⚠️  No migrations directory found"
fi

# Note: Database tables will be created automatically by SQLAlchemy
# when the FastAPI application starts (via init_db() in main.py)

# Start the application
echo "🎯 Starting application with command: $@"
exec "$@"
