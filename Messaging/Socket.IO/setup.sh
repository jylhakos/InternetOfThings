#!/bin/bash

# Weather Streaming Application Setup Script
# This script sets up the development environment

set -e

echo "🛠️  Weather Streaming Application Setup"
echo "====================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system dependencies
echo "📋 Checking system dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+"
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    echo "   Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm"
    exit 1
fi

if ! command_exists curl; then
    echo "❌ curl is not installed. Please install curl"
    echo "   Ubuntu/Debian: sudo apt install curl"
    exit 1
fi

echo " All system dependencies found"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python version $PYTHON_VERSION is too old. Please install Python 3.8+"
    exit 1
fi
echo " Python version $PYTHON_VERSION is compatible"

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version is too old. Please install Node.js 16+"
    exit 1
fi
echo " Node.js version $(node --version) is compatible"

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo " Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment and install backend dependencies
echo "📦 Installing backend dependencies..."
source venv/bin/activate
cd backend
pip install --upgrade pip
pip install -r requirements.txt
echo " Backend dependencies installed"
cd ..

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install
echo " Frontend dependencies installed"
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p logs/archive
echo " Directory structure created"

# Create .env file from template if it doesn't exist
echo "⚙️  Setting up configuration..."
if [ ! -f "backend/.env" ]; then
    cp backend/.env backend/.env.backup 2>/dev/null || true
    echo "📝 Please edit backend/.env with your configuration:"
    echo "   - Set your OpenWeatherMap API key"
    echo "   - Configure your database connection"
    echo "   - Set a secure JWT secret key"
else
    echo "ℹ️  Configuration file already exists"
fi

# Optional: PostgreSQL setup check
echo "🗄️  Database setup check..."
if command_exists psql; then
    echo " PostgreSQL client found"
    echo "ℹ️  To create the database:"
    echo "   sudo -u postgres createdb weatherdb"
    echo "   sudo -u postgres createuser username"
    echo "   sudo -u postgres psql -c \"ALTER USER username WITH PASSWORD 'password';\""
else
    echo "⚠️  PostgreSQL client not found. Install it for database operations:"
    echo "   Ubuntu/Debian: sudo apt install postgresql-client"
fi

# Docker setup check
if command_exists docker && command_exists docker-compose; then
    echo "🐳 Docker and Docker Compose found"
    echo "ℹ️  You can use Docker for easy deployment: docker-compose up -d"
else
    echo "ℹ️  Docker not found. Install for easy deployment:"
    echo "   Ubuntu/Debian: sudo apt install docker.io docker-compose"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Edit backend/.env with your configuration"
echo "2. Set up PostgreSQL database (or use Docker)"
echo "3. Get an OpenWeatherMap API key (optional, has fallback)"
echo "4. Run './start.sh' to start the application"
echo ""
echo "📚 Useful commands:"
echo "   Start app: ./start.sh"
echo "   Stop app: ./stop.sh"
echo "   View logs: tail -f logs/backend.log logs/frontend.log"
echo "   Docker: docker-compose up -d"
echo ""
echo "🌐 The application will be available at:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"

deactivate