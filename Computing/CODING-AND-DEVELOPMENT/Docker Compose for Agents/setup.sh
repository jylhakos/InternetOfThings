#!/bin/bash
# Setup script for Compose for Agents project

set -e

echo "🚀 Setting up Compose for Agents..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12 or higher."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop or Docker Engine."
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose 2.38.1+."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install uv
echo "⚡ Installing uv package manager..."
pip install --upgrade pip
pip install uv

# Install dependencies
echo "📚 Installing project dependencies..."
uv sync

# Download Chinook database if not present
if [ ! -f "Chinook.db" ]; then
    echo "⬇️  Downloading Chinook database..."
    wget -q https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite -O Chinook.db
    echo "✅ Database downloaded"
else
    echo "✅ Chinook database already exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Start Docker services: docker compose up"
echo "  3. Open another terminal to view logs: docker compose logs -f agent"
echo ""
echo "To customize the question, edit the QUESTION variable in compose.yaml"
