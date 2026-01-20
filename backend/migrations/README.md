# Database Migrations

This directory contains SQL migration files for the NarraForge database.

## Applying Migrations

### Option 1: Using the migration script

```bash
cd backend/migrations
chmod +x apply_migration.sh
./apply_migration.sh
```

### Option 2: Manually using psql

```bash
psql -h localhost -p 5432 -U narraforge -d narraforge -f 001_add_simulation_fields.sql
```

### Option 3: Using Docker (if database is in container)

```bash
# Copy migration file to container
docker cp backend/migrations/001_add_simulation_fields.sql narraforge-postgres:/tmp/

# Execute migration
docker exec -it narraforge-postgres psql -U narraforge -d narraforge -f /tmp/001_add_simulation_fields.sql
```

## Migration History

| Migration | Date | Description |
|-----------|------|-------------|
| 001_add_simulation_fields.sql | 2026-01-20 | Add simulation_data and estimated_duration_minutes fields to projects table |

## Notes

- All migrations use `IF NOT EXISTS` clauses to be idempotent
- Migrations can be safely run multiple times
- Always test migrations on a development database first
