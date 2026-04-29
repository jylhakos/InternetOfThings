#!/bin/bash

# LangChain.js AI Agent Installation Script

echo "🚀 Installing LangChain.js AI Agent Dependencies"
echo "==============================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_VERSION="18.0.0"

if ! node -p "require('semver').gte('$NODE_VERSION', '$REQUIRED_VERSION')" 2>/dev/null; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please upgrade to Node.js 18+."
    exit 1
fi

echo "✅ Node.js version: $(node -v)"
echo "✅ NPM version: $(npm -v)"

# Install dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Make sure Ollama is running with the required model:"
    echo "   ollama run llama3.1:8b-instruct-q4_0"
    echo ""
    echo "2. Start the LangChain.js AI Agent:"
    echo "   npm start"
    echo ""
    echo "3. Test the agent:"
    echo "   npm run test"
    echo ""
    echo "4. Or test manually:"
    echo "   curl -X POST http://localhost:8000/v1/chat/completions \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}'"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
