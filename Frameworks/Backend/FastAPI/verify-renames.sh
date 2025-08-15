#!/bin/bash
# Verification script to check for any remaining old file name references

echo "🔍 Checking for old file name references..."
echo "=========================================="

# Check for old file names
echo "Searching for old file name references:"
echo ""

echo "1. DEVOPS_GRPC_GUIDE.md references:"
grep -r "DEVOPS_GRPC_GUIDE\.md" . --exclude-dir=venv 2>/dev/null || echo "   ✅ No references found"

echo ""
echo "2. GRPC_IMPLEMENTATION_SUMMARY.md references:"
grep -r "GRPC_IMPLEMENTATION_SUMMARY\.md" . --exclude-dir=venv 2>/dev/null || echo "   ✅ No references found"

echo ""
echo "3. GIT_GRPC_CONFIGURATION.md references:"
grep -r "GIT_GRPC_CONFIGURATION\.md" . --exclude-dir=venv 2>/dev/null || echo "   ✅ No references found"

echo ""
echo "📁 Current markdown files:"
ls -la *.md | grep -E "(DEVOPS|GRPC|GIT)\.md"

echo ""
echo "✅ File rename verification complete!"
