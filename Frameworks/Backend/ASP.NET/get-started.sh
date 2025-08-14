#!/bin/bash

echo "=================================================="
echo "ASP.NET Core Development Environment Setup"
echo "=================================================="
echo ""

echo "1. Installing .NET SDK 8.0..."
echo "   wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb"
echo "   sudo dpkg -i packages-microsoft-prod.deb"
echo "   rm packages-microsoft-prod.deb"
echo "   sudo apt update"
echo "   sudo apt install -y apt-transport-https dotnet-sdk-8.0"
echo ""

echo "2. Installing Node.js for React development..."
echo "   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -"
echo "   sudo apt-get install -y nodejs"
echo ""

echo "3. Installing VS Code..."
echo "   wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg"
echo "   sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/"
echo "   sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'"
echo "   sudo apt update"
echo "   sudo apt install code"
echo ""

echo "4. Installing VS Code Extensions..."
echo "   code --install-extension ms-dotnettools.csharp"
echo "   code --install-extension ms-dotnettools.csdevkit"
echo "   code --install-extension ms-dotnettools.vscodeintellicode-csharp"
echo "   code --install-extension dsznajder.es7-react-js-snippets"
echo ""

echo "5. Testing the gRPC Service..."
echo "   cd gRPC/GrpcGreeterService"
echo "   dotnet run"
echo ""

echo "6. Creating a React + ASP.NET Core Project..."
echo "   dotnet new react -n MyReactApp"
echo "   cd MyReactApp"
echo "   dotnet run --project MyReactApp.Server"
echo ""

echo "7. Using Docker Compose for complete setup..."
echo "   docker-compose up --build"
echo ""

echo "=================================================="
echo "For detailed instructions, see README.md"
echo "=================================================="
