# AI Agent - No Framework Makefile
# Provides convenient commands for development and testing

.PHONY: help install clean test test-api run dev health setup ollama webui-setup webui-start webui-stop webui-logs

# Default target
help:
	@echo "AI Agent - No Framework"
	@echo "======================="
	@echo ""
	@echo "Available commands:"
	@echo "  make setup      - Run initial setup (install dependencies, create venv)"
	@echo "  make install    - Install Python dependencies only"
	@echo "  make run        - Start the AI agent server"
	@echo "  make dev        - Start server in development mode with reload"
	@echo "  make test       - Test individual components"
	@echo "  make test-api   - Test API endpoints (server must be running)"
	@echo "  make health     - Quick health check"
	@echo "  make clean      - Clean virtual environment and cache files"
	@echo "  make ollama     - Show Ollama setup commands"
	@echo ""
	@echo "Open WebUI commands:"
	@echo "  make webui-setup - Setup Open WebUI in Docker"
	@echo "  make webui-start - Start Open WebUI container"
	@echo "  make webui-stop  - Stop Open WebUI container"
	@echo "  make webui-logs  - Show Open WebUI logs"
	@echo "  make webui-health- Check all services health"
	@echo "  make full-stack  - Start AI Agent + Open WebUI"
	@echo ""

# Setup everything
setup:
	@echo "🚀 Running full setup..."
	./setup.sh

# Install dependencies only
install:
	@echo "📥 Installing dependencies..."
	@if [ ! -d "venv" ]; then python3 -m venv venv; fi
	@. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Run the server
run:
	@echo "🌟 Starting AI Agent server..."
	@. venv/bin/activate && python src/index.py

# Development mode with reload
dev:
	@echo "🔧 Starting in development mode..."
	@. venv/bin/activate && ENVIRONMENT=development python src/index.py

# Test components
test:
	@echo "🧪 Testing components..."
	@. venv/bin/activate && python test_components.py

# Test API endpoints
test-api:
	@echo "🌐 Testing API endpoints..."
	./test_api.sh

# Quick health check
health:
	@echo "🏥 Health check..."
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ Server not running or unhealthy"

# Clean environment
clean:
	@echo "🧹 Cleaning up..."
	rm -rf venv/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned"

# Show Ollama setup
ollama:
	@echo "🦙 Ollama Setup Commands"
	@echo "========================"
	@echo ""
	@echo "1. Install Ollama:"
	@echo "   curl -fsSL https://ollama.com/install.sh | sh"
	@echo ""
	@echo "2. Start Ollama service:"
	@echo "   ollama serve"
	@echo ""
	@echo "3. Pull Llama model (in another terminal):"
	@echo "   ollama pull llama3.1:8b-instruct-q4_0"
	@echo ""
	@echo "4. Verify installation:"
	@echo "   ollama list"
	@echo ""
	@echo "Alternative models (smaller/larger):"
	@echo "   ollama pull llama3.1:7b-instruct-q4_0  # Smaller"
	@echo "   ollama pull llama3.1:8b-instruct-q8_0  # Higher quality"
	@echo ""

# Development shortcuts
.PHONY: start stop restart logs
start: run
stop:
	@pkill -f "python src/index.py" || echo "No server process found"
restart: stop
	@sleep 2
	@make run
logs:
	@tail -f logs/agent.log 2>/dev/null || echo "No log file found"

# Open WebUI targets
webui-setup:
	@echo "🌐 Setting up Open WebUI..."
	./setup-webui.sh

webui-start:
	@echo "🚀 Starting Open WebUI..."
	./webui-manage.sh start

webui-stop:
	@echo "🛑 Stopping Open WebUI..."
	./webui-manage.sh stop

webui-logs:
	@echo "📋 Open WebUI logs..."
	./webui-manage.sh logs

webui-health:
	@echo "🏥 Checking all services..."
	./webui-manage.sh health

# Start full stack (AI Agent + Open WebUI)
full-stack:
	@echo "🚀 Starting full stack..."
	@echo "1. Starting AI Agent..."
	@. venv/bin/activate && python src/index.py &
	@sleep 5
	@echo "2. Starting Open WebUI..."
	@./webui-manage.sh start
	@echo "✅ Full stack running!"
	@echo "🤖 AI Agent: http://localhost:8000"
	@echo "🌐 Open WebUI: http://localhost:3000"
