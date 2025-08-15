#!/bin/bash
# Pre-commit hook to prevent committing generated gRPC files
# 
# Installation:
# cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
# chmod +x .git/hooks/pre-commit

echo "🔍 Checking for generated gRPC files in commit..."

# Check if any generated files are staged for commit
GENERATED_FILES=$(git diff --cached --name-only | grep -E "_pb2\.py$|_pb2_grpc\.py$" || true)

if [[ -n "$GENERATED_FILES" ]]; then
    echo ""
    echo "❌ ERROR: Generated gRPC files should not be committed!"
    echo ""
    echo "The following generated files were found in your commit:"
    echo "$GENERATED_FILES" | sed 's/^/  - /'
    echo ""
    echo "These files are automatically generated during the build process."
    echo ""
    echo "To fix this issue:"
    echo "  1. Remove the files from staging:"
    echo "     git reset HEAD protos/*_pb2*.py"
    echo ""
    echo "  2. Ensure .gitignore contains:"
    echo "     *_pb2.py"
    echo "     *_pb2_grpc.py"
    echo ""
    echo "  3. The files will be generated automatically during:"
    echo "     - Local development: ./generate_grpc.sh"
    echo "     - CI/CD builds: Jenkins/GitHub Actions"
    echo "     - Docker builds: Multi-stage Dockerfile"
    echo ""
    echo "Only commit the source .proto files and generation scripts."
    echo ""
    exit 1
fi

# Check if proto files are being committed without the generation script
PROTO_FILES=$(git diff --cached --name-only | grep "\.proto$" || true)
GENERATION_SCRIPT=$(git diff --cached --name-only | grep "generate_grpc.sh" || true)

if [[ -n "$PROTO_FILES" && -z "$GENERATION_SCRIPT" ]]; then
    if [[ ! -f "generate_grpc.sh" ]]; then
        echo ""
        echo "⚠️  WARNING: Proto files are being committed but generate_grpc.sh is missing!"
        echo ""
        echo "Proto files found in commit:"
        echo "$PROTO_FILES" | sed 's/^/  - /'
        echo ""
        echo "Please ensure generate_grpc.sh is available for DevOps builds."
        echo ""
    fi
fi

echo "✅ No generated gRPC files found in commit."

# Optional: Check for other common issues
echo "🔍 Running additional checks..."

# Check for merge conflict markers
CONFLICT_MARKERS=$(git diff --cached | grep -E "^(\+.*)?(<<<<<<<|=======|>>>>>>>)" || true)
if [[ -n "$CONFLICT_MARKERS" ]]; then
    echo "❌ ERROR: Merge conflict markers found in staged files!"
    echo "Please resolve all conflicts before committing."
    exit 1
fi

# Check for debug statements (optional)
DEBUG_STATEMENTS=$(git diff --cached --name-only -z | xargs -0 grep -l "print(\|console\.log(\|debugger\|pdb\.set_trace" 2>/dev/null || true)
if [[ -n "$DEBUG_STATEMENTS" ]]; then
    echo "⚠️  WARNING: Debug statements found in:"
    echo "$DEBUG_STATEMENTS" | sed 's/^/  - /'
    echo "Consider removing debug code before committing."
fi

echo "✅ Pre-commit checks passed!"
echo ""
