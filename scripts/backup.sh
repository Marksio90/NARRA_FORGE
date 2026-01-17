#!/bin/bash
# NARRA_FORGE V2 Database Backup Script

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="narra_forge_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=7

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== NARRA_FORGE Database Backup ===${NC}"
echo "Timestamp: $TIMESTAMP"
echo ""

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database
echo -e "${YELLOW}Creating database backup...${NC}"
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U narra_forge narra_forge > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
echo -e "${YELLOW}Compressing backup...${NC}"
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Calculate size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_FILE}.gz" | cut -f1)
echo -e "${GREEN}✓ Backup created: ${BACKUP_FILE}.gz ($BACKUP_SIZE)${NC}"

# Clean old backups
echo -e "${YELLOW}Cleaning old backups (older than $RETENTION_DAYS days)...${NC}"
find $BACKUP_DIR -name "narra_forge_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# List remaining backups
echo ""
echo -e "${GREEN}=== Available Backups ===${NC}"
ls -lh $BACKUP_DIR/narra_forge_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo ""
echo -e "${GREEN}=== Backup Complete ===${NC}"
