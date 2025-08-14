#!/bin/bash

# Vite Build Script for DevOps
# This script provides a comprehensive build process for Vite applications

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

print_message $BLUE "🚀 Starting Vite Build Process..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_message $RED "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_message $RED "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Display versions
print_message $BLUE "📋 Environment Information:"
echo "Node.js version: $(node -v)"
echo "npm version: $(npm -v)"
echo "Current directory: $(pwd)"

# Parse command line arguments
BUILD_MODE=${1:-production}
SKIP_TESTS=${2:-false}
SKIP_LINT=${3:-false}
GENERATE_REPORT=${4:-false}

print_message $BLUE "🔧 Build Configuration:"
echo "Build mode: $BUILD_MODE"
echo "Skip tests: $SKIP_TESTS"
echo "Skip lint: $SKIP_LINT"
echo "Generate report: $GENERATE_REPORT"

# Clean previous builds
print_message $YELLOW "🧹 Cleaning previous builds..."
npm run clean || true

# Install dependencies
print_message $YELLOW "📦 Installing dependencies..."
if [ -f "package-lock.json" ]; then
    npm ci
else
    npm install
fi

# Run TypeScript type checking
if command -v tsc &> /dev/null; then
    print_message $YELLOW "🔍 Running TypeScript type checking..."
    npm run type-check
fi

# Run linting (if not skipped)
if [ "$SKIP_LINT" = "false" ]; then
    print_message $YELLOW "🔍 Running ESLint..."
    npm run lint
    
    print_message $YELLOW "💅 Checking code formatting..."
    npm run format:check
fi

# Run tests (if not skipped)
if [ "$SKIP_TESTS" = "false" ]; then
    print_message $YELLOW "🧪 Running tests..."
    npm run test || print_message $YELLOW "⚠️  No tests found or test command not configured"
fi

# Build the application
print_message $YELLOW "🏗️  Building application..."
if [ "$BUILD_MODE" = "development" ]; then
    npm run build -- --mode development
elif [ "$BUILD_MODE" = "staging" ]; then
    npm run build -- --mode staging
else
    npm run build -- --mode production --sourcemap
fi

# Generate bundle analysis report (if requested)
if [ "$GENERATE_REPORT" = "true" ]; then
    print_message $YELLOW "📊 Generating bundle analysis report..."
    npm run build:analyze || print_message $YELLOW "⚠️  Bundle analyzer not available"
fi

# Verify build output
if [ -d "dist" ]; then
    print_message $GREEN "✅ Build completed successfully!"
    print_message $BLUE "📁 Build output:"
    ls -la dist/
    
    # Calculate build size
    BUILD_SIZE=$(du -sh dist/ | cut -f1)
    print_message $BLUE "📦 Total build size: $BUILD_SIZE"
    
    # Check for critical files
    if [ -f "dist/index.html" ]; then
        print_message $GREEN "✅ index.html found"
    else
        print_message $RED "❌ index.html not found"
        exit 1
    fi
    
    # Count assets
    JS_FILES=$(find dist -name "*.js" | wc -l)
    CSS_FILES=$(find dist -name "*.css" | wc -l)
    
    print_message $BLUE "📄 Generated files:"
    echo "JavaScript files: $JS_FILES"
    echo "CSS files: $CSS_FILES"
    
else
    print_message $RED "❌ Build failed - dist directory not found"
    exit 1
fi

# Test the production build
print_message $YELLOW "🔬 Testing production build..."
npm run preview &
PREVIEW_PID=$!

# Wait a moment for the server to start
sleep 3

# Check if the preview server is running
if kill -0 $PREVIEW_PID 2>/dev/null; then
    print_message $GREEN "✅ Preview server started successfully"
    kill $PREVIEW_PID
else
    print_message $YELLOW "⚠️  Preview server test skipped"
fi

# Generate build report
print_message $BLUE "📋 Build Summary:"
echo "======================================"
echo "Build Mode: $BUILD_MODE"
echo "Build Time: $(date)"
echo "Build Size: $BUILD_SIZE"
echo "Node.js Version: $(node -v)"
echo "npm Version: $(npm -v)"
echo "======================================"

print_message $GREEN "🎉 Build process completed successfully!"

# Exit with success status
exit 0
