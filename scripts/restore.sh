#!/bin/bash
# NARRA_FORGE V2 Database Restore Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not specified${NC}"
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh /backups/narra_forge_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${RED}=== WARNING ===${NC}"
echo "This will REPLACE the current database with the backup"
echo "Current database will be LOST"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo -e "${GREEN}=== NARRA_FORGE Database Restore ===${NC}"
echo "Backup file: $BACKUP_FILE"
echo ""

# Stop backend and celery services
echo -e "${YELLOW}Stopping backend services...${NC}"
docker-compose -f docker-compose.prod.yml stop backend celery_worker

# Decompress backup if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    echo -e "${YELLOW}Decompressing backup...${NC}"
    gunzip -c "$BACKUP_FILE" > /tmp/restore.sql
    RESTORE_SQL="/tmp/restore.sql"
else
    RESTORE_SQL="$BACKUP_FILE"
fi

# Drop and recreate database
echo -e "${YELLOW}Recreating database...${NC}"
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U narra_forge -c "DROP DATABASE IF EXISTS narra_forge;"
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U narra_forge -c "CREATE DATABASE narra_forge;"

# Restore database
echo -e "${YELLOW}Restoring database...${NC}"
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U narra_forge narra_forge < "$RESTORE_SQL"

# Clean up temp file
if [ -f "/tmp/restore.sql" ]; then
    rm /tmp/restore.sql
fi

# Restart services
echo -e "${YELLOW}Restarting services...${NC}"
docker-compose -f docker-compose.prod.yml start backend celery_worker

echo ""
echo -e "${GREEN}=== Restore Complete ===${NC}"
echo "Database has been restored from: $BACKUP_FILE"
