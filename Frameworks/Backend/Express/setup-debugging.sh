#!/bin/bash

# Express.js Debugging Setup Script for Linux/Debian

set -e

echo "🚀 Setting up Express.js debugging environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    print_info "Visit: https://nodejs.org/ or use nvm"
    exit 1
fi

# Check if VS Code is installed
if ! command -v code &> /dev/null; then
    print_warning "VS Code is not installed. Debugging features will be limited."
    print_info "Install VS Code: https://code.visualstudio.com/"
else
    print_status "VS Code found"
fi

# Check Node.js version
NODE_VERSION=$(node -v)
print_status "Node.js version: $NODE_VERSION"

# Install VS Code extensions if VS Code is available
if command -v code &> /dev/null; then
    print_info "Installing essential VS Code extensions..."
    
    extensions=(
        "ms-vscode.vscode-node-debug2"
        "ms-vscode.js-debug"
        "github.copilot"
        "github.copilot-chat"
        "rangav.vscode-thunder-client"
        "ms-vscode.vscode-typescript-next"
        "bradlc.vscode-tailwindcss"
        "ms-vscode.vscode-json"
        "christian-kohler.path-intellisense"
        "formulahendry.auto-rename-tag"
        "esbenp.prettier-vscode"
    )
    
    for extension in "${extensions[@]}"; do
        if code --list-extensions | grep -q "$extension"; then
            print_status "$extension already installed"
        else
            print_info "Installing $extension..."
            code --install-extension "$extension" --force
        fi
    done
fi

# Create debugging scripts
print_info "Creating debugging helper scripts..."

# Create debug.sh
cat > debug.sh << 'EOF'
#!/bin/bash
echo "🐛 Starting Express.js application in debug mode..."
echo "Debug server will be available at http://localhost:3000"
echo "Debugger will listen on port 9229"
echo "Connect Chrome DevTools to chrome://inspect"
echo ""
NODE_ENV=development DEBUG=express:*,app:* node --inspect app.js
EOF

chmod +x debug.sh

# Create test.sh
cat > test.sh << 'EOF'
#!/bin/bash
echo "🧪 Running tests for Express.js application..."
echo ""

# Run different test suites
echo "Running Mocha tests..."
npm test

echo ""
echo "Running performance tests..."
time curl -s http://localhost:3000 > /dev/null

echo ""
echo "Testing memory endpoint..."
curl -s http://localhost:3000/memory | jq '.' || echo "Install jq for pretty JSON output: sudo apt install jq"
EOF

chmod +x test.sh

# Create docker-debug.sh
cat > docker-debug.sh << 'EOF'
#!/bin/bash
echo "🐳 Starting Express.js application with Docker in debug mode..."
echo "Building and starting containers..."
docker-compose -f docker-compose.dev.yml up --build -d

echo ""
echo "Containers started. Access points:"
echo "  Application: http://localhost:3000"
echo "  Debug port: 9229"
echo "  PostgreSQL: localhost:5432"
echo "  Redis: localhost:6379"
echo ""
echo "To attach debugger in VS Code:"
echo "  1. Open VS Code"
echo "  2. Go to Run and Debug (Ctrl+Shift+D)"
echo "  3. Select 'Attach to Docker' configuration"
echo "  4. Press F5"
echo ""
echo "To stop containers: docker-compose -f docker-compose.dev.yml down"
EOF

chmod +x docker-debug.sh

# Create system check script
cat > system-check.sh << 'EOF'
#!/bin/bash
echo "🔍 System Check for Express.js Debugging"
echo "========================================"

# Check Node.js
if command -v node &> /dev/null; then
    echo "✓ Node.js: $(node -v)"
else
    echo "✗ Node.js: Not installed"
fi

# Check npm
if command -v npm &> /dev/null; then
    echo "✓ npm: $(npm -v)"
else
    echo "✗ npm: Not installed"
fi

# Check VS Code
if command -v code &> /dev/null; then
    echo "✓ VS Code: Available"
else
    echo "✗ VS Code: Not installed"
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "✓ Docker: $(docker --version)"
else
    echo "✗ Docker: Not installed"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✓ Docker Compose: $(docker-compose --version)"
else
    echo "✗ Docker Compose: Not installed"
fi

# Check ports
echo ""
echo "Port availability:"
ports=(3000 9229 5432 6379)
for port in "${ports[@]}"; do
    if lsof -i :$port &> /dev/null; then
        echo "⚠ Port $port: In use"
    else
        echo "✓ Port $port: Available"
    fi
done

# Check memory
echo ""
echo "System Resources:"
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "CPU: $(nproc) cores"
echo "Disk: $(df -h . | tail -1 | awk '{print $4}') available"
EOF

chmod +x system-check.sh

print_status "Created debugging helper scripts:"
print_info "  ./debug.sh - Start app in debug mode"
print_info "  ./test.sh - Run tests"
print_info "  ./docker-debug.sh - Debug with Docker"
print_info "  ./system-check.sh - Check system requirements"

# System recommendations
print_info "System optimization recommendations for debugging:"

# Check available memory
MEMORY_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
MEMORY_GB=$((MEMORY_KB / 1024 / 1024))

if [ $MEMORY_GB -lt 4 ]; then
    print_warning "System has less than 4GB RAM. Consider increasing memory for better debugging performance."
fi

# Check Node.js version
NODE_MAJOR_VERSION=$(node -v | cut -d. -f1 | cut -dv -f2)
if [ $NODE_MAJOR_VERSION -lt 16 ]; then
    print_warning "Node.js version is older than 16. Consider upgrading for better debugging features."
fi

# Firewall recommendations
if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
    print_info "UFW firewall is active. You may need to allow debugging ports:"
    print_info "  sudo ufw allow 3000"
    print_info "  sudo ufw allow 9229"
fi

print_status "Setup complete!"
print_info ""
print_info "Quick start commands:"
print_info "  npm run dev          - Start with nodemon"
print_info "  npm run debug        - Start with inspector"
print_info "  npm test            - Run test suite"
print_info "  ./debug.sh          - Debug with environment variables"
print_info "  ./system-check.sh   - Check system status"
print_info ""
print_info "VS Code debugging:"
print_info "  1. Open this project in VS Code"
print_info "  2. Go to Run and Debug (Ctrl+Shift+D)"
print_info "  3. Select a debug configuration"
print_info "  4. Set breakpoints and press F5"
print_info ""
print_info "Chrome DevTools debugging:"
print_info "  1. Run: npm run debug"
print_info "  2. Open Chrome and go to chrome://inspect"
print_info "  3. Click 'Open dedicated DevTools for Node'"
print_info ""
print_info "Happy debugging! 🐛✨"
