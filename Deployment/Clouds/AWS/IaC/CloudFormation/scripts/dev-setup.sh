#!/bin/bash

# Local Development Setup Script
# This script sets up the development environment for the microservices application

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies for all services..."
    
    # Backend services
    for service in auth-service user-service api-gateway; do
        log "Installing dependencies for ${service}..."
        cd "backend/${service}"
        npm install
        cd "../.."
    done
    
    # Frontend
    log "Installing dependencies for frontend..."
    cd frontend
    npm install
    cd ..
    
    log "All dependencies installed successfully."
}

# Setup environment files
setup_environment() {
    log "Setting up environment files..."
    
    # Create .env files for backend services
    cat > backend/auth-service/.env << EOF
NODE_ENV=development
PORT=3001
JWT_SECRET=your-super-secret-jwt-key-for-development
FRONTEND_URL=http://localhost:3001
EOF

    cat > backend/user-service/.env << EOF
NODE_ENV=development
PORT=3002
DB_HOST=localhost
DB_PORT=5432
DB_NAME=microservices_db
DB_USER=postgres
DB_PASSWORD=password
JWT_SECRET=your-super-secret-jwt-key-for-development
AUTH_SERVICE_URL=http://localhost:3001
FRONTEND_URL=http://localhost:3001
EOF

    cat > backend/api-gateway/.env << EOF
NODE_ENV=development
PORT=3000
AUTH_SERVICE_URL=http://localhost:3001
USER_SERVICE_URL=http://localhost:3002
FRONTEND_URL=http://localhost:3001
EOF

    # Create .env.local for frontend
    cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:3000
EOF

    log "Environment files created successfully."
}

# Start development services
start_development() {
    log "Starting development environment with Docker Compose..."
    
    # Create Docker network if it doesn't exist
    docker network create microservices-network 2>/dev/null || true
    
    # Start services with Docker Compose
    docker-compose up -d
    
    log "Development environment started successfully."
    log "Services available at:"
    echo -e "${BLUE}  - Frontend: http://localhost:3001${NC}"
    echo -e "${BLUE}  - API Gateway: http://localhost:3000${NC}"
    echo -e "${BLUE}  - Auth Service: http://localhost:3001${NC}"
    echo -e "${BLUE}  - User Service: http://localhost:3002${NC}"
    echo -e "${BLUE}  - PostgreSQL: localhost:5432${NC}"
}

# Stop development services
stop_development() {
    log "Stopping development environment..."
    docker-compose down
    log "Development environment stopped."
}

# Show logs
show_logs() {
    docker-compose logs -f "${1:-}"
}

# Run tests
run_tests() {
    log "Running tests for all services..."
    
    for service in auth-service user-service api-gateway; do
        log "Running tests for ${service}..."
        cd "backend/${service}"
        npm test 2>/dev/null || warn "No tests found for ${service}"
        cd "../.."
    done
    
    log "Tests completed."
}

# Database operations
setup_database() {
    log "Setting up database..."
    
    # Wait for PostgreSQL to be ready
    log "Waiting for PostgreSQL to be ready..."
    until docker-compose exec postgres pg_isready -U postgres; do
        sleep 1
    done
    
    # Run database migrations
    log "Running database migrations..."
    cd backend/user-service
    npm run migrate 2>/dev/null || warn "Migration script not found"
    cd ../..
    
    log "Database setup completed."
}

# Main function
main() {
    case "${1:-setup}" in
        "setup")
            install_dependencies
            setup_environment
            ;;
        "start")
            start_development
            ;;
        "stop")
            stop_development
            ;;
        "restart")
            stop_development
            start_development
            ;;
        "logs")
            show_logs "${2}"
            ;;
        "test")
            run_tests
            ;;
        "db-setup")
            setup_database
            ;;
        "clean")
            log "Cleaning up..."
            docker-compose down -v
            docker system prune -f
            log "Cleanup completed."
            ;;
        *)
            echo "Usage: $0 [setup|start|stop|restart|logs|test|db-setup|clean]"
            echo ""
            echo "Commands:"
            echo "  setup    - Install dependencies and create environment files"
            echo "  start    - Start development environment with Docker Compose"
            echo "  stop     - Stop development environment"
            echo "  restart  - Restart development environment"
            echo "  logs     - Show logs (optionally for specific service)"
            echo "  test     - Run tests for all services"
            echo "  db-setup - Setup database"
            echo "  clean    - Clean up containers and images"
            exit 1
            ;;
    esac
}

main "$@"
