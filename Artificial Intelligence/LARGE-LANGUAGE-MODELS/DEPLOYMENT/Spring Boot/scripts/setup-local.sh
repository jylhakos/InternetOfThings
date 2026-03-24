#!/bin/bash

# Local development setup script for LLM Chat Service
# This script sets up the local environment for development

set -e

echo "🚀 Setting up LLM Chat Service Local Development Environment"

# Check if required tools are installed
command -v java >/dev/null 2>&1 || { echo "❌ Java is required but not installed. Aborting." >&2; exit 1; }
command -v mvn >/dev/null 2>&1 || { echo "❌ Maven is required but not installed. Aborting." >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "❌ curl is required but not installed. Aborting." >&2; exit 1; }

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 17 ]; then
    echo "❌ Java 17 or higher is required. Current version: $JAVA_VERSION"
    exit 1
fi

echo "✅ Java $JAVA_VERSION detected"

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service
echo "🔄 Starting Ollama service..."
sudo systemctl start ollama || {
    echo "⚠️  Could not start Ollama as service, trying direct start..."
    ollama serve &
    OLLAMA_PID=$!
    echo "Ollama started with PID: $OLLAMA_PID"
    sleep 5
}

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/version > /dev/null; then
        echo "✅ Ollama is ready"
        break
    fi
    sleep 2
    if [ $i -eq 30 ]; then
        echo "❌ Ollama failed to start after 60 seconds"
        exit 1
    fi
done

# Pull Llama-3 model
echo "📥 Pulling Llama-3 model (this may take a while)..."
ollama pull llama3 || {
    echo "❌ Failed to pull Llama-3 model"
    exit 1
}

echo "✅ Llama-3 model is ready"

# Build the Spring Boot application
echo "🔨 Building Spring Boot application..."
mvn clean compile

echo "✅ Application built successfully"

# Create run script
cat > run-local.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting LLM Chat Service locally..."

# Start Ollama if not running
if ! curl -s http://localhost:11434/api/version > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Run Spring Boot application
mvn spring-boot:run
EOF

chmod +x run-local.sh

echo "✅ Local setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run './run-local.sh' to start the application"
echo "2. Open http://localhost:8080 in your browser"
echo "3. Use the chat interface to interact with Llama-3"
echo ""
echo "📚 API Endpoints:"
echo "- POST /api/v1/chat - Send chat messages"
echo "- GET /api/v1/chat/health - Health check"
echo "- GET /api/v1/chat/info - Service information"
