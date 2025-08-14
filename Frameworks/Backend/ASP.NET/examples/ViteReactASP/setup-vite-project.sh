#!/bin/bash

# Setup Script for Vite + React + ASP.NET Core Project
# This script demonstrates the complete setup process

echo "🚀 Setting up Vite + React + ASP.NET Core Project"
echo "=================================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check .NET SDK
if command -v dotnet &> /dev/null; then
    DOTNET_VERSION=$(dotnet --version)
    echo "✅ .NET SDK found: $DOTNET_VERSION"
else
    echo "❌ .NET SDK not found. Please install .NET 8.0 SDK"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js found: $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js LTS"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm found: $NPM_VERSION"
else
    echo "❌ npm not found. Please install npm"
    exit 1
fi

echo ""
echo "🏗️  Creating project structure..."

# Create project directory
PROJECT_NAME="ViteReactASP"
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

echo "📂 Created project directory: $PROJECT_NAME"

# Create ASP.NET Core Web API project
echo "🔧 Creating ASP.NET Core Web API..."
dotnet new webapi -n $PROJECT_NAME.Server -o Server
cd Server

# Add CORS package
echo "📦 Adding CORS support..."
dotnet add package Microsoft.AspNetCore.Cors

cd ..

# Create React project with Vite
echo "⚛️  Creating React project with Vite..."
npm create vite@latest Client -- --template react-ts
cd Client

# Install additional dependencies
echo "📦 Installing React dependencies..."
npm install
npm install -D @types/node

cd ..

# Create solution file
echo "📋 Creating solution file..."
dotnet new sln -n $PROJECT_NAME
dotnet sln add Server/$PROJECT_NAME.Server.csproj

echo ""
echo "✅ Project structure created successfully!"
echo ""
echo "📁 Project Structure:"
echo "├── $PROJECT_NAME.sln"
echo "├── Server/"
echo "│   ├── Controllers/"
echo "│   ├── Program.cs"
echo "│   └── $PROJECT_NAME.Server.csproj"
echo "└── Client/"
echo "    ├── src/"
echo "    ├── package.json"
echo "    ├── vite.config.ts"
echo "    └── index.html"
echo ""
echo "🚀 Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Configure the backend (Server/Program.cs)"
echo "3. Configure Vite proxy (Client/vite.config.ts)"
echo "4. Run: dotnet run --project Server (Terminal 1)"
echo "5. Run: cd Client && npm run dev (Terminal 2)"
echo ""
echo "🌐 Default URLs:"
echo "- Backend API: https://localhost:7042"
echo "- Frontend Dev: http://localhost:5173"
