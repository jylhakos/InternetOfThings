# Model Context Protocol (MCP) Project

## Description

A complete Python implementation demonstrating how to build AI agents using the Model Context Protocol (MCP). This project includes example MCP servers, clients, and agents that can interact with external tools and data sources.

## Features

-   MCP Server implementations (STDIO and SSE transports)
-   MCP Client for connecting to servers
-   Simple AI Agent with MCP integration
-   OpenAI integration example
-   FastMCP examples for rapid development
-   Testing suite
-   Complete documentation and tutorials

## Project Structure

```
.
├── src/
│   ├── server/          # MCP server implementations
│   ├── client/          # MCP client implementations
│   └── agent/           # AI agent implementations
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
├── setup.sh            # Quick setup script
├── .gitignore          # Git ignore rules
└── README.md           # Full documentation
```

## Quick Start

1. **Set up environment:**
   ```bash
   ./setup.sh
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Run an example:**
   ```bash
   python src/agent/simple_agent.py
   ```

## Documentation

See [README.md](README.md) for complete documentation including:
- MCP architecture and concepts
- Setup tutorials
- Testing strategies
- API references

## Requirements

- Python 3.8+
- pip
- Virtual environment support

## Resources

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Documentation](https://docs.anthropic.com/en/docs/mcp)
- [OpenAI API](https://developers.openai.com/api/reference/overview)
