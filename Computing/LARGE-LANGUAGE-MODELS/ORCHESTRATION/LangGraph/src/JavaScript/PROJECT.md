# Taxi Booking Agents by LangGraph

## Project

This project presents a **LangGraph agents implementation** with taxi booking tools, featuring both **OpenAI API** and **Ollama local LLM** support. The project implements AI agent with practical, real-world taxi booking functionality while maintaining privacy options and cost flexibility through local LLM support.

### 🆕 Recent Updates (2025)

1. **.gitignore** - Complete Git exclusions for Node.js projects
2. **Project Structure** - Detailed file and folder descriptions
3. **Mermaid Diagram** - AI agent data flow visualization
4. **API Service Documentation** - REST API usage examples
5. **🦙 Ollama Integration** - Complete local LLM alternative setup
6. **Testing** - Ollama-specific validation
7. 🚗 **Ready for production** 🤖

### 📁 Complete Project Structure (15 Files)

```
src/JavaScript/
├── 📄 .gitignore                       # Git exclusions (NEW)
├── 📄 package.json                     # Updated with Ollama deps
├── 📄 .env.example                     # Updated with Ollama config
├── 📄 index.js                         # Main OpenAI agent
├── 📄 demo.js                          # Standalone demo
├── 📄 ollama-demo.js                   # Ollama demo (NEW)
├── 📄 validate.js                      # Project validator
├── 📄 config.json                      # Configuration data
├── 📄 QUICKSTART.md                    # Quick start guide
├── 📁 agents/
│   ├── 📄 taxi-booking-agent.js        # OpenAI LangGraph agent
│   └── 📄 ollama-taxi-agent.js         # Ollama LangGraph agent (NEW)
├── 📁 tools/
│   └── 📄 taxi-booking-tool.js         # Three powerful tools
├── 📁 test/
│   └── 📄 test-taxi-tool.js            # Comprehensive tests
├── 📁 examples/
│   └── 📄 langgraph-sdk-integration.js # SDK examples
└── 📁 setup/
    └── 📄 install-deps.js              # Automated setup
```

## Commands (8 Total)

| Command | Description | API Required |
|---------|-------------|--------------|
| `npm run demo` | Interactive tool demo | ❌ None |
| `npm run ollama-demo` | 🦙 Ollama LLM demo | ❌ None (local) |
| `npm test` | Test suite | ❌ None |
| `npm run validate` | Project validation | ❌ None |
| `npm start` | 🤖 OpenAI agent | ✅ OpenAI API |
| `npm run dev` | LangGraph server | ✅ OpenAI API |
| `npm run sdk-example` | SDK integration | ✅ OpenAI API |
| `npm run setup` | Automated setup | ❌ None |

## AI Agents Data Flow

The project includes a **Mermaid diagram** showing:
- User input processing
- LLM decision making
- Tool selection and execution
- State management
- Response generation

##Features Implemented

### Functionality
- **3 Powerful Tools**: Geocoding, Taxi Booking, Status Checking
- **5 Supported Cities**: London, Berlin, Paris, Madrid, Rome
- **4 Taxi Types**: Economy, Premium, Luxury, Van
- **Comprehensive Validation**: Schema validation with Zod
- **Error Handling**: Robust error messages and recovery

### LangGraph Implementation
- **StateGraph Workflow**: Complete agent conversation flow
- **Tool Binding**: Seamless LLM-tool integration
- **Memory Management**: Persistent conversation context
- **Streaming Support**: Real-time response generation

### Dual LLM Support
- **OpenAI Integration**: Traditional cloud-based LLMs
- **Ollama Integration**: Local, private, cost-free LLMs
- **Models**: Support for multiple local models
- **Performance**: Hardware-specific configuration

## How to Use Agents by LangGraph?

### Option 1: Quick Demo (No Setup)
```bash
cd src/JavaScript
npm install
npm run demo
```

### Option 2: OpenAI Agent (Cloud)
```bash
# Add OpenAI API key to .env
npm start
```

### Option 3: Ollama Agent (Local)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download model
ollama pull llama3.1:8b

# Run demo
npm run ollama-demo
```

## Testing Results

- **Tools are working correctly**
- **Project setup verified**
- **OpenAI and Ollama agents are functional**

## Documentation

1. **Step-by-step installation** for both OpenAI and Ollama
2. **Complete API documentation** with examples
3. **Mermaid diagrams** showing agent workflow
4. **Performance comparisons** between cloud and local LLMs
5. **Troubleshooting guides** for common issues
6. **Model recommendations** for different use cases

---