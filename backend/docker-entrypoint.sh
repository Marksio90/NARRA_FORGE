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

# Run migrations
echo "🔄 Running database migrations..."

# Apply migration 001 - simulation fields
PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
ALTER TABLE projects ADD COLUMN IF NOT EXISTS simulation_data JSONB;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS estimated_duration_minutes INTEGER;
COMMENT ON COLUMN projects.simulation_data IS 'Stores the full simulation response including estimated_steps, estimated_total_cost, estimated_duration_minutes, and ai_decisions';
COMMENT ON COLUMN projects.estimated_duration_minutes IS 'Estimated duration in minutes for the generation pipeline (from simulation)';
EOF

# Apply migration 002 - error message field
PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
ALTER TABLE projects ADD COLUMN IF NOT EXISTS error_message TEXT;
COMMENT ON COLUMN projects.error_message IS 'Stores detailed error message when generation fails (status = failed)';
EOF

echo "✅ Migrations applied successfully!"

# Start the application
echo "🎯 Starting application with command: $@"
exec "$@"
