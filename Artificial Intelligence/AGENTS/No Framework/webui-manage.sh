#!/bin/bash

# Open WebUI Management Script
# Provides easy commands to manage Open WebUI Docker container

COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.docker"

show_help() {
    echo "Open WebUI Management Commands"
    echo "============================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start Open WebUI and AI Agent services"
    echo "  stop     - Stop Open WebUI container"
    echo "  restart  - Restart Open WebUI container" 
    echo "  logs     - Show Open WebUI logs"
    echo "  status   - Show service status"
    echo "  health   - Check health of all services"
    echo "  update   - Update Open WebUI to latest version"
    echo "  reset    - Reset Open WebUI data (removes all chats)"
    echo "  backup   - Backup Open WebUI data"
    echo "  restore  - Restore Open WebUI data from backup"
    echo "  shell    - Access Open WebUI container shell"
    echo "  cleanup  - Remove stopped containers and unused images"
    echo ""
}

check_ai_agent() {
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ AI Agent: Running"
        return 0
    else
        echo "❌ AI Agent: Not running"
        return 1
    fi
}

check_ollama() {
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✅ Ollama: Running"
        return 0
    else
        echo "❌ Ollama: Not running"
        return 1
    fi
}

check_webui() {
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Open WebUI: Running"
        return 0
    else
        echo "❌ Open WebUI: Not running"
        return 1
    fi
}

start_services() {
    echo "🚀 Starting services..."
    
    # Check if AI Agent is running
    if ! check_ai_agent > /dev/null; then
        echo "⚠️  AI Agent is not running. Please start it first:"
        echo "   source venv/bin/activate && python src/index.py"
        echo ""
    fi
    
    # Start Open WebUI
    docker-compose --env-file "$ENV_FILE" up -d
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    echo "📊 Service Status:"
    check_ai_agent
    check_ollama
    check_webui
    
    if check_webui > /dev/null; then
        echo ""
        echo "🌟 Open WebUI is running at: http://localhost:3000"
    fi
}

stop_services() {
    echo "🛑 Stopping Open WebUI..."
    docker-compose down
    echo "✅ Services stopped"
}

restart_services() {
    echo "🔄 Restarting Open WebUI..."
    docker-compose restart
    sleep 5
    check_webui
}

show_logs() {
    echo "📋 Open WebUI Logs (Press Ctrl+C to exit):"
    docker-compose logs -f open-webui
}

show_status() {
    echo "📊 Service Status"
    echo "=================="
    check_ai_agent
    check_ollama  
    check_webui
    
    echo ""
    echo "🐳 Docker Status:"
    docker-compose ps
}

health_check() {
    echo "🏥 Health Check"
    echo "==============="
    
    # Check AI Agent health
    echo "Checking AI Agent..."
    if curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null; then
        echo "✅ AI Agent health check passed"
    else
        echo "❌ AI Agent health check failed"
    fi
    
    echo ""
    
    # Check Open WebUI
    echo "Checking Open WebUI..."
    if curl -s http://localhost:3000/health > /dev/null; then
        echo "✅ Open WebUI health check passed"
    else
        echo "❌ Open WebUI health check failed"
    fi
    
    echo ""
    
    # Test integration
    echo "Testing integration..."
    TEST_RESPONSE=$(curl -s -X POST http://localhost:3000/api/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"messages":[{"role":"user","content":"Hello"}],"model":"ai-agent-no-framework"}' 2>/dev/null)
    
    if echo "$TEST_RESPONSE" | grep -q "choices"; then
        echo "✅ AI Agent integration working"
    else
        echo "❌ AI Agent integration failed"
    fi
}

update_webui() {
    echo "⬆️  Updating Open WebUI..."
    docker-compose pull
    docker-compose up -d
    echo "✅ Update completed"
}

reset_data() {
    echo "⚠️  This will delete all Open WebUI data (chats, settings, etc.)"
    read -p "Are you sure? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        docker-compose down
        docker volume rm "$(basename $(pwd))_open-webui-data" 2>/dev/null || true
        echo "🗑️  Data reset completed"
        echo "Run '$0 start' to start fresh"
    else
        echo "❌ Reset cancelled"
    fi
}

backup_data() {
    BACKUP_FILE="open-webui-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
    echo "💾 Creating backup: $BACKUP_FILE"
    
    if docker-compose ps | grep -q "Up"; then
        docker exec "$(docker-compose ps -q open-webui)" tar czf - /app/backend/data > "$BACKUP_FILE"
        echo "✅ Backup created: $BACKUP_FILE"
    else
        echo "❌ Open WebUI is not running"
        exit 1
    fi
}

restore_data() {
    if [ -z "$2" ]; then
        echo "Usage: $0 restore <backup-file.tar.gz>"
        exit 1
    fi
    
    BACKUP_FILE="$2"
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "❌ Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    echo "📁 Restoring from: $BACKUP_FILE"
    docker exec -i "$(docker-compose ps -q open-webui)" tar xzf - -C / < "$BACKUP_FILE"
    echo "✅ Restore completed"
    restart_services
}

access_shell() {
    echo "🐚 Accessing Open WebUI container shell..."
    docker exec -it "$(docker-compose ps -q open-webui)" /bin/bash
}

cleanup() {
    echo "🧹 Cleaning up Docker resources..."
    docker system prune -f
    docker volume prune -f
    echo "✅ Cleanup completed"
}

# Main command handling
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    health)
        health_check
        ;;
    update)
        update_webui
        ;;
    reset)
        reset_data
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data "$@"
        ;;
    shell)
        access_shell
        ;;
    cleanup)
        cleanup
        ;;
    *)
        show_help
        ;;
esac
