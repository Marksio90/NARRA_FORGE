#!/bin/bash

# Apply database migration for simulation fields
# This script applies the migration 001_add_simulation_fields.sql

set -e

MIGRATION_FILE="001_add_simulation_fields.sql"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Database connection parameters
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-narraforge}"
DB_USER="${POSTGRES_USER:-narraforge}"
export PGPASSWORD="${POSTGRES_PASSWORD:-narraforge_password}"

echo "Applying migration: $MIGRATION_FILE"
echo "Database: $DB_NAME on $DB_HOST:$DB_PORT"

# Apply migration
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCRIPT_DIR/$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Migration applied successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi
