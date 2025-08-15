#!/bin/bash
# setup-devops.sh - Comprehensive DevOps Setup Script for FastAPI

set -e  # Exit on any error

echo "🚀 FastAPI DevOps Setup Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if command -v $1 &> /dev/null; then
        log_info "$1 is installed"
        return 0
    else
        log_error "$1 is not installed"
        return 1
    fi
}

# Check system requirements
log_info "Checking system requirements..."

REQUIRED_COMMANDS=("python3" "pip3" "docker" "curl" "git")
MISSING_COMMANDS=()

for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! check_command $cmd; then
        MISSING_COMMANDS+=($cmd)
    fi
done

if [ ${#MISSING_COMMANDS[@]} -ne 0 ]; then
    log_error "Missing required commands: ${MISSING_COMMANDS[*]}"
    log_info "Installing missing packages..."
    
    # Update package manager
    sudo apt update
    
    # Install missing packages
    for cmd in "${MISSING_COMMANDS[@]}"; do
        case $cmd in
            python3)
                sudo apt install -y python3 python3-dev python3-venv python3-pip
                ;;
            pip3)
                sudo apt install -y python3-pip
                ;;
            docker)
                curl -fsSL https://get.docker.com -o get-docker.sh
                sudo sh get-docker.sh
                sudo usermod -aG docker $USER
                log_warn "You need to log out and back in for docker group changes to take effect"
                ;;
            curl)
                sudo apt install -y curl
                ;;
            git)
                sudo apt install -y git
                ;;
        esac
    done
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
MIN_PYTHON_VERSION="3.9"

if [ "$(printf '%s\n' "$MIN_PYTHON_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$MIN_PYTHON_VERSION" ]; then
    log_info "Python version $PYTHON_VERSION meets requirements (>= $MIN_PYTHON_VERSION)"
else
    log_error "Python version $PYTHON_VERSION is below minimum required version $MIN_PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
log_info "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_info "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
log_info "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    log_info "Dependencies installed from requirements.txt"
else
    log_warn "requirements.txt not found, installing basic dependencies..."
    pip install fastapi uvicorn gunicorn
fi

# Setup Docker services
log_info "Setting up Docker services..."

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    log_error "Neither docker-compose nor docker compose plugin found"
    exit 1
fi

# Start infrastructure services
if [ -f "docker-compose.yml" ]; then
    log_info "Starting Docker services..."
    $DOCKER_COMPOSE_CMD up -d postgres redis
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    echo -n "Waiting for PostgreSQL..."
    while ! docker exec fastapi_postgres pg_isready -U postgres 2>/dev/null; do
        echo -n "."
        sleep 1
    done
    echo " Ready!"
    
    # Wait for Redis
    echo -n "Waiting for Redis..."
    while ! docker exec fastapi_redis redis-cli ping 2>/dev/null | grep -q PONG; do
        echo -n "."
        sleep 1
    done
    echo " Ready!"
    
else
    log_warn "docker-compose.yml not found, starting individual containers..."
    
    # Start PostgreSQL
    docker run -d --name postgres \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=password \
        -e POSTGRES_DB=microservices \
        -p 5432:5432 \
        postgres:14 || log_info "PostgreSQL container already exists"
    
    # Start Redis
    docker run -d --name redis \
        -p 6379:6379 \
        redis:7-alpine || log_info "Redis container already exists"
fi

# Frontend setup
if [ -d "frontend" ]; then
    log_info "Setting up frontend dependencies..."
    cd frontend
    
    if command -v npm &> /dev/null; then
        npm install
        log_info "Frontend dependencies installed"
    else
        log_warn "npm not found, skipping frontend setup"
    fi
    
    cd ..
fi

# Create environment file if not exists
if [ ! -f ".env" ]; then
    log_info "Creating .env file..."
    cat > .env << EOF
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/microservices
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# gRPC
GRPC_PORT=50051
AUTH_SERVICE_URL=localhost:50051

# Application
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Monitoring
ENABLE_METRICS=True
LOG_LEVEL=INFO
EOF
    log_info ".env file created"
else
    log_info ".env file already exists"
fi

# Create performance test script
log_info "Creating performance test scripts..."
cat > performance-test.sh << 'EOF'
#!/bin/bash
# FastAPI Performance Test Script

BASE_URL="http://localhost:8000"
HEALTH_ENDPOINT="$BASE_URL/health"
AUTH_ENDPOINT="$BASE_URL/auth/login"

echo "🔥 FastAPI Performance Testing"
echo "=============================="

# Test 1: Health endpoint performance
echo "1. Health Endpoint Test (100 requests, 10 concurrent)"
seq 1 100 | xargs -n1 -P10 -I{} curl -s -o /dev/null -w "%{time_total}\n" $HEALTH_ENDPOINT | \
awk '{ sum+=$1; count++ } END { 
    print "Average response time: " sum/count "s"
    print "Total requests: " count
}'

# Test 2: Authentication load test
echo "2. Authentication Load Test (10 sequential requests)"
for i in $(seq 1 10); do
    time curl -X POST $AUTH_ENDPOINT \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test&password=test" \
        -s -o /dev/null \
        -w "Login $i: %{time_total}s %{http_code}\n"
done

echo "Performance test completed!"
EOF

chmod +x performance-test.sh

# Create cURL test cases
log_info "Creating cURL test script..."
cat > curl-tests.sh << 'EOF'
#!/bin/bash
# Comprehensive cURL Test Cases for FastAPI

BASE_URL="http://localhost:8000"

echo "🧪 FastAPI cURL Test Suite"
echo "=========================="

# Create timing format file
cat > curl-format.txt << 'CURL_FORMAT'
     time_namelookup:  %{time_namelookup}s
        time_connect:  %{time_connect}s
     time_appconnect:  %{time_appconnect}s
    time_pretransfer:  %{time_pretransfer}s
       time_redirect:  %{time_redirect}s
  time_starttransfer:  %{time_starttransfer}s
                     ----------
          time_total:  %{time_total}s
           http_code:  %{http_code}
       response_size:  %{size_download} bytes
CURL_FORMAT

# Test 1: Health check
echo "1. Health Check Test"
curl -X GET $BASE_URL/health \
    -w "@curl-format.txt" \
    -o /dev/null -s
echo ""

# Test 2: API Documentation
echo "2. API Documentation Test"
curl -X GET $BASE_URL/docs \
    -w "Docs load time: %{time_total}s, Status: %{http_code}\n" \
    -o /dev/null -s
echo ""

# Test 3: Metrics endpoint
echo "3. Metrics Endpoint Test"
curl -X GET $BASE_URL/metrics \
    -w "Metrics time: %{time_total}s, Status: %{http_code}\n" \
    -s | head -10
echo ""

# Test 4: Registration (if endpoint exists)
echo "4. User Registration Test"
curl -X POST $BASE_URL/auth/register \
    -H "Content-Type: application/json" \
    -d '{
        "phone": "+1234567890",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "full_name": "Test User"
    }' \
    -w "Registration time: %{time_total}s, Status: %{http_code}\n" \
    -v
echo ""

# Cleanup
rm -f curl-format.txt

echo "cURL tests completed!"
EOF

chmod +x curl-tests.sh

# Create start script
log_info "Creating start scripts..."
cat > start-dev.sh << 'EOF'
#!/bin/bash
# Start FastAPI in development mode

echo "🚀 Starting FastAPI Development Server"
echo "======================================"

# Activate virtual environment
source venv/bin/activate

# Start FastAPI with auto-reload
echo "Starting server at http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF

chmod +x start-dev.sh

cat > start-prod.sh << 'EOF'
#!/bin/bash
# Start FastAPI in production mode

echo "🏭 Starting FastAPI Production Server"
echo "===================================="

# Activate virtual environment  
source venv/bin/activate

# Calculate optimal workers (number of CPU cores * 2 + 1)
WORKERS=$(($(nproc) * 2 + 1))
echo "Starting with $WORKERS workers"

# Start with Gunicorn + Uvicorn workers
gunicorn main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --worker-connections 1000 \
    --max-requests 10000 \
    --max-requests-jitter 1000 \
    --preload \
    --timeout 120 \
    --log-level info
EOF

chmod +x start-prod.sh

# Final setup verification
log_info "Running setup verification..."

# Check virtual environment
if [ -f "venv/bin/activate" ]; then
    log_info "✅ Virtual environment created"
else
    log_error "❌ Virtual environment creation failed"
fi

# Check Docker services
if docker ps | grep -q postgres && docker ps | grep -q redis; then
    log_info "✅ Docker services running"
else
    log_warn "⚠️ Some Docker services may not be running"
fi

# Check environment file
if [ -f ".env" ]; then
    log_info "✅ Environment file created"
else
    log_warn "⚠️ Environment file not found"
fi

echo ""
log_info "🎉 DevOps setup completed!"
echo "=============================="
echo ""
echo "Next steps:"
echo "1. Review and update .env file with your configurations"
echo "2. Start development server: ./start-dev.sh"
echo "3. Run tests: ./curl-tests.sh"
echo "4. Run performance tests: ./performance-test.sh"
echo "5. For production: ./start-prod.sh"
echo ""
echo "Useful commands:"
echo "  - Activate venv: source venv/bin/activate"
echo "  - Check services: docker ps"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo ""

log_info "Happy coding! 🚀"
