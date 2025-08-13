# MCP Implementation

The project creates a MCP server/client.

## **Data Flow**

### **Request Flow:**
1. **Client** sends JSON-RPC request: `{"method": "tools/call", "params": {"name": "llama_generate", "arguments": {"prompt": "Hello"}}}`
2. **MCP Server** validates request, applies prompt template: `"System: You are helpful\nUser: Hello"`
3. **Server** calls Ollama API: `POST /api/generate {"model": "llama3.2:3b", "prompt": "..."}`
4. **Ollama** loads Llama model and runs inference (tokenization → neural network → generation)
5. **Llama Model** generates response: `"Hello! How can I help you?"`
6. **Server** formats response and returns to client as JSON-RPC

### **MCP Server's Role:**
- **Orchestration**: Routes requests, validates inputs, handles errors
- **Prompt Engineering**: Applies context-aware templates for better responses
- **Protocol Translation**: Converts between MCP JSON-RPC and Ollama REST API
- **State Management**: Maintains conversation history and context
- **Multi-Model Support**: Abstract interface for different LLMs

## **Concepts**

### **MCP (Model Context Protocol)**
- Open standard for connecting AI assistants to data sources and tools
- Provides **Tools** (functions AI can call), **Resources** (data sources), **Prompts** (templates)
- Benefits: Standardization, security, modularity, scalability

### **LLM Inference Process**
- **Tokenization**: Text → numerical tokens (e.g., "Hello" → [15496])
- **Embeddings**: Tokens → high-dimensional vectors (e.g., [0.1, -0.3, 0.7, ...])
- **Forward Pass**: Neural network processes embeddings through attention layers
- **Token Selection**: Probability-based selection of next token (temperature, top-p)
- **Iteration**: Repeat until completion or max tokens

### **Prompt Templates**
- Structured formats: System message + Context + User input + Format instructions
- Variable substitution: `{{user_input}}` → actual user text
- Context-aware: Different templates for coding, chat, analysis use cases


## **Start the Server:**
```bash
npm run server
# or
node dist/index.js server --transport stdio
```

### **Run Interactive Client:**
```bash
npm run client
# or
node dist/index.js client
```

### **Test with Examples:**
```bash
node examples/simple-client.js
python3 examples/python-client.py
```

### **Deploy with Docker:**
```bash
docker-compose up -d
```