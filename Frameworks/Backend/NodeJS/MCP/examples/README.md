# MCP

This directory contains code demonstrating how to interact with the MCP server.

## Examples

### 1. Simple JavaScript Client (`simple-client.js`)

A basic Node.js client that demonstrates:
- Connecting to the MCP server
- Listing available tools
- Calling tools (system info, text generation, model listing)

**Usage:**
```bash
# Make sure the project is built first
npm run build

# Run the example
node examples/simple-client.js
```

### 2. Python Client (`python-client.py`)

A Python client that shows how to:
- Communicate with the MCP server via subprocess
- Handle JSON-RPC messaging
- Call tools from Python applications

**Usage:**
```bash
# Make sure the project is built first
npm run build

# Run the Python example
python3 examples/python-client.py
```

## Integrations

### Web Applications

You can integrate the MCP server with web applications:

```javascript
// Express.js integration example
const express = require('express');
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

const app = express();
app.use(express.json());

let mcpClient;

// Initialize MCP client
async function initializeMCP() {
  mcpClient = new Client({
    name: 'web-app-client',
    version: '1.0.0',
  }, { capabilities: { sampling: {} } });
  
  const transport = new StdioClientTransport({
    command: 'node',
    args: ['./dist/server/index.js']
  });
  
  await mcpClient.connect(transport);
}

// API endpoint using MCP
app.post('/api/generate', async (req, res) => {
  try {
    const { prompt, temperature = 0.7 } = req.body;
    
    const response = await mcpClient.request({
      method: 'tools/call',
      params: {
        name: 'llama_generate',
        arguments: { prompt, temperature }
      }
    });
    
    res.json({ text: response.content[0].text });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

initializeMCP().then(() => {
  app.listen(3000, () => console.log('Web app running on port 3000'));
});
```

### Command Line Tools

Create custom CLI tools using the MCP server:

```bash
#!/bin/bash
# mcp-cli.sh - Simple CLI wrapper

case "$1" in
  "generate")
    echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"llama_generate","arguments":{"prompt":"'"$2"'"}}}' | node dist/server/index.js | jq -r '.result.content[0].text'
    ;;
  "chat")
    echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"llama_chat","arguments":{"messages":[{"role":"user","content":"'"$2"'"}]}}}' | node dist/server/index.js | jq -r '.result.content[0].text'
    ;;
  *)
    echo "Usage: $0 {generate|chat} \"your prompt\""
    ;;
esac
```

### Docker

Run examples in Docker:

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY . .
RUN npm install && npm run build

# Run example
CMD ["node", "examples/simple-client.js"]
```

## Testing Tools

These examples can also serve as integration tests:

```bash
# Test all tools
npm test

# Run specific example tests
npm run test:examples
```