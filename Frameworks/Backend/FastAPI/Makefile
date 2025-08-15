.PHONY: help install dev-start dev-stop dev-reset test lint build clean docker-build docker-up docker-down

# Default target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation
install: ## Install all dependencies
	@echo "🔧 Installing backend dependencies..."
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "🔧 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed"

# Development
dev-start: ## Start development environment
	@echo "🚀 Starting development environment..."
	docker-compose up -d postgres redis
	@echo "⏳ Waiting for services to be ready..."
	@until docker exec fastapi_postgres pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done
	@until docker exec fastapi_redis redis-cli ping >/dev/null 2>&1; do sleep 1; done
	@echo "✅ Infrastructure services are ready"
	@echo "🖥️  Start backend: make backend-dev"
	@echo "🖥️  Start frontend: make frontend-dev"

backend-dev: ## Start FastAPI backend in development mode
	@echo "🐍 Starting FastAPI backend..."
	. venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Start React frontend in development mode
	@echo "⚛️  Starting React frontend..."
	cd frontend && npm run dev

dev-stop: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	docker-compose down
	@echo "✅ Development environment stopped"

dev-reset: ## Reset development environment (remove all data)
	@echo "🔄 Resetting development environment..."
	docker-compose down -v
	docker-compose up -d postgres redis
	@echo "⏳ Waiting for services to be ready..."
	@until docker exec fastapi_postgres pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done
	@until docker exec fastapi_redis redis-cli ping >/dev/null 2>&1; do sleep 1; done
	@echo "✅ Development environment reset"

# Testing
test: ## Run all tests
	@echo "🧪 Running backend tests..."
	. venv/bin/activate && pytest tests/ -v --cov=./ --cov-report=html
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test -- --run
	@echo "✅ All tests completed"

test-backend: ## Run backend tests only
	@echo "🐍 Running backend tests..."
	. venv/bin/activate && pytest tests/ -v

test-frontend: ## Run frontend tests only
	@echo "⚛️  Running frontend tests..."
	cd frontend && npm test -- --run

test-load: ## Run load tests
	@echo "⚡ Running load tests..."
	./performance-test.sh
	. venv/bin/activate && locust -f tests/load_test.py --headless -u 50 -r 10 -t 30s --host http://localhost:8000

# Code Quality
lint: ## Run linting on all code
	@echo "🔍 Linting backend code..."
	. venv/bin/activate && flake8 . --exclude=venv --max-line-length=88
	. venv/bin/activate && black --check .
	. venv/bin/activate && isort --check-only .
	@echo "🔍 Linting frontend code..."
	cd frontend && npm run lint
	@echo "✅ Linting completed"

format: ## Format all code
	@echo "✨ Formatting backend code..."
	. venv/bin/activate && black .
	. venv/bin/activate && isort .
	@echo "✨ Formatting frontend code..."
	cd frontend && npm run format
	@echo "✅ Code formatted"

security-scan: ## Run security scans
	@echo "🔒 Running security scans..."
	. venv/bin/activate && bandit -r . -f json -o bandit-report.json
	cd frontend && npm audit
	@echo "✅ Security scan completed"

# Building
build: ## Build for production
	@echo "🏗️  Building backend..."
	. venv/bin/activate && python -m compileall .
	@echo "🏗️  Building frontend..."
	cd frontend && npm run build
	@echo "✅ Build completed"

build-docker: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build
	@echo "✅ Docker images built"

# Production
docker-up: ## Start production environment with Docker
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production environment started"

docker-down: ## Stop production environment
	@echo "🛑 Stopping production environment..."
	docker-compose -f docker-compose.prod.yml down
	@echo "✅ Production environment stopped"

# Monitoring
monitor-start: ## Start monitoring stack (Prometheus, Grafana, Jaeger)
	@echo "📊 Starting monitoring stack..."
	docker-compose -f docker-compose.monitoring.yml up -d
	@echo "📈 Prometheus: http://localhost:9090"
	@echo "📊 Grafana: http://localhost:3000 (admin/admin)"
	@echo "🔍 Jaeger: http://localhost:16686"

monitor-stop: ## Stop monitoring stack
	@echo "🛑 Stopping monitoring stack..."
	docker-compose -f docker-compose.monitoring.yml down

# Database
db-migrate: ## Run database migrations
	@echo "🗄️  Running database migrations..."
	. venv/bin/activate && alembic upgrade head

db-seed: ## Seed database with test data
	@echo "🌱 Seeding database..."
	. venv/bin/activate && python scripts/seed_database.py

db-reset: ## Reset database
	@echo "🔄 Resetting database..."
	docker-compose restart postgres
	@until docker exec fastapi_postgres pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done
	$(MAKE) db-migrate db-seed

# Utilities
logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f fastapi

logs-db: ## Show database logs
	docker-compose logs -f postgres

logs-redis: ## Show redis logs
	docker-compose logs -f redis

health-check: ## Check health of all services
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Backend health check failed"
	@curl -f http://localhost:5173 || echo "❌ Frontend health check failed"
	@docker exec fastapi_postgres pg_isready -U postgres || echo "❌ Database health check failed"
	@docker exec fastapi_redis redis-cli ping || echo "❌ Redis health check failed"

clean: ## Clean up build artifacts and caches
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage bandit-report.json
	cd frontend && npm run clean 2>/dev/null || true
	docker system prune -f
	@echo "✅ Cleanup completed"

# Quick commands
quick-start: dev-start backend-dev ## Quick start (infrastructure + backend)

full-start: install dev-start ## Full start (install + dev environment)

ci: lint test security-scan build ## Run CI pipeline locally
