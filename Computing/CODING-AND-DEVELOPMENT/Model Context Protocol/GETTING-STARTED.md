# Getting Started with MCP

## Quick Start Guide

This guide will help you get up and running with the Model Context Protocol (MCP) project in just a few minutes.

### Step 1: Environment Setup

**IMPORTANT**: Always use the virtual environment!

```bash
# Activate the virtual environment
source venv/bin/activate

# You should see (venv) in your terminal prompt
# Example: (venv) user@computer:~/project$
```

To verify your virtual environment is active:

```bash
which python
# Should show: /path/to/your/project/venv/bin/python
```

### Step 2: Verify Installation

Check that all packages are installed:

```bash
pip list | grep -E "(mcp|fastmcp|anthropic|openai)"
```

If packages are missing, install them:

```bash
pip install -r requirements.txt
```

### Step 3: Run Your First MCP Server

Open a terminal with venv active and run:

```bash
python src/server/mcp_server_stdio.py
```

The server will start and wait for client connections via STDIO.

### Step 4: Run the MCP Client (in another terminal)

Open a NEW terminal, activate venv, then run:

```bash
source venv/bin/activate
python src/client/mcp_client.py
```

You should see output showing:
- Connection to MCP server
- Available tools listed
- Tool execution result

### Step 5: Run the Simple Agent

The agent demonstrates how an AI assistant uses MCP:

```bash
source venv/bin/activate
python src/agent/simple_agent.py
```

## Examples by Use Case

### Use Case 1: Weather Data Access

**Server**: Exposes weather tools
```bash
python src/server/mcp_server_stdio.py
```

**Client**: Queries weather information
```bash
python src/client/mcp_client.py
```

### Use Case 2: FastMCP (Rapid Development)

For quick prototyping:

```bash
python src/server/fastmcp_server.py
```

### Use Case 3: SSE Transport (HTTP-based)

For remote server deployments:

```bash
# Terminal 1: Start SSE server
python src/server/mcp_server_sse.py

# Server will run on http://localhost:8000
# Connect to: http://localhost:8000/sse
```

### Use Case 4: OpenAI Integration

See `src/agent/openai_agent.py` for how to integrate OpenAI with MCP.

**Note**: Requires `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY="your-api-key-here"
python src/agent/openai_agent.py
```

## Common Commands

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_mcp.py::test_server_tool_discovery -v

# Run with coverage
pip install pytest-cov
pytest --cov=src tests/
```

### Using MCP Inspector

The MCP Inspector is a visual debugging tool:

```bash
# Install (requires Node.js)
npm install -g @modelcontextprotocol/inspector

# Or use npx (no install needed)
npx @modelcontextprotocol/inspector python src/server/mcp_server_stdio.py
```

This opens a web interface where you can:
- See all available tools
- Test tool invocations
- Debug request/response data

### Checking Virtual Environment Status

Always verify venv is active before running Python commands:

```bash
# Check Python path
which python
# Should output: .../venv/bin/python

# Check pip path
which pip
# Should output: .../venv/bin/pip

# View environment variable
echo $VIRTUAL_ENV
# Should output: /path/to/your/project/venv
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'mcp'"

**Solution**: Virtual environment is not active or packages not installed.

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Server exits immediately

**Solution**: STDIO servers wait for client connections. They exit when the client disconnects. This is normal behavior.

### Problem: "Connection refused" with SSE server

**Solution**: Make sure the SSE server is running before trying to connect.

```bash
# Check if server is running
curl http://localhost:8000/sse
```

### Problem: Import errors

**Solution**: Make sure you're running from the project root directory.

```bash
# Check current directory
pwd
# Should be: /path/to/Model Context Protocol

# If not, cd to project root
cd "path/to/Model Context Protocol"
```

## Project Structure Explanation

```
Model Context Protocol/
│
├── venv/                          # Virtual environment (DO NOT COMMIT)
│
├── src/                           # Source code
│   ├── server/                    # MCP servers
│   │   ├── mcp_server_stdio.py   # STDIO transport server
│   │   ├── mcp_server_sse.py     # SSE transport server
│   │   └── fastmcp_server.py     # FastMCP server
│   │
│   ├── client/                    # MCP clients
│   │   └── mcp_client.py         # Basic client implementation
│   │
│   └── agent/                     # AI agents
│       ├── simple_agent.py       # Basic agent
│       └── openai_agent.py       # OpenAI integration
│
├── tests/                         # Test suite
│   └── test_mcp.py               # MCP tests
│
├── requirements.txt               # Python dependencies
├── setup.sh                       # Setup script
├── .gitignore                    # Git ignore rules
├── .env.example                  # Environment variables template
├── PROJECT.md                    # Project overview
├── GETTING-STARTED.md            # This file
└── README.md                     # Complete documentation
```

## Next Steps

1.  Set up virtual environment
2.  Install dependencies
3.  Run example server and client
4.  Read [README.md](README.md) for complete documentation
5.  Explore the test suite in `tests/`
6.  Modify examples to experiment
7.  Build your own MCP server!

## Learning Path

1. **Beginner**: Run the examples, understand the flow
2. **Intermediate**: Modify servers to add new tools, change behavior
3. **Advanced**: Integrate with real APIs, build production agents
4. **Expert**: Create custom transport layers, optimize performance

## Resources

- **Full Documentation**: See [README.md](README.md)
- **MCP Official Site**: https://modelcontextprotocol.io/
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk

## Getting Help

- Check the [README.md](README.md) for detailed explanations
- Review code comments in source files
- Use MCP Inspector to debug
- Test with the provided test suite

---

**Remember**: Always activate your virtual environment before running any Python commands!

```bash
source venv/bin/activate
```
