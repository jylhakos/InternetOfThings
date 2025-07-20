#!/bin/bash

# Setup script for AI Agent with Llama 4 Scout support
# This script installs Ollama, pulls Llama 4 models, and sets up the Python environment

set -e

echo "🚀 Setting up AI Agent with Llama 4 Scout support..."

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  This script is designed for Linux systems"
    echo "Please adapt the commands for your operating system"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
echo "🔍 Checking system requirements..."

# Check Python version
if command_exists python3; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "✅ Python version: $PYTHON_VERSION"
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        echo "✅ Python version is compatible"
    else
        echo "❌ Python 3.8+ required"
        exit 1
    fi
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check available memory
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
echo "💾 Available RAM: ${TOTAL_MEM}GB"
if [ "$TOTAL_MEM" -lt 32 ]; then
    echo "⚠️  Warning: Less than 32GB RAM available. Consider using quantized models or cloud resources."
fi

# Install Ollama if not exists
echo "🦙 Installing Ollama..."
if ! command_exists ollama; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installed"
else
    echo "✅ Ollama already installed"
fi

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

# Activate virtual environment and install dependencies
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip

# Install core dependencies
pip install \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    httpx==0.25.2 \
    python-dotenv==1.0.0 \
    pydantic==2.5.0

echo "✅ Python dependencies installed"

# Create environment files
echo "⚙️  Creating environment configuration..."

# Create .env file for AI Agent
cat > .env << EOF
# AI Agent Configuration
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama4:scout
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Fallback model if Llama 4 Scout is not available
FALLBACK_MODEL=llama3.1:8b-instruct-q4_0
EOF

# Create .env.docker for Open WebUI (if needed)
cat > .env.docker << EOF
# Open WebUI Configuration
WEBUI_PORT=3000
OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1
DEFAULT_MODELS=ai-agent-llama4-scout
ENABLE_SIGNUP=false
EOF

echo "✅ Environment files created"

# Start Ollama service
echo "🦙 Starting Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
    sleep 3
    echo "✅ Ollama service started"
else
    echo "✅ Ollama service already running"
fi

# Pull Llama 4 Scout model
echo "📥 Pulling Llama 4 Scout model..."
echo "This may take several minutes depending on your internet connection..."

if ollama list | grep -q "llama4:scout"; then
    echo "✅ Llama 4 Scout already available"
else
    echo "Downloading Llama 4 Scout (this may take 10-30 minutes)..."
    if ollama pull llama4:scout; then
        echo "✅ Llama 4 Scout downloaded successfully"
    else
        echo "⚠️  Failed to download Llama 4 Scout. Trying alternative..."
        
        # Try quantized version
        if ollama pull ingu627/llama4-scout-q4; then
            echo "✅ Llama 4 Scout (quantized) downloaded successfully"
            # Update .env to use quantized model
            sed -i 's/MODEL_NAME=llama4:scout/MODEL_NAME=ingu627\/llama4-scout-q4/' .env
        else
            echo "⚠️  Failed to download Llama 4. Installing fallback model..."
            ollama pull llama3.1:8b-instruct-q4_0
            sed -i 's/MODEL_NAME=llama4:scout/MODEL_NAME=llama3.1:8b-instruct-q4_0/' .env
            echo "✅ Fallback model installed"
        fi
    fi
fi

# Test Ollama connection
echo "🧪 Testing Ollama connection..."
MODEL_NAME=$(grep "MODEL_NAME=" .env | cut -d'=' -f2)
if ollama run "$MODEL_NAME" "Hello, respond with just 'OK' to test connection" 2>/dev/null | grep -q "OK"; then
    echo "✅ Ollama connection successful"
else
    echo "⚠️  Ollama connection test failed, but installation continues"
fi

# Test Python components
echo "🧪 Testing Python components..."
python3 -c "
import asyncio
import sys
sys.path.append('src')

async def test():
    try:
        from tools import WeatherTool
        weather = WeatherTool()
        result = await weather.get_coordinates('London')
        print('✅ Weather tool test passed')
        return True
    except Exception as e:
        print(f'⚠️ Weather tool test failed: {e}')
        return False

if asyncio.run(test()):
    print('✅ Python components working')
else:
    print('⚠️ Some Python components may need attention')
"

# Make scripts executable
chmod +x *.sh

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Start the AI Agent:"
echo "   ./start-simple.sh"
echo ""
echo "2. Or start the full stack with web interface:"
echo "   make full-stack"
echo ""
echo "3. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "4. Access the web interface (if using full stack):"
echo "   http://localhost:3000"
echo ""
echo "Available models:"
ollama list
echo ""
echo "Environment:"
echo "- Ollama: http://localhost:11434"
echo "- AI Agent API: http://localhost:8000"
echo "- Web Interface: http://localhost:3000 (when started)"
echo ""

# Final instructions
if grep -q "llama4" .env; then
    echo "🌟 Llama 4 Scout Features:"
    echo "- 10M token context window"
    echo "- Advanced tool calling"
    echo "- Mixture of Experts architecture"
    echo "- Enhanced reasoning capabilities"
else
    echo "📝 Note: Using fallback model. To upgrade later:"
    echo "   ollama pull llama4:scout"
    echo "   # Then update .env file"
fi

echo ""
echo "Happy coding with your AI Agent! 🤖"
