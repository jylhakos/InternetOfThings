#!/bin/bash

# Complete Demo Script for Vite + React + ASP.NET Core Guide
# This script demonstrates the entire workflow from setup to deployment

echo "🌟 Complete Vite + React + ASP.NET Core Demonstration"
echo "====================================================="

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}🔹 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local all_good=true
    
    # Check .NET
    if command -v dotnet &> /dev/null; then
        DOTNET_VER=$(dotnet --version)
        print_success ".NET SDK: $DOTNET_VER"
    else
        print_warning ".NET SDK not found"
        all_good=false
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VER=$(node --version)
        print_success "Node.js: $NODE_VER"
    else
        print_warning "Node.js not found"
        all_good=false
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VER=$(npm --version)
        print_success "npm: $NPM_VER"
    else
        print_warning "npm not found"
        all_good=false
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        DOCKER_VER=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker: $DOCKER_VER"
    else
        print_info "Docker not found (optional for containerization)"
    fi
    
    echo ""
    if [ "$all_good" = true ]; then
        print_success "All prerequisites are met!"
    else
        print_warning "Some prerequisites are missing. Please install them before continuing."
        echo ""
        echo "Installation commands for Debian/Ubuntu:"
        echo "  .NET SDK: wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb && sudo dpkg -i packages-microsoft-prod.deb && sudo apt update && sudo apt install dotnet-sdk-8.0"
        echo "  Node.js:  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
        echo "  Docker:   sudo apt install docker.io docker-compose"
        return 1
    fi
    
    return 0
}

# Show project structure
show_project_structure() {
    print_header "Project Structure Overview"
    
    echo "📁 Complete Vite + React + ASP.NET Core Project Structure:"
    echo ""
    echo "examples/ViteReactASP/"
    echo "├── 🚀 setup-vite-project.sh       # Automated project creation"
    echo "├── 🔧 dev-workflow.sh             # Development automation"
    echo "├── 🐳 Dockerfile                  # Production container"
    echo "├── 🐳 docker-compose.yml          # Multi-service orchestration"
    echo "├── 🔨 docker-compose.dev.yml      # Development overrides"
    echo "├── Server/                        # ASP.NET Core Backend"
    echo "│   ├── Program.cs                 # 🎛️  Enhanced configuration"
    echo "│   └── Controllers/               # 🔌 API endpoints"
    echo "└── Client/                        # React Frontend with Vite"
    echo "    ├── package.json               # 📦 Dependencies"
    echo "    ├── vite.config.ts             # ⚡ Vite configuration"
    echo "    ├── src/"
    echo "    │   ├── App.tsx                # ⚛️  Main React component"
    echo "    │   └── App.css                # 🎨 Styling"
    echo "    └── index.html                 # 🌐 Entry point"
    echo ""
}

# Demonstrate key features
demonstrate_features() {
    print_header "Key Features Demonstrated"
    
    echo "🚀 Development Speed & Experience:"
    echo "   • Lightning-fast Hot Module Replacement (HMR)"
    echo "   • Instant feedback on code changes"
    echo "   • Native TypeScript support"
    echo "   • Automatic dependency optimization"
    echo ""
    
    echo "🔗 Seamless Integration:"
    echo "   • Vite proxy configuration for API calls"
    echo "   • CORS setup for development"
    echo "   • Environment-specific configurations"
    echo "   • Shared error handling patterns"
    echo ""
    
    echo "📦 Production Optimization:"
    echo "   • Code splitting and tree shaking"
    echo "   • Asset optimization and caching"
    echo "   • Minification and compression"
    echo "   • Docker multi-stage builds"
    echo ""
    
    echo "🛠️ Developer Tools:"
    echo "   • VS Code debugging setup"
    echo "   • Automated workflow scripts"
    echo "   • Health check endpoints"
    echo "   • Comprehensive error handling"
    echo ""
}

# Show available commands
show_commands() {
    print_header "Available Commands & Workflows"
    
    echo "1️⃣  Project Setup:"
    echo "   ./examples/ViteReactASP/setup-vite-project.sh"
    echo ""
    
    echo "2️⃣  Development Workflow:"
    echo "   cd ViteReactASP"
    echo "   ./dev-workflow.sh dev              # Start dev environment"
    echo "   ./dev-workflow.sh build            # Build for production"
    echo "   ./dev-workflow.sh test             # Test endpoints"
    echo ""
    
    echo "3️⃣  Manual Commands:"
    echo "   # Backend:"
    echo "   cd Server && dotnet run"
    echo "   "
    echo "   # Frontend:"
    echo "   cd Client && npm run dev"
    echo ""
    
    echo "4️⃣  Docker Deployment:"
    echo "   docker-compose up --build          # Production mode"
    echo "   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up  # Dev mode"
    echo ""
    
    echo "5️⃣  Access Points:"
    echo "   🌐 Frontend:    http://localhost:5173"
    echo "   🔌 Backend API: https://localhost:7042"
    echo "   📚 Swagger UI:  https://localhost:7042/swagger"
    echo "   ❤️  Health:     https://localhost:7042/health"
    echo ""
}

# Show performance comparison
show_performance() {
    print_header "Performance Benefits"
    
    echo "⚡ Vite vs Traditional Bundlers:"
    echo "   • Development startup: 40-100x faster"
    echo "   • Hot reload speed: < 50ms (vs 2-5 seconds)"
    echo "   • Build time: 60-80% faster"
    echo "   • Bundle size: 20-40% smaller (with tree shaking)"
    echo ""
    
    echo "🎯 Real-world Impact:"
    echo "   • Faster developer feedback loop"
    echo "   • Improved developer experience"
    echo "   • Reduced build server costs"
    echo "   • Better user experience with smaller bundles"
    echo ""
}

# Show technology stack
show_tech_stack() {
    print_header "Complete Technology Stack"
    
    echo "🎯 Frontend Stack:"
    echo "   • React 18 with TypeScript"
    echo "   • Vite 5 (build tool)"
    echo "   • ES Modules & Tree Shaking"
    echo "   • Hot Module Replacement (HMR)"
    echo ""
    
    echo "🏗️  Backend Stack:"
    echo "   • ASP.NET Core 8"
    echo "   • Web API with Swagger"
    echo "   • CORS configuration"
    echo "   • Health checks"
    echo ""
    
    echo "🔧 Development Tools:"
    echo "   • VS Code integration"
    echo "   • TypeScript support"
    echo "   • ESLint configuration"
    echo "   • Debugging setup"
    echo ""
    
    echo "🐳 Deployment:"
    echo "   • Docker containerization"
    echo "   • Multi-stage builds"
    echo "   • Docker Compose orchestration"
    echo "   • Production optimizations"
    echo ""
}

# Interactive menu
show_menu() {
    echo ""
    echo "📋 Choose what you'd like to explore:"
    echo "1) 🔍 Check Prerequisites"
    echo "2) 📁 Show Project Structure"
    echo "3) 🚀 Demonstrate Key Features"
    echo "4) 🛠️  Show Commands & Workflows"
    echo "5) ⚡ Performance Benefits"
    echo "6) 🎯 Technology Stack"
    echo "7) 📖 Open README.md Guide"
    echo "8) 🎬 Run Complete Demo"
    echo "9) ❌ Exit"
    echo ""
}

# Open README
open_readme() {
    print_header "Opening README.md Guide"
    
    README_PATH="/home/laptop/EXERCISES/IOT/InternetOfThings/Frameworks/Backend/ASP.NET /README.md"
    
    if command -v code &> /dev/null; then
        code "$README_PATH"
        print_success "README.md opened in VS Code"
    elif command -v gedit &> /dev/null; then
        gedit "$README_PATH" &
        print_success "README.md opened in gedit"
    elif command -v nano &> /dev/null; then
        nano "$README_PATH"
        print_success "README.md opened in nano"
    else
        print_info "README.md location: $README_PATH"
        print_info "Please open it with your preferred text editor"
    fi
}

# Run complete demo
run_complete_demo() {
    print_header "Running Complete Demonstration"
    
    check_prerequisites
    if [ $? -ne 0 ]; then
        print_warning "Prerequisites check failed. Please install missing dependencies."
        return 1
    fi
    
    echo ""
    show_project_structure
    echo ""
    demonstrate_features
    echo ""
    show_commands
    echo ""
    show_performance
    echo ""
    show_tech_stack
    
    echo ""
    print_header "🎉 Demo Complete!"
    print_info "You're ready to start developing with Vite + React + ASP.NET Core!"
    echo ""
    print_info "Next Steps:"
    echo "1. Run the setup script: ./examples/ViteReactASP/setup-vite-project.sh"
    echo "2. Follow the README.md guide for detailed instructions"
    echo "3. Start coding your amazing full-stack application!"
}

# Main menu loop
main() {
    echo ""
    print_info "This demonstration showcases modern full-stack development with:"
    echo "  ⚛️  React 18 + TypeScript"
    echo "  ⚡ Vite 5 (Lightning-fast build tool)"
    echo "  🏗️  ASP.NET Core 8"
    echo "  🐳 Docker containerization"
    
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Enter your choice (1-9): " choice
            
            case $choice in
                1) check_prerequisites ;;
                2) show_project_structure ;;
                3) demonstrate_features ;;
                4) show_commands ;;
                5) show_performance ;;
                6) show_tech_stack ;;
                7) open_readme ;;
                8) run_complete_demo ;;
                9) 
                    print_info "Thank you for exploring Vite + React + ASP.NET Core!"
                    print_info "Happy coding! 🚀"
                    exit 0
                    ;;
                *)
                    print_warning "Invalid option. Please choose 1-9."
                    ;;
            esac
            
            echo ""
            read -p "Press Enter to continue..."
        done
    else
        # Command line mode
        case $1 in
            "demo"|"full")
                run_complete_demo
                ;;
            "check"|"prereq")
                check_prerequisites
                ;;
            "structure")
                show_project_structure
                ;;
            "features")
                demonstrate_features
                ;;
            "commands")
                show_commands
                ;;
            "performance"|"perf")
                show_performance
                ;;
            "stack"|"tech")
                show_tech_stack
                ;;
            "readme")
                open_readme
                ;;
            *)
                print_warning "Unknown command: $1"
                echo "Available commands: demo, check, structure, features, commands, performance, stack, readme"
                ;;
        esac
    fi
}

# Run the main function
main "$@"
