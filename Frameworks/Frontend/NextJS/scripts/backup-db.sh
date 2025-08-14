#!/bin/bash

echo "📦 Creating database backup..."

# Get current date for backup filename
BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups"

# Create backups directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Set default values if not in environment
POSTGRES_USER=${POSTGRES_USER:-webapp_user}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-webapp_password}
POSTGRES_DB=${POSTGRES_DB:-webapp_db}

# Check if PostgreSQL container is running
if ! docker ps | grep webapp_postgres > /dev/null 2>&1; then
    echo "❌ PostgreSQL container is not running!"
    echo "   Please start the database first: docker-compose up -d postgres"
    exit 1
fi

# Create database dump
BACKUP_FILE="$BACKUP_DIR/backup_${POSTGRES_DB}_${BACKUP_DATE}.sql"

echo "🗄️ Backing up database to $BACKUP_FILE..."

docker exec webapp_postgres pg_dump \
    -U "$POSTGRES_USER" \
    -h localhost \
    -d "$POSTGRES_DB" \
    --no-password > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
    # Compress backup
    gzip "$BACKUP_FILE"
    COMPRESSED_FILE="$BACKUP_FILE.gz"
    
    echo "✅ Database backup completed successfully!"
    echo "📁 Backup file: $COMPRESSED_FILE"
    echo "📊 Backup size: $(du -h "$COMPRESSED_FILE" | cut -f1)"
    
    # Keep only last 7 backups
    echo "🧹 Cleaning up old backups (keeping last 7)..."
    ls -t "$BACKUP_DIR"/backup_*.sql.gz | tail -n +8 | xargs -r rm
    
    echo "✨ Backup cleanup completed!"
else
    echo "❌ Database backup failed!"
    rm -f "$BACKUP_FILE"
    exit 1
fi
