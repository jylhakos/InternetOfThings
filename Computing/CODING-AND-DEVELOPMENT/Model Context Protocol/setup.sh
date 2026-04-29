#!/bin/bash
# Quick setup script for the MCP project
# Run this script to set up the environment quickly

echo "================================================"
echo "  MCP Project Setup"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "================================================"
echo "  Next Steps:"
echo "================================================"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run an example MCP server:"
echo "   python src/server/mcp_server_stdio.py"
echo ""
echo "3. In another terminal, run the client:"
echo "   python src/client/mcp_client.py"
echo ""
echo "4. Or run the agent directly:"
echo "   python src/agent/simple_agent.py"
echo ""
echo "5. Test with MCP Inspector:"
echo "   npx @modelcontextprotocol/inspector python src/server/mcp_server_stdio.py"
echo ""
