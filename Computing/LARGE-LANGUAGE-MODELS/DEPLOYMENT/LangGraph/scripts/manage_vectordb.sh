#!/bin/bash

# Complete Vector Database Management Script
# Usage: ./scripts/manage_vectordb.sh [start|stop|restart|status|init|reset]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QDRANT_CONTAINER="qdrant_vectordb"
QDRANT_URL="http://localhost:6333"

show_help() {
    echo "Vector Database Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start Qdrant vector database"
    echo "  stop      Stop Qdrant (preserves data)"
    echo "  restart   Restart Qdrant service"
    echo "  status    Show current status"
    echo "  init      Initialize collections and indexes"
    echo "  reset     Stop and remove all data (destructive)"
    echo "  backup    Create backup of vector data"
    echo "  restore   Restore from backup"
    echo "  logs      Show container logs"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start the database"
    echo "  $0 status         # Check if running"
    echo "  $0 init           # Set up collections"
    echo "  $0 reset          # Complete reset (careful!)"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed or not in PATH"
        exit 1
    fi
}

get_status() {
    if docker ps --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
        echo "running"
    elif docker ps -a --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
        echo "stopped"
    else
        echo "not_found"
    fi
}

show_status() {
    local status=$(get_status)
    echo "📊 Qdrant Vector Database Status"
    echo "================================="
    
    case $status in
        "running")
            echo "🟢 Status: Running"
            docker ps --filter "name=$QDRANT_CONTAINER" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            echo ""
            if curl -s "$QDRANT_URL/health" >/dev/null 2>&1; then
                echo "🌐 API: Healthy ($QDRANT_URL)"
                echo "📊 Dashboard: $QDRANT_URL/dashboard"
                
                # Show collections if API is available
                if collections=$(curl -s "$QDRANT_URL/collections" 2>/dev/null); then
                    echo ""
                    echo "📚 Collections:"
                    echo "$collections" | jq -r '.result.collections[]? | "   - \(.name) (\(.vectors_count // 0) vectors)"' 2>/dev/null || echo "   No collections found"
                fi
            else
                echo "🔴 API: Not responding"
            fi
            ;;
        "stopped")
            echo "🟡 Status: Stopped (container exists)"
            echo "   Use 'start' command to restart"
            ;;
        "not_found")
            echo "⚪ Status: Not created"
            echo "   Use 'start' command to create and start"
            ;;
    esac
}

start_service() {
    echo "🚀 Starting Qdrant Vector Database..."
    "$SCRIPT_DIR/start_qdrant.sh"
}

stop_service() {
    echo "🛑 Stopping Qdrant Vector Database..."
    "$SCRIPT_DIR/stop_qdrant.sh"
}

restart_service() {
    local status=$(get_status)
    if [[ "$status" == "running" ]]; then
        stop_service
        sleep 2
    fi
    start_service
}

init_collections() {
    echo "🏗️  Initializing Collections..."
    "$SCRIPT_DIR/init_collections.sh"
}

reset_database() {
    echo "⚠️  This will completely remove all vector data!"
    read -p "Are you sure? Type 'yes' to confirm: " -r
    if [[ $REPLY == "yes" ]]; then
        echo "🗑️  Resetting vector database..."
        "$SCRIPT_DIR/stop_qdrant.sh" --remove
        rm -rf "./data/qdrant_storage"
        echo "✅ Database reset complete"
    else
        echo "❌ Reset cancelled"
    fi
}

backup_data() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="./backups/qdrant_$timestamp"
    
    echo "💾 Creating backup..."
    mkdir -p "$backup_dir"
    
    if [ -d "./data/qdrant_storage" ]; then
        cp -r "./data/qdrant_storage" "$backup_dir/"
        echo "✅ Backup created: $backup_dir"
    else
        echo "❌ No data directory found"
        exit 1
    fi
}

restore_data() {
    echo "📋 Available backups:"
    if [ -d "./backups" ]; then
        ls -la ./backups/ | grep qdrant || echo "No backups found"
    else
        echo "No backups directory found"
        exit 1
    fi
    
    read -p "Enter backup folder name (e.g., qdrant_20240808_143000): " backup_name
    
    if [ -d "./backups/$backup_name" ]; then
        stop_service
        rm -rf "./data/qdrant_storage"
        cp -r "./backups/$backup_name/qdrant_storage" "./data/"
        echo "✅ Backup restored from $backup_name"
        start_service
    else
        echo "❌ Backup not found: $backup_name"
        exit 1
    fi
}

show_logs() {
    echo "📋 Qdrant Container Logs:"
    echo "========================"
    if docker ps --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
        docker logs -f "$QDRANT_CONTAINER"
    else
        echo "❌ Container is not running"
        exit 1
    fi
}

# Main script logic
check_docker

case "${1:-help}" in
    "start")
        start_service
        ;;
    "stop")
        stop_service
        ;;
    "restart")
        restart_service
        ;;
    "status")
        show_status
        ;;
    "init")
        init_collections
        ;;
    "reset")
        reset_database
        ;;
    "backup")
        backup_data
        ;;
    "restore")
        restore_data
        ;;
    "logs")
        show_logs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
