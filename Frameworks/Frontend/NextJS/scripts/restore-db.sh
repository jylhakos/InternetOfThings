#!/bin/bash

echo "🔄 Restoring database from backup..."

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo "❌ Please provide a backup file!"
    echo "Usage: $0 <backup-file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -la ./backups/backup_*.sql.gz 2>/dev/null || echo "   No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file '$BACKUP_FILE' not found!"
    exit 1
fi

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

# Confirm restoration
echo "⚠️  This will replace all data in database '$POSTGRES_DB'"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Database restoration cancelled."
    exit 0
fi

# Create temporary file for decompressed backup
TEMP_FILE="/tmp/restore_$(basename "$BACKUP_FILE" .gz)"

# Decompress backup
echo "📦 Decompressing backup file..."
gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"

if [ $? -ne 0 ]; then
    echo "❌ Failed to decompress backup file!"
    rm -f "$TEMP_FILE"
    exit 1
fi

# Drop existing database and recreate
echo "🗄️ Recreating database..."
docker exec webapp_postgres psql -U "$POSTGRES_USER" -c "DROP DATABASE IF EXISTS $POSTGRES_DB;"
docker exec webapp_postgres psql -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB;"

# Restore database
echo "⬆️ Restoring database from backup..."
docker exec -i webapp_postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "$TEMP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Database restoration completed successfully!"
    echo "🔄 Running Prisma generate to sync schema..."
    npx prisma generate
    echo "✨ Database restore process completed!"
else
    echo "❌ Database restoration failed!"
    rm -f "$TEMP_FILE"
    exit 1
fi

# Clean up temporary file
rm -f "$TEMP_FILE"
