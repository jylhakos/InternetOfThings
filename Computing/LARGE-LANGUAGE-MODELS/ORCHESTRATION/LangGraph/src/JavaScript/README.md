# 🚗 Taxi Booking Agents by LangGraph

An implementation of LangGraph agents with taxi booking tools for cities like London, Berlin, Paris, Madrid, and Rome. This project demonstrates how to use **LangChain** and **LangGraph** libraries with **Node.js** to create intelligent agents that can:

- 🌍 **Geocode locations** - Get coordinates for cities
- 🚗 **Book taxis** - Reserve vehicles with different service types  
- 📊 **Check booking status** - Monitor existing reservations

*Choose your model, deploy locally or in the cloud, and enjoy privacy or cost effective AI agent solutions.*

🚗 **Taxi booking by LangGraph Agents** 🤖

## Table of Contents

- [Features](#features)
- [🛠️ Installation](#️-installation)
- [Quick Start](#quick-start)
- [How LangGraph Agents Use Tools](#how-langgraph-agents-use-tools)
- [🔧 Tool Functions Explained](#-tool-functions-explained)
- [API References](#api-references)
- [Testing](#testing)
- [ Project Structure](#project-structure)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Features

### Functionality
- **Multi-city support**: London, Berlin, Paris, Madrid, Rome
- **Multiple taxi types**: Economy, Premium, Luxury, Van
- **Real-time status checking**: Track booking progress
- **Geocoding integration**: Convert city names to coordinates
- **Comprehensive error handling**: Robust validation and fallbacks

### LangGraph Implementation
- **StateGraph workflow**: Structured agent conversation flow
- **Tool binding**: Seamless integration between LLM and tools
- **Memory management**: Persistent conversation context
- **Streaming support**: Real-time response generation

## 🛠️ Installation

### Prerequisites
- **Node.js 18+** (required for ES modules and modern features)
- **npm** or **yarn** package manager  
- **OpenAI API key** (for LLM functionality)

### Step 1: Install LangGraph CLI

```bash
npx @langchain/langgraph-cli
```

### Step 2: Clone and Setup Project

```bash
cd LARGE-LANGUAGE-MODELS/ORCHESTRATION/LangGraph/src/JavaScript

# Run automated setup
npm run setup
```

### Step 3: Install Dependencies Manually (if needed)

```bash
# Install core dependencies
npm install

# Install LangGraph CLI globally (optional)
npm install -g @langchain/langgraph-cli
```

### Step 4: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

Required environment variables:
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

## Quick Start

### Step 1: Navigate to the JavaScript project
```bash
cd src/JavaScript
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Run the Demo (No API Key Required)
```bash
npm run demo
```

### Step 4: Run Tests
```bash
npm test
```

### Step 5: Validate Project Setup
```bash
npm run validate
```

### Step 6: Set Up Environment (Optional)
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your OpenAI API key for full agent functionality
nano .env
```

Required environment variables for full functionality:
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### Commands

| Command | Description |
|---------|-------------|
| `npm run demo` | 🎬 Interactive demo showing all tools in action (no API key needed) |
| `npm run ollama-demo` | 🦙 Demo using local Ollama LLMs instead of OpenAI |
| `npm test` | 🧪 Run comprehensive test suite |
| `npm run validate` | ✅ Validate entire project setup |
| `npm start` | 🤖 Run the main agent application (requires OpenAI API key) |
| `npm run dev` | 🚀 Start LangGraph development server (port 2024) |
| `npm run sdk-example` | 📡 Test LangGraph SDK integration |
| `npm run setup` | ⚙️ Automated setup and validation |

## How LangGraph Agents Use Tools?

LangGraph agents utilize a **4-step tool calling process**:

### 1. 🔨 Tool Creation
Tools are defined using LangChain's `tool` function, creating an association between a function and its schema:

```javascript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const taxiBookingTool = tool(
  async ({ city, pickup_address, destination_address, passenger_count, taxi_type }) => {
    // Tool implementation
    return bookingResult;
  },
  {
    name: "bookTaxi",
    description: "Book a taxi in supported cities",
    schema: z.object({
      city: z.string().describe("The city where the taxi is needed"),
      pickup_address: z.string().describe("Pickup address or location"),
      destination_address: z.string().describe("Destination address"),
      passenger_count: z.number().min(1).max(8).describe("Number of passengers"),
      taxi_type: z.enum(["economy", "premium", "luxury", "van"])
    }),
  }
);
```

### 2. 🔗 Tool Binding
Tools are connected to a model that supports tool calling, giving the model awareness of available tools:

```javascript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ temperature: 0.1 });
const modelWithTools = model.bindTools([taxiBookingTool, geocodingTool, statusTool]);
```

### 3. Tool Calling
When appropriate, the model decides to call tools and ensures responses conform to tool schemas:

```javascript
const response = await modelWithTools.invoke([
  new HumanMessage("Book a taxi in London from Heathrow to Westminster for 2 passengers")
]);

// Response contains tool_calls if the model decides to use tools
if (response.tool_calls && response.tool_calls.length > 0) {
  console.log("Model wants to call:", response.tool_calls[0].name);
}
```

### 4. ⚙️ Tool Execution
Tools are executed using arguments provided by the model:

```javascript
// In LangGraph, this is handled by ToolNode
const toolNode = new ToolNode([taxiBookingTool, geocodingTool, statusTool]);

// Tools are automatically executed based on model's tool_calls
const toolResults = await toolNode.invoke(state);
```

## 🔧 Tool Functions Explained

### 🌍 Geocoding Tool (`geocodingTool`)
Converts city names to geographical coordinates.

**Purpose**: Provides location data for taxi booking services
**API Reference**: [MapTiler Geocoding API](https://docs.maptiler.com/server/api/geocoding/)

```javascript
// Usage example
const result = await geocodingTool.invoke({ city: "London" });
// Returns: "Location found: London - Latitude: 51.5074, Longitude: -0.1278, Country: UK"
```

**Schema**:
- `city` (string): City name to geocode

### 🚗 Taxi Booking Tool (`bookTaxi`)
Books taxi reservations with comprehensive options.

**Purpose**: Main booking functionality for taxi services
**API Reference**: [Taxi API Example](https://api.taxicode.com/)

```javascript
// Usage example  
const booking = await taxiBookingTool.invoke({
  city: "Berlin",
  pickup_address: "Brandenburg Gate", 
  destination_address: "Berlin Hauptbahnhof",
  passenger_count: 3,
  taxi_type: "premium"
});
```

**Schema**:
- `city` (string): Target city for booking
- `pickup_address` (string): Pickup location
- `destination_address` (string): Drop-off location
- `passenger_count` (number 1-8): Number of passengers
- `taxi_type` (enum): "economy" | "premium" | "luxury" | "van"
- `booking_time` (string, optional): ISO timestamp for scheduled booking

### Status Check Tool (`checkTaxiStatus`)
Monitors existing taxi bookings.

**Purpose**: Real-time tracking of booking progress

```javascript
// Usage example
const status = await taxiStatusTool.invoke({
  booking_id: "taxi_1735123456789_abc123def"
});
```

**Schema**:
- `booking_id` (string): Unique booking identifier

## API References

### LangGraph Documentation
- **Main Documentation**: [LangGraph.js](https://langchain-ai.github.io/langgraphjs/)
- **Tool Calling Guide**: [LangChain Tool Calling](https://js.langchain.com/docs/concepts/tool_calling/)
- **StateGraph API**: [StateGraph Reference](https://langchain-ai.github.io/langgraphjs/reference/classes/langgraph.StateGraph.html)

### External APIs
- **Geocoding**: [MapTiler Geocoding API](https://docs.maptiler.com/server/api/geocoding/)
- **Taxi Services**: [Taxi API Example](https://api.taxicode.com/)

### Key LangGraph Concepts

#### StateGraph Workflow
```javascript
import { StateGraph, START, END } from "@langchain/langgraph";

const workflow = new StateGraph(AgentState);
workflow.addNode("agent", callModel);
workflow.addNode("tools", toolNode);
workflow.setEntryPoint("agent");
workflow.addConditionalEdges("agent", shouldCallTool, {
  tools: "tools",
  end: END
});
```

#### Tool Node Integration
```javascript
import { ToolNode } from "@langchain/langgraph/prebuilt";

const toolNode = new ToolNode(taxiTools);
// Automatically handles tool execution and result formatting
```

## � API Service Usage

### REST API Format for AI Agent + Tool Call Service

```bash
# Start the LangGraph development server
npm run dev
# Server runs on http://localhost:2024
```

#### API Endpoints

```http
POST /api/runs/stream
Content-Type: application/json

{
  "assistant_id": "agent",
  "input": {
    "messages": [
      {
        "role": "user",
        "content": "Book a taxi in London from Heathrow to Westminster for 2 passengers"
      }
    ]
  },
  "stream_mode": "messages"
}
```

#### Example API Usage with curl

```bash
# Stream a taxi booking request
curl -X POST http://localhost:2024/api/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [
        {"role": "user", "content": "I need a taxi in Berlin from Brandenburg Gate to Hauptbahnhof"}
      ]
    },
    "stream_mode": "messages"
  }'
```

#### JavaScript SDK Usage

```javascript
import { Client } from "@langchain/langgraph-sdk";

const client = new Client({ apiUrl: "http://localhost:2024" });

const streamResponse = client.runs.stream(
  null, // Threadless run
  "agent", // Assistant ID
  {
    input: {
      "messages": [
        { "role": "user", "content": "Book a luxury taxi in Paris for 4 people" }
      ]
    },
    streamMode: "messages-tuple",
  }
);

for await (const chunk of streamResponse) {
  console.log(`Event: ${chunk.event}`);
  console.log(JSON.stringify(chunk.data, null, 2));
}
```

## 🦙 Ollama + Local LLM Alternative Setup

### **Architecture: OpenAI vs Ollama**

**Important**: This project provides **two separate agent implementations**:

```bash
# 🌐 CLOUD-BASED: OpenAI Implementation
agents/taxi-booking-agent.js     # Uses ChatOpenAI → OpenAI API servers
npm run demo                     # Requires OPENAI_API_KEY

# 🏠 LOCAL: Ollama Implementation  
agents/ollama-taxi-agent.js      # Uses ChatOllama → Local Ollama server
npm run ollama-demo              # No API key needed, runs locally
```

**No API Bridge**: The system does **NOT** use OpenAI API to call Ollama. Each implementation communicates directly with its respective backend:
- OpenAI agent → `api.openai.com`
- Ollama agent → `localhost:11434`

### Why Use Ollama Instead of OpenAI?

- **Privacy**: Data stays local, no cloud API calls
- **Cost**: No per-token charges, unlimited usage
- **Offline**: Works without internet connection
- **Customizable**: Use any compatible model
- **Performance**: Optimized for local hardware
- **Specialized Models**: Access to agent-specific models like ArceeAgents

### Step 1: Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com/download

# Start Ollama service
ollama serve
```

### Step 2: Install Recommended LLM Models

#### ** Models Optimized for Tool Calling**

```bash
# === RECOMMENDED FOR TAXI BOOKING AGENTS ===

# BEST OVERALL: Llama 3.1 8B (Excellent tool calling)
ollama pull llama3.1:8b

# LIGHTWEIGHT: Llama 3.2 3B (Good performance, low resources)
ollama pull llama3.2:3b

# ⚡ CODE-FOCUSED: CodeLlama 7B (Outstanding for tool calling)
ollama pull codellama:7b

# ADVANCED: Llama 3.1 13B (Best quality, high resources)
ollama pull llama3.1:13b
```

#### **🤖 Specialized Agent Models**

```bash
# === AGENT-SPECIFIC MODELS ===

# ArceeAgents (Fine-tuned for agent tasks) - if available
ollama pull arcee-agent:7b

# Function-calling optimized models
ollama pull functionary:7b-v2
ollama pull nexusraven:13b

# Mistral models (excellent reasoning)
ollama pull mistral:7b-instruct-v0.3
ollama pull mistral-nemo:12b

# Qwen models (strong tool calling)
ollama pull qwen2:7b-instruct
ollama pull qwen2.5:7b-instruct
```

#### **⚙️ Quantized Models (Memory Optimized)**

```bash
# === QUANTIZED VERSIONS (Lower VRAM usage) ===

# 4-bit quantization (~4-6GB VRAM)
ollama pull llama3.1:8b-instruct-q4_0
ollama pull codellama:7b-instruct-q4_0

# 8-bit quantization (~7-9GB VRAM) 
ollama pull llama3.1:8b-instruct-q8_0
ollama pull mistral:7b-instruct-q8_0

# Check all installed models
ollama list
```

### Step 3: Test Ollama Installation

```bash
# Test the model
ollama run llama3.2:3b "Hello, how are you?"

# Test tool calling capability
ollama run llama3.1:8b "I need to book a taxi in London. What information do you need?"

# Test agent-specific models (if available)
ollama run arcee-agent:7b "Book a taxi in Berlin from airport to hotel"
ollama run functionary:7b-v2 "What are the coordinates of Paris?"
ollama run codellama:7b "I need a luxury taxi for 4 passengers in Madrid"
```

### **Step 3b: Model Tool Calling Benchmarks**

Test different models with taxi booking tasks:

```bash
# Quick tool calling test for each model
echo "Testing llama3.1:8b..." && ollama run llama3.1:8b "Book economy taxi in London for 2 passengers"
echo "Testing codellama:7b..." && ollama run codellama:7b "Get coordinates for Berlin"
echo "Testing mistral:7b..." && ollama run mistral:7b "Check booking status for taxi_12345"

# Compare response quality and function calling accuracy
```

### Step 4: Configure LangGraph Agent for Ollama

Create a new agent file `agents/ollama-taxi-agent.js`:

```javascript
import { ChatOllama } from "@langchain/ollama";
import { StateGraph, START, END } from "@langchain/langgraph";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import { taxiTools } from "../tools/taxi-booking-tool.js";

// Create Ollama LLM instance
const llm = new ChatOllama({
  baseUrl: "http://localhost:11434", // Default Ollama URL
  model: "llama3.1:8b", // Use your installed model
  temperature: 0.1,
});

// Create agent with Ollama
export class OllamaTaxiAgent {
  constructor() {
    this.model = llm.bindTools(taxiTools);
    this.toolNode = new ToolNode(taxiTools);
    this.workflow = this.buildWorkflow();
    this.app = this.workflow.compile();
  }

  buildWorkflow() {
    const workflow = new StateGraph({
      messages: {
        value: (x, y) => x.concat(y),
        default: () => [],
      },
    });

    workflow.addNode("agent", this.callModel.bind(this));
    workflow.addNode("tools", this.toolNode);
    workflow.setEntryPoint("agent");
    
    workflow.addConditionalEdges(
      "agent",
      this.shouldCallTool.bind(this),
      {
        tools: "tools",
        end: END,
      }
    );
    
    workflow.addEdge("tools", "agent");
    return workflow;
  }

  async callModel(state) {
    const messages = state.messages;
    const response = await this.model.invoke(messages);
    return { messages: [response] };
  }

  shouldCallTool(state) {
    const messages = state.messages;
    const lastMessage = messages[messages.length - 1];
    
    if (lastMessage.tool_calls && lastMessage.tool_calls.length > 0) {
      return "tools";
    }
    return "end";
  }
}
```

### Step 5: Update Environment Configuration

Update your `.env` file with model-specific options:

```bash
# === DUAL CONFIGURATION SUPPORT ===

# OpenAI Configuration (Cloud-based)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Ollama Configuration (Local)
OLLAMA_BASE_URL=http://localhost:11434

# === MODEL SELECTION OPTIONS ===

# RECOMMENDED: Best overall performance
OLLAMA_MODEL=llama3.1:8b

# TOOL CALLING OPTIMIZED: Best for function calling
# OLLAMA_MODEL=codellama:7b

# 🤖 AGENT-SPECIFIC: Fine-tuned for agent tasks (if available)
# OLLAMA_MODEL=arcee-agent:7b
# OLLAMA_MODEL=functionary:7b-v2

# ⚡ LIGHTWEIGHT: Lower resource usage
# OLLAMA_MODEL=llama3.2:3b

# HIGH QUALITY: Best performance (high resources)
# OLLAMA_MODEL=llama3.1:13b

# QUANTIZED: Memory optimized versions
# OLLAMA_MODEL=llama3.1:8b-instruct-q4_0  # 4-bit quantization
# OLLAMA_MODEL=codellama:7b-instruct-q8_0  # 8-bit quantization

# LangGraph Server Configuration
LANGGRAPH_API_URL=http://localhost:2024
```

### **Step 5b: Dynamic Model Switching**

Switch between models without restarting:

```bash
# Test different models with the same agent
export OLLAMA_MODEL=llama3.1:8b && npm run ollama-demo
export OLLAMA_MODEL=codellama:7b && npm run ollama-demo
export OLLAMA_MODEL=mistral:7b-instruct && npm run ollama-demo

# Compare performance
npm run validate  # Check which model performs best
```

### Step 6: Create Ollama Demo Script

Create `ollama-demo.js`:

```javascript
import { OllamaTaxiAgent } from "./agents/ollama-taxi-agent.js";
import { HumanMessage } from "@langchain/core/messages";

async function ollamaDemo() {
  console.log("🦙 Ollama Taxi Booking Agent Demo");
  console.log("==================================\n");

  try {
    const agent = new OllamaTaxiAgent();
    
    const queries = [
      "I need a taxi in London from Heathrow to Westminster for 2 passengers",
      "What are the coordinates of Berlin?",
      "Book a luxury taxi in Paris from Eiffel Tower to Louvre for 4 people"
    ];

    for (const query of queries) {
      console.log(`👤 User: ${query}`);
      console.log("🦙 Ollama Agent: Processing...\n");

      const initialState = {
        messages: [new HumanMessage(query)]
      };

      let finalState;
      const stream = await agent.app.stream(initialState);
      
      for await (const output of stream) {
        finalState = output;
      }

      const messages = Object.values(finalState)[0].messages;
      const lastMessage = messages[messages.length - 1];
      
      console.log(`🤖 Response: ${lastMessage.content}\n`);
      console.log("-".repeat(60) + "\n");
    }
  } catch (error) {
    console.error("❌ Error:", error.message);
    console.log("💡 Make sure Ollama is running: ollama serve");
    console.log("💡 And model is installed: ollama pull llama3.1:8b");
  }
}

ollamaDemo();
```

### Step 7: Install Ollama Dependencies

```bash
# Install Ollama LangChain integration
npm install @langchain/ollama

# Update package.json scripts
npm run build # if you have a build script
```

### Step 8: Performance Optimization for Ollama

#### **🔧 Hardware Requirements & Tool Calling Performance**

| Model | Size | RAM Required | VRAM (GPU) | Tool Calling Quality | Speed | Best For |
|-------|------|--------------|------------|---------------------|-------|----------|
| **llama3.2:3b** | 3B | 4GB+ | 3GB | ⭐⭐⭐ Good | Fast | Basic tasks, testing |
| **codellama:7b** | 7B | 8GB+ | 5GB | ⭐⭐⭐⭐⭐ **Excellent** | Fast | **Tool calling** |
| **llama3.1:8b** | 8B | 12GB+ | 6GB | ⭐⭐⭐⭐⭐ **Excellent** | ⚡ Medium | **Recommended** |
| **mistral:7b** | 7B | 8GB+ | 5GB | ⭐⭐⭐⭐ Very Good | Fast | Reasoning tasks |
| **functionary:7b** | 7B | 8GB+ | 5GB | ⭐⭐⭐⭐⭐ **Outstanding** | ⚡ Medium | **Function calling** |
| **qwen2:7b** | 7B | 8GB+ | 5GB | ⭐⭐⭐⭐ Very Good | Fast | Multi-language |
| **arcee-agent:7b** | 7B | 8GB+ | 5GB | ⭐⭐⭐⭐⭐ **Specialized** | ⚡ Medium | **Agent tasks** |
| **llama3.1:13b** | 13B | 16GB+ | 10GB | ⭐⭐⭐⭐⭐ **Outstanding** | Slow | Best quality |

#### **Model Selection**

```bash
# TOP RECOMMENDATIONS FOR TAXI BOOKING AGENTS:

# 1. BEST OVERALL: Great balance of performance and resources
OLLAMA_MODEL=llama3.1:8b

# 2. BEST FOR TOOL CALLING: Optimized for function calling
OLLAMA_MODEL=codellama:7b

# 3. SPECIALIZED AGENTS: If available (fine-tuned for agents)
OLLAMA_MODEL=arcee-agent:7b
OLLAMA_MODEL=functionary:7b-v2

# 4. LIGHTWEIGHT: For resource-constrained environments
OLLAMA_MODEL=llama3.2:3b

# 5. BEST QUALITY: If you have powerful hardware
OLLAMA_MODEL=llama3.1:13b
```

#### **⚡ Quantized Models Comparison**

| Model | Original Size | Quantized Size | Quality Loss | VRAM Savings |
|-------|---------------|----------------|--------------|--------------|
| `llama3.1:8b` | ~16GB | `q4_0`: ~4.6GB | ~5% | 65% |
| `llama3.1:8b` | ~16GB | `q8_0`: ~8.5GB | ~2% | 45% |
| `codellama:7b` | ~13GB | `q4_0`: ~3.8GB | ~5% | 70% |
| `mistral:7b` | ~13GB | `q4_0`: ~4.1GB | ~3% | 68% |

#### Optimization Tips

```bash
# Enable GPU acceleration (if available)
export OLLAMA_GPU=1

# Adjust context size for better performance
export OLLAMA_NUM_CONTEXT=4096

# Set thread count for CPU optimization
export OLLAMA_NUM_THREAD=8

# Use quantized models for lower memory usage
export OLLAMA_MODEL=llama3.1:8b-instruct-q4_0

# Start optimized Ollama
ollama serve
```

### Step 9: Model Comparison

| Aspect | OpenAI GPT-3.5/4 | Ollama Local LLMs |
|--------|-------------------|-------------------|
| **Cost** | Pay per token | Free after setup |
| **Privacy** | Data sent to OpenAI | 100% local |
| **Speed** | Very fast | Depends on hardware |
| **Quality** | Excellent | Good (model dependent) |
| **Setup** | API key only | Install + model download |
| **Internet** | Required | Optional |
| **Customization** | Limited | Full control |

### Step 10: Troubleshooting Ollama & Model Issues

#### **🔧 General Ollama Troubleshooting**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# View Ollama logs
ollama logs

# Restart Ollama service
pkill ollama && ollama serve

# Check available models
ollama list
```

#### **🤖 Model-Specific Troubleshooting**

```bash
# === MODEL AVAILABILITY ===

# Check if specific model exists
ollama show llama3.1:8b
ollama show codellama:7b
ollama show arcee-agent:7b  # May not be available

# Download missing models
ollama pull functionary:7b-v2
ollama pull qwen2:7b-instruct

# === PERFORMANCE ISSUES ===

# Check model resource usage
ollama ps  # Show running models and memory usage

# Free up memory by unloading models
ollama unload llama3.1:13b  # Unload large model
ollama load llama3.1:8b     # Load smaller model

# === TOOL CALLING ISSUES ===

# Test specific model tool calling
ollama run codellama:7b "Use get_weather tool for London"
ollama run llama3.1:8b "Call booking function for Berlin taxi"

# Compare model responses
echo "Testing tool calling accuracy..." 
for model in llama3.1:8b codellama:7b mistral:7b-instruct; do
  echo "=== Testing $model ==="
  ollama run $model "Book a taxi in Paris from airport to hotel for 2 people"
done
```

#### **⚠️ Common Issues & Solutions**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Model not found** | `Error: model not found` | `ollama pull model-name` |
| **Out of memory** | Slow responses, crashes | Use quantized model (`q4_0`, `q8_0`) |
| **Poor tool calling** | Agent doesn't use tools | Switch to `codellama:7b` or `functionary:7b` |
| **Connection refused** | `curl: connection refused` | `ollama serve` in separate terminal |
| **Slow responses** | Long response times | Reduce model size or enable GPU |

#### **Model Selection Troubleshooting**

```bash
# If current model isn't working well, try alternatives:

# Poor tool calling → Switch to code-optimized
export OLLAMA_MODEL=codellama:7b

# Out of memory → Use quantized version  
export OLLAMA_MODEL=llama3.1:8b-instruct-q4_0

# Need better quality → Upgrade model
export OLLAMA_MODEL=llama3.1:13b

# Want agent specialization → Use fine-tuned (if available)
export OLLAMA_MODEL=arcee-agent:7b

# Test the change
npm run ollama-demo
```

## Testing

### Comprehensive Test Suite
```bash
npm test
```

**Test Coverage**:
- Individual tool functionality
- Schema validation
- Error handling
- Agent integration
- Tool binding verification

### Manual Testing
```bash
# Test tools directly
node test/test-taxi-tool.js

# Test individual components
node -e "
import { geocodingTool } from './tools/taxi-booking-tool.js';
console.log(await geocodingTool.invoke({ city: 'Paris' }));
"
```

## Project Structure

```
src/JavaScript/
├── 📄 package.json                     # Project dependencies and scripts
├── 📄 .gitignore                       # Git exclusions
├── 📄 .env.example                     # Environment template
├── 📄 index.js                         # Main agent application
├── 📄 demo.js                          # Interactive demo (no API key needed)
├── 📄 validate.js                      # Project validation script
├── 📄 config.json                      # Configuration and constants
├── � QUICKSTART.md                    # Quick start guide
├── �📁 agents/                          # AI Agent implementations
│   └── 📄 taxi-booking-agent.js        # LangGraph StateGraph agent
├── 📁 tools/                           # Tool function definitions
│   └── 📄 taxi-booking-tool.js         # Three taxi booking tools
├── 📁 test/                            # Test suite
│   └── 📄 test-taxi-tool.js            # Comprehensive tests
├── 📁 examples/                        # Integration examples
│   └── 📄 langgraph-sdk-integration.js # LangGraph SDK usage
├── 📁 setup/                           # Setup utilities
│   └── 📄 install-deps.js              # Automated installation
└── 📁 node_modules/                    # Dependencies (git ignored)
```

### Files

| File/Folder | Purpose |
|-------------|---------|
| **PROJECT.md** | Complete project summary with implementation details |
| **agents/taxi-booking-agent.js** | Core LangGraph agent with StateGraph workflow |
| **agents/ollama-taxi-agent.js** | Local Ollama LangGraph agent implementation |
| **tools/taxi-booking-tool.js** | Three tools: geocoding, booking, status checking |
| **demo.js** | Standalone demo showing tools without LLM |
| **ollama-demo.js** | Ollama-specific demo with local LLM integration |
| **index.js** | Full agent with LLM integration |
| **test/test-taxi-tool.js** | Comprehensive test suite for all functionality |
| **validate.js** | Project health checker |
| **config.json** | Cities, taxi types, and configuration data |

## AI Agents Data Flow & Tool Calling

```mermaid
graph TB
    subgraph "User Interaction"
        A[👤 User Input<br/>\"Book taxi in London\"]
    end
    
    subgraph "LangGraph Agent"
        B[🤖 StateGraph Agent<br/>Process Input]
        C{LLM Decision<br/>Call Tools?}
        D[Tool Calling<br/>Select & Execute]
        E[State Update<br/>Add Results]
        F[💬 Response Generation<br/>Format Output]
    end
    
    subgraph "Tool Functions"
        G[🌍 Geocoding Tool<br/>Get Coordinates]
        H[🚗 Taxi Booking Tool<br/>Create Reservation]
        I[Status Tool<br/>Check Booking]
    end
    
    subgraph "External APIs"
        J[�️ MapTiler API<br/>Geocoding Service]
        K[🚖 Taxi API<br/>Booking Service]
    end
    
    A --> B
    B --> C
    C -->|Yes| D
    C -->|No| F
    D --> G
    D --> H
    D --> I
    G --> J
    H --> K
    G --> E
    H --> E
    I --> E
    E --> C
    F --> L[User Response]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#e8f5e8
    style G fill:#fff9c4
    style H fill:#fff9c4
    style I fill:#fff9c4
```

**Figure: AI Agents Tool Call Data Flow**

### Tool Calling Process

1. **User Input** → Agent receives natural language request
2. **LLM Analysis** → Model determines if tools are needed
3. **Tool Selection** → Agent selects appropriate tools based on context
4. **Tool Execution** → Tools run with validated parameters
5. **Result Integration** → Tool outputs integrated into conversation
6. **Response Generation** → Final response formatted for user

## Usage

### Example 1: Simple Geocoding
```bash
User: "What are the coordinates of Berlin?"
Agent: "Location found: Berlin - Latitude: 52.5200, Longitude: 13.4050, Country: Germany"
```

### Example 2: Taxi Booking
```bash
User: "I need a taxi in London from Heathrow Airport to Westminster for 2 passengers"

Agent: "Taxi booked successfully.
📍 City: London
🚗 Booking ID: taxi_1735123456789_abc123def
👥 Passengers: 2
🎯 Type: economy
📍 From: Heathrow Airport
📍 To: Westminster
⏰ Estimated arrival: 12 minutes
💰 Estimated cost: £18
👨‍✈️ Driver: John Doe
📞 Contact: +44-xxx-xxx-xxxx
🚙 Vehicle: Toyota Prius - ABC 123
📅 Status: CONFIRMED"
```

### Example 3: Status Check
```bash
User: "Check status of booking taxi_1735123456789_abc123def"

Agent: "🚗 Taxi Status Update
📋 Booking ID: taxi_1735123456789_abc123def
📊 Status: EN_ROUTE
⏰ ETA: 3 minutes
📍 Driver location: 2.1 km away
💬 Driver is en route to your pickup location."
```

### Example 4: Complex Multi-Step Request
```bash
User: "I want to book a luxury taxi in Paris from Notre-Dame to Eiffel Tower for 4 people"

# The agent will:
# 1. Use geocodingTool to verify Paris location
# 2. Use taxiBookingTool to create the reservation
# 3. Return comprehensive booking confirmation
```

## Troubleshooting

### Issues

#### 1. "OpenAI API Key not found"
```bash
# Solution: Check your .env file
cat .env | grep OPENAI_API_KEY

# Make sure it's set correctly
OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### 2. "Module not found" errors
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### 3. "Tool not binding correctly"
```bash
# Solution: Check tool exports
node -e "
import { taxiTools } from './tools/taxi-booking-tool.js';
console.log('Loaded tools:', taxiTools.length);
console.log('Tool names:', taxiTools.map(t => t.name));
"
```

#### 4. "LangGraph CLI not found"
```bash
# Solution: Install CLI globally
npm install -g @langchain/langgraph-cli

# Or use npx
npx @langchain/langgraph-cli dev
```

### Debug Mode
Enable verbose logging:
```bash
# Set debug environment variable
DEBUG=langgraph:* npm start
```

### Validation
```bash
# Check project structure
npm run setup

# Validate all components
npm test

# Test individual tools
node test/test-taxi-tool.js
```

## **Advanced Models (Options)**

### **Experimental Models**

Keep an eye on these future models for even better agent performance.

```bash
# === NEXT-GENERATION MODELS ===

# Llama 4 Scout (when available)
# ollama pull llama4:scout          # 10M context, native tool calling
# OLLAMA_MODEL=llama4:scout

# Advanced agent models
# ollama pull hermes-2-pro:7b       # Enhanced reasoning
# ollama pull wizard-vicuna:13b     # Instruction following
# ollama pull openchat:7b-v3.5      # Conversation optimized

# === SPECIALIZED TOOL-CALLING MODELS ===

# NexusRaven (Function calling specialist)
# ollama pull nexusraven:13b

# Gorilla (API calling optimized) 
# ollama pull gorilla-openfunctions:7b

# ToolLlama (Tool usage fine-tuned)
# ollama pull toolllama:7b
```

### **Recommendations for models by Use Case**

| Use Case | Primary Model | Alternative | Lightweight Option |
|----------|---------------|-------------|-------------------|
| **General Taxi Booking** | `llama3.1:8b` | `mistral:7b-instruct` | `llama3.2:3b` |
| **Complex Tool Chains** | `codellama:7b` | `functionary:7b-v2` | `qwen2:7b-instruct` |
| **Agent Conversations** | `arcee-agent:7b` | `hermes-2-pro:7b` | `openchat:7b` |
| **Code Generation** | `codellama:13b` | `wizard-coder:7b` | `codellama:7b-instruct-q4_0` |
| **Reasoning Tasks** | `llama3.1:13b` | `mistral-nemo:12b` | `llama3.1:8b-instruct-q8_0` |

### **Performance**

Track your model performance.

```bash
# Monitor model efficiency
npm run validate | grep "Tool calling accuracy"

# Benchmark different models
for model in llama3.1:8b codellama:7b mistral:7b arcee-agent:7b; do
  export OLLAMA_MODEL=$model
  echo "=== Testing $model ==="
  time npm run ollama-demo > /dev/null
done

# Resource usage monitoring
ollama ps  # Check memory usage
nvidia-smi  # Check GPU usage (if available)
```
### **Roadmap**

Planned enhancements for this project.

- **Llama 4 Scout Integration** - Native 10M context tool calling
- **Multi-model Ensemble** - Use different models for different tasks
- **Model Auto-selection** - Choose best model based on query complexity
- **Fine-tuning** - Train models specifically for taxi booking
- **Performance Benchmarking** - Automated model comparison suite

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
