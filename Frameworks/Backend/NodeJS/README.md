# Full-Stack Software Development by Node.js

An overview of software development using Node.js, Express.js, Next.js, MCP and Vite for building scalable web applications with server-side rendering and LLM integration capabilities.

## Table of Contents

- [Overview](#overview)
- [Node.js](#nodejs)
- [Next.js and Server-Side Rendering](#nextjs-and-server-side-rendering)
- [Express.js Backend Development](#expressjs-backend-development)
- [Vite Frontend Tooling](#vite-frontend-tooling)
- [Full-Stack Integration](#full-stack-integration)
- [LLM Integration with Node.js](#llm-integration-with-nodejs)
- [LLMs Interaction with MCP and Express](#llms-interaction-with-mcp-and-express)
  - [Core Components](#core-components)
  - [MCP Server: Exposing Tools to the LLM](#mcp-server-exposing-tools-to-the-llm)
  - [MCP Client: Express Integration](#mcp-client-express-integration)
  - [Transport Modes: stdio and SSE](#transport-modes-stdio-and-sse)
  - [Defining MCP Tools with Zod](#defining-mcp-tools-with-zod)
  - [Running MCP Alongside Express](#running-mcp-alongside-express)
  - [LLM Reasoning Workflow](#llm-reasoning-workflow)
  - [Configure MCP Environment in VS Code](#configure-mcp-environment-in-vs-code)
  - [Connecting LLMs to Your MCP Server](#connecting-llms-to-your-mcp-server)
- [Model Context Protocol (MCP)](#model-context-protocol-mcp)
  - [What is MCP?](#what-is-mcp)
  - [MCP Architecture](#mcp-architecture)
  - [TypeScript SDK](#typescript-sdk)
  - [Add MCP Server to Your Web App](#add-mcp-server-to-your-web-app)
  - [MCP Transport Protocols](#mcp-transport-protocols)
  - [Deploy to Azure Functions](#deploy-to-azure-functions)
  - [Deploy to Azure Container Apps](#deploy-to-azure-container-apps)
  - [Security Considerations for MCP](#security-considerations-for-mcp)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [References](#references)

## Overview

This directory contains implementations demonstrating JavaScript development patterns using Node.js ecosystem tools. The projects showcase different approaches to building web applications, from traditional server-side rendering to modern JAMstack architectures with LLM integration capabilities.

## Node.js

**Node.js** is a JavaScript runtime environment that allows developers to execute JavaScript code outside of a web browser. Built on Chrome's V8 JavaScript engine, Node.js enables server-side programming and provides the foundation for modern full-stack JavaScript development.

### Capabilities

Node.js enables the creation of:

- **Web servers and REST APIs** - HTTP servers and RESTful services
- **Backend services** - Database interactions, authentication, business logic
- **Real-time applications** - Chat applications, live updates, WebSocket connections
- **Command-line tools** - Build tools, deployment scripts, automation
- **Microservices** - Scalable, distributed application architectures

### Core Features

```javascript
// Example: Simple HTTP server with Node.js
const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end('<h1>Hello from Node.js Server!</h1>');
});

server.listen(3000, () => {
  console.log('Server running at http://localhost:3000/');
});
```

## Next.js and Server-Side Rendering

**Next.js** is a React framework for building full-stack web applications that leverages Node.js for its server-side features. It provides a solution for modern web development with built-in optimizations and performance enhancements.

### Server-Side Rendering (SSR)

SSR renders React components on the server before sending them to the client, providing several advantages:

- **Improved SEO** - Search engines can crawl fully rendered HTML
- **Faster Initial Load** - Users see content immediately
- **Better Performance** - Reduced client-side JavaScript processing
- **Enhanced Accessibility** - Works without JavaScript enabled

### Core Next.js Features

#### 1. Server-Side Rendering (SSR)
```javascript
// pages/products/[id].js
export async function getServerSideProps(context) {
  const { id } = context.params;
  const product = await fetchProduct(id);
  
  return {
    props: { product }
  };
}

export default function Product({ product }) {
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
    </div>
  );
}
```

#### 2. Static Site Generation (SSG)
```javascript
// pages/blog/[slug].js
export async function getStaticProps({ params }) {
  const post = await getPost(params.slug);
  
  return {
    props: { post },
    revalidate: 60 // Regenerate page every 60 seconds
  };
}

export async function getStaticPaths() {
  const posts = await getAllPosts();
  
  return {
    paths: posts.map(post => ({ params: { slug: post.slug } })),
    fallback: 'blocking'
  };
}
```

#### 3. API Routes
```javascript
// pages/api/hello.js
export default function handler(req, res) {
  res.status(200).json({
    name: 'John Doe',
    message: 'Hello from Next.js API!'
  });
}
```

### Node.js as the Runtime Environment

Next.js applications run on Node.js, which provides:

- **JavaScript Runtime** - Executes both client-side and server-side code
- **Build Process** - Compiles and optimizes React components
- **Server Environment** - Handles SSR, API routes, and static generation
- **Development Tools** - Hot reload, debugging, and development server

## Express.js Backend Development

**Express.js** is a minimal and flexible Node.js web application framework that provides robust features for building web and mobile applications. It's ideal for creating RESTful APIs and handling complex backend logic.

### Express.js vs Next.js API Routes

| Aspect | Express.js | Next.js API Routes |
|--------|------------|-------------------|
| **Use Case** | Complex backend services | Frontend-focused APIs |
| **Scalability** | Highly scalable | Limited to app scope |
| **Database Integration** | Full ORM/ODM support | Suitable for simple queries |
| **Middleware** | Extensive ecosystem | Built-in Next.js features |
| **Authentication** | Complex auth strategies | Simple auth solutions |

### Express.js Example

```javascript
// server.js
const express = require('express');
const cors = require('cors');
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/api/users', async (req, res) => {
  try {
    const users = await getUsersFromDB();
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/users', async (req, res) => {
  try {
    const newUser = await createUser(req.body);
    res.status(201).json(newUser);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Express server running on port ${PORT}`);
});
```

## Vite Frontend Tooling

**Vite** (pronounced "veet") is a next-generation frontend build tool that provides an extremely fast development experience for modern web projects.

### Key Features

- **Lightning-fast cold server start** - Instant development server startup
- **Hot Module Replacement (HMR)** - Real-time updates without page refresh
- **Optimized builds** - Efficient production bundling with Rollup
- **Framework agnostic** - Works with React, Vue, Svelte, and vanilla JS

### Vite Configuration Example

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
});
```

### How Vite and Node.js Work Together?

#### Development Workflow
1. **Frontend Development** - Use Vite for rapid React/Vue development
2. **Backend Development** - Run Node.js/Express server for API endpoints
3. **Proxy Configuration** - Vite proxies API calls to Node.js backend
4. **Hot Reload** - Both frontend and backend support live reloading

#### Production Deployment
```bash
# Build frontend with Vite
npm run build

# Serve built files with Express
app.use(express.static('dist'));
```

## Full-Stack Integration

### Architecture Patterns

#### 1. Next.js Full-Stack Application
```
┌─────────────────────┐
│     Next.js App     │
│  ┌───────────────┐  │
│  │   Frontend    │  │  React Components
│  │   (React)     │  │  Pages & Routing
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │  API Routes   │  │  Backend Logic
│  │  (Node.js)    │  │  Database Access
│  └───────────────┘  │
└─────────────────────┘
```

#### 2. Separated Frontend/Backend Architecture
```
┌─────────────────┐    ┌─────────────────┐
│  Vite Frontend  │    │ Express Backend │
│     (React)     │────│   (Node.js)     │
│                 │API │                 │
│  - Components   │    │  - REST APIs    │
│  - Routing      │    │  - Database     │
│  - State Mgmt   │    │  - Auth Logic   │
└─────────────────┘    └─────────────────┘
```

### Integration Examples

#### Next.js with External API
```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/external/:path*',
        destination: 'http://localhost:5000/api/:path*'
      }
    ];
  }
};

// pages/users.js
export async function getServerSideProps() {
  const res = await fetch('http://localhost:5000/api/users');
  const users = await res.json();
  
  return { props: { users } };
}
```

#### Vite + Express Development Setup
```json
{
  "scripts": {
    "dev": "concurrently \"npm run server\" \"npm run client\"",
    "server": "nodemon server/index.js",
    "client": "vite",
    "build": "vite build",
    "start": "node server/index.js"
  }
}
```

## LLM Integration with Node.js

Node.js provides excellent capabilities for integrating Large Language Models (LLMs) into web applications, supporting both local and cloud-based inference.

### Interacting with LLM APIs

Node.js excels at making HTTP requests to LLM services with its asynchronous nature:

```javascript
const axios = require('axios');

async function callOpenAI(prompt) {
  try {
    const response = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });
    
    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('OpenAI API error:', error.message);
    throw error;
  }
}
```

### Local LLM Inference with Ollama

Ollama provides local LLM inference capabilities that integrate seamlessly with Node.js:

```javascript
const axios = require('axios');

async function getLlmResponse(prompt) {
  try {
    const response = await axios.post('http://localhost:11434/api/chat', {
      model: 'llama3', // Or your chosen model
      messages: [{ role: 'user', content: prompt }],
      stream: false // Set to true for streaming responses
    });
    return response.data;
  } catch (error) {
    console.error('Error interacting with Ollama:', error.message);
    throw error;
  }
}

// Example usage
getLlmResponse("Tell me a short story about a brave knight.")
  .then(data => {
    console.log(data.message.content);
  })
  .catch(err => {
    console.error('Failed to get LLM response.');
  });
```

### Server-side LLM Inference in Next.js

```javascript
// pages/api/chat.js
import axios from 'axios';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const { message } = req.body;
  
  try {
    const response = await axios.post('http://localhost:11434/api/chat', {
      model: 'llama3',
      messages: [{ role: 'user', content: message }],
      stream: false
    });
    
    res.status(200).json({
      reply: response.data.message.content
    });
  } catch (error) {
    res.status(500).json({
      error: 'Failed to get AI response'
    });
  }
}
```

### Model Context Protocol (MCP) Integration

The Model Context Protocol provides a standardized way to connect LLMs to external tools and data sources. See the dedicated [Model Context Protocol (MCP)](#model-context-protocol-mcp) section for full documentation.

## LLMs Interaction with MCP and Express

Integrating Node.js Express with the Model Context Protocol (MCP) and Large Language Models (LLMs) allows models like GPT or Claude to interact directly with your application's internal tools and data. The LLM selects tools provided by the MCP server — such as database queries, API calls, or custom functions — based on user intent, returning actionable results through an Express endpoint.

You can build your own MCP server in Node.js/TypeScript to expose your Express routes as tools or resources that an LLM can discover and execute. The LLM sends a request to the MCP server, which then makes an internal function call or a local HTTP request to your Express routes to retrieve data.

### Core Components

Three components work together to connect an LLM to your Express backend:

| Component | Role |
|---|---|
| **Express.js** | Acts as your backend API where business logic, database queries, and data processing live |
| **MCP Server** | A wrapper using `@modelcontextprotocol/sdk` that defines and exposes tools (functions) to the LLM |
| **LLM (AI Client)** | An AI assistant (like GPT or Claude) that connects to your MCP server to fetch context or trigger actions |

```
┌─────────────────────────────────────────────────┐
│                   User Input                    │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         Express Client (REST Endpoint)          │
│  - Receives user prompt                         │
│  - Fetches available MCP tools                  │
│  - Sends prompt + tools to the LLM              │
│  - Interprets tool_call responses               │
│  - Executes tools on the MCP server             │
└──────────────┬───────────────────┬──────────────┘
               │                   │
               ▼                   ▼
┌──────────────────────┐  ┌──────────────────────┐
│   LLM (GPT/Claude)   │  │     MCP Server       │
│                      │  │     (Node.js)        │
│  - Evaluates user    │  │  - Exposes tools     │
│    intent            │  │  - Defines Zod       │
│  - Selects tools     │  │    schemas           │
│  - Parses outputs    │  │  - Calls Express     │
│  - Returns response  │  │    routes internally │
└──────────────────────┘  └──────────────────────┘
```

### MCP Server: Exposing Tools to the LLM

The MCP Server acts as a mediator between the LLM and your application. It exposes **tools** (functions) that the LLM can invoke, with input schemas validated using [Zod](https://github.com/colinhacks/zod) so the LLM knows exactly what parameters to send.

In a dedicated file (e.g., `mcp-server.ts`), define tools that correspond to your Express endpoints or internal business logic:

```typescript
// mcp-server.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export const mcpServer = new McpServer({
  name: "ExpressAppMCPServer",
  version: "1.0.0",
});

// Tool: query the database via an internal function
mcpServer.tool(
  "get_product",
  "Retrieve a product by its ID from the database.",
  { productId: z.string().describe("The unique identifier of the product") },
  async ({ productId }) => {
    const product = await getProductFromDB(productId);
    return {
      content: [{ type: "text", text: JSON.stringify(product) }],
    };
  }
);

// Tool: call an external API
mcpServer.tool(
  "get_weather",
  "Fetch current weather for a given city.",
  { city: z.string().describe("The city name") },
  async ({ city }) => {
    const weather = await fetchWeatherAPI(city);
    return {
      content: [{ type: "text", text: JSON.stringify(weather) }],
    };
  }
);
```

### MCP Client: Express Integration

The Express side acts as the **MCP client**. It receives user input, sends it to the LLM along with the list of available MCP tools, interprets any `tool_call` responses from the LLM, executes those tools on the MCP server, and returns the final answer to the user.

```typescript
// routes/chat.ts
import express from "express";
import OpenAI from "openai";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const router = express.Router();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Connect MCP client to the MCP server
const mcpClient = new Client({ name: "express-client", version: "1.0.0" });
const transport = new StreamableHTTPClientTransport(
  new URL("http://localhost:3001/mcp")
);
await mcpClient.connect(transport);

router.post("/chat", async (req, res) => {
  const { message } = req.body;

  // Step 1: Fetch the list of available MCP tools
  const { tools } = await mcpClient.listTools();
  const openAITools = tools.map((tool) => ({
    type: "function" as const,
    function: {
      name: tool.name,
      description: tool.description,
      parameters: tool.inputSchema,
    },
  }));

  // Step 2: Send user message and tools to the LLM
  const messages: OpenAI.Chat.ChatCompletionMessageParam[] = [
    { role: "user", content: message },
  ];
  let response = await openai.chat.completions.create({
    model: "gpt-4o",
    messages,
    tools: openAITools,
    tool_choice: "auto",
  });

  let choice = response.choices[0];

  // Step 3: Handle tool calls until the LLM produces a final answer
  while (choice.finish_reason === "tool_calls") {
    const toolCall = choice.message.tool_calls![0];
    const toolArgs = JSON.parse(toolCall.function.arguments);

    // Step 4: Execute the tool on the MCP server
    const toolResult = await mcpClient.callTool({
      name: toolCall.function.name,
      arguments: toolArgs,
    });

    // Step 5: Feed the tool result back to the LLM
    messages.push(choice.message);
    messages.push({
      role: "tool",
      tool_call_id: toolCall.id,
      content: JSON.stringify(toolResult.content),
    });

    response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages,
      tools: openAITools,
      tool_choice: "auto",
    });
    choice = response.choices[0];
  }

  res.json({ reply: choice.message.content });
});

export default router;
```

### Transport Modes: stdio and SSE

MCP supports two primary transport modes for connecting the client to the server. Choose the mode that matches your deployment environment:

| Transport | Best For | Notes |
|---|---|---|
| **Standard I/O (stdio)** | Local development, desktop AI agents | Parent process communicates via stdin/stdout |
| **Streaming HTTP / SSE** | Production web services | Mount on an Express route; supports remote LLMs |

#### Standard I/O (stdio)

Best for **local development** and **desktop AI agents** such as Cursor or Claude Desktop. The AI client starts your Node.js process and communicates through standard input/output:

```typescript
// server.ts — stdio transport
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { mcpServer } from "./mcp-server.js";

const transport = new StdioServerTransport();
await mcpServer.connect(transport);
// No HTTP port needed — the parent process communicates via stdin/stdout
```

Configure Claude Desktop by editing its config file:

```json
{
  "mcpServers": {
    "my-express-app": {
      "command": "node",
      "args": ["/path/to/your/server.js"]
    }
  }
}
```

#### Streaming HTTP / Server-Sent Events (SSE)

Ideal for **production web services**. Mount the MCP handler directly onto an Express route so remote LLMs can call your tools via HTTP. Use `@modelcontextprotocol/sdk/server/streamableHttp.js` (recommended) or `@modelcontextprotocol/sdk/server/sse.js` for legacy SSE clients:

```typescript
// server.ts — Streaming HTTP transport (recommended for production)
import express from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { mcpServer } from "./mcp-server.js";

const app = express();
app.use(express.json());

const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });

// Mount the /mcp endpoint
app.post("/mcp", async (req, res) => { await transport.handleRequest(req, res, req.body); });
app.get("/mcp",  async (req, res) => { await transport.handleRequest(req, res); });
app.delete("/mcp", async (req, res) => { await transport.handleRequest(req, res); });

await mcpServer.connect(transport);
app.listen(3001, () => console.log("MCP Server on http://localhost:3001/mcp"));
```

### Defining MCP Tools with Zod

Zod schemas give the LLM precise knowledge of what inputs each tool expects. Define schemas in the MCP server so the model never sends malformed parameters:

```typescript
import { z } from "zod";

// Simple string input
mcpServer.tool(
  "search_products",
  "Search the product catalog by keyword.",
  { query: z.string().min(1).describe("The search keyword") },
  async ({ query }) => { /* ... */ }
);

// Complex object with nested array
mcpServer.tool(
  "create_order",
  "Create a new order for a customer.",
  {
    customerId: z.string().uuid().describe("Customer UUID"),
    items: z
      .array(
        z.object({
          productId: z.string(),
          quantity: z.number().int().positive(),
        })
      )
      .describe("List of order line items"),
    shippingAddress: z.string().describe("Full shipping address"),
  },
  async ({ customerId, items, shippingAddress }) => { /* ... */ }
);
```

### Running MCP Alongside Express

You can run your MCP server on a **separate port** alongside your main Express API, or **combine both on a single Express instance** using separate route prefixes.

#### Separate Ports

```typescript
// index.ts — start both servers independently
import { expressApp } from "./api-server.js";    // Main Express API (port 3000)
import { mcpExpressApp } from "./mcp-server.js"; // MCP endpoint    (port 3001)

expressApp.listen(3000, () => console.log("Express API on :3000"));
mcpExpressApp.listen(3001, () => console.log("MCP Server on :3001"));
```

#### Combined Single Server

```typescript
// server.ts — single Express app for both API and MCP
import express from "express";
import { apiRouter } from "./routes/api.js";
import { mcpServer } from "./mcp-server.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

const app = express();
app.use(express.json());

// Regular Express API routes
app.use("/api", apiRouter);

// MCP protocol endpoint
const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
app.post("/mcp",   (req, res) => transport.handleRequest(req, res, req.body));
app.get("/mcp",    (req, res) => transport.handleRequest(req, res));
app.delete("/mcp", (req, res) => transport.handleRequest(req, res));

await mcpServer.connect(transport);
app.listen(3000, () => console.log("Combined server on :3000"));
```

The MCP server tools can internally call your Express routes or shared service functions, keeping business logic in one place while exposing it to the LLM through the protocol.

### LLM Reasoning Workflow

The following sequence describes how the LLM evaluates user intent, selects a tool, and produces a final response:

```
User: "What is the weather in Paris?"
         │
         ▼
┌──────────────────────────────┐
│  Express /chat endpoint      │
│  1. Receives user prompt     │
│  2. Fetches tool list        │
│     from MCP server          │
└──────────────┬───────────────┘
               │ prompt + tool definitions
               ▼
┌──────────────────────────────┐
│     LLM (GPT / Claude)       │
│  3. Evaluates user intent    │
│  4. Decides to call          │
│     get_weather("Paris")     │
└──────────────┬───────────────┘
               │ tool_call: get_weather
               ▼
┌──────────────────────────────┐
│      MCP Server              │
│  5. Executes get_weather     │
│  6. Returns JSON result      │
└──────────────┬───────────────┘
               │ tool result
               ▼
┌──────────────────────────────┐
│     LLM (GPT / Claude)       │
│  7. Parses tool output       │
│  8. Generates final          │
│     structured response      │
└──────────────┬───────────────┘
               │
               ▼
  "The weather in Paris is 18°C and partly cloudy."
```

Key reasoning steps:

1. The LLM receives the user prompt and the list of available MCP tools.
2. If the LLM decides to use `get_weather`, it sends a `tool_call` request back to the Express client.
3. The Express client executes the `get_weather` tool on the MCP server and passes the output back to the LLM.
4. The LLM uses the tool output to generate a final, structured response.

### Configure MCP Environment in VS Code

Add your MCP server to VS Code so that GitHub Copilot and other MCP-compatible extensions can discover and use your Express tools. Create a `.vscode/mcp.json` file in your project root:

```json
{
  "servers": {
    "express-mcp": {
      "type": "http",
      "url": "http://localhost:3001/mcp"
    }
  }
}
```

For a stdio-based local server, use the `stdio` type:

```json
{
  "servers": {
    "express-mcp-local": {
      "type": "stdio",
      "command": "node",
      "args": ["dist/server.js"],
      "env": {
        "DATABASE_URL": "${env:DATABASE_URL}"
      }
    }
  }
}
```

Open Copilot Chat in **Agent mode** and your tools will be automatically discovered. The LLM can then call `get_product`, `get_weather`, or any tool you registered in your MCP server directly from the chat interface.

### Connecting LLMs to Your MCP Server

#### Local Connection (Claude Desktop or Cursor)

Point your AI agent to your local Node.js MCP server by editing the agent's configuration file.

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "my-express-app": {
      "command": "node",
      "args": ["/path/to/your/server.js"]
    }
  }
}
```

**Cursor** (`.cursor/mcp.json` in your project root):

```json
{
  "mcpServers": {
    "my-express-app": {
      "command": "node",
      "args": ["dist/server.js"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

#### Remote Connection

Point an MCP-compatible agent to your deployed Express server's URL. For a server hosted on Azure Container Apps or any cloud provider, update `.vscode/mcp.json`:

```json
{
  "servers": {
    "express-mcp-remote": {
      "type": "http",
      "url": "https://your-app.azurecontainerapps.io/mcp"
    }
  }
}
```

For OpenAI-based clients, connect to a remote MCP server programmatically:

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const mcpClient = new Client({ name: "remote-client", version: "1.0.0" });
const transport = new StreamableHTTPClientTransport(
  new URL("https://your-app.azurecontainerapps.io/mcp")
);
await mcpClient.connect(transport);

// List available tools and pass them to the LLM
const { tools } = await mcpClient.listTools();
```

## Model Context Protocol (MCP)

**Model Context Protocol (MCP)** is an open-source standard for connecting AI applications to external systems. Using MCP, AI applications like Claude or ChatGPT can connect to data sources (local files, databases), tools (search engines, calculators), and workflows — enabling them to access key information and perform tasks on behalf of users.

Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect electronic devices, MCP provides a standardized way to connect AI applications to external systems.

### What is MCP?

MCP defines a client-server architecture where:

- **MCP Host** — An AI application (e.g., Claude, GitHub Copilot, ChatGPT) that initiates connections to MCP servers.
- **MCP Server** — A lightweight program that exposes capabilities (tools, resources, prompts) to the host through the standard protocol.
- **MCP Client** — The protocol layer inside the host that maintains a 1:1 connection with an MCP server.

MCP matters because it:

- **Reduces development complexity** when building or integrating AI applications.
- **Provides a broad ecosystem** of data sources, tools, and apps that enhance AI agent capabilities.
- **Is model-agnostic** — works with any LLM that supports the protocol, including models from Anthropic, OpenAI, and others.
- **Has broad ecosystem support** — backed by Claude, ChatGPT, Visual Studio Code, Cursor, and many other tools.

### MCP Architecture

```
┌────────────────────────────────────────────────┐
│                   MCP Host                     │
│  (Claude / GitHub Copilot / Custom AI Agent)   │
│  ┌─────────────┐    ┌─────────────┐            │
│  │ MCP Client  │    │ MCP Client  │  ...       │
│  └──────┬──────┘    └──────┬──────┘            │
└─────────┼─────────────────┼────────────────────┘
          │  MCP Protocol   │  MCP Protocol
          ▼                 ▼
  ┌──────────────┐  ┌──────────────┐
  │  MCP Server  │  │  MCP Server  │
  │  (Node.js /  │  │  (Node.js /  │
  │   Express)   │  │   Azure Fn.) │
  └──────┬───────┘  └──────┬───────┘
         │                 │
  ┌──────▼───────┐  ┌──────▼───────┐
  │  Data Source │  │  External    │
  │  / Tools     │  │  APIs        │
  └──────────────┘  └──────────────┘
```

MCP servers expose three types of capabilities:

| Capability | Description | Example |
|---|---|---|
| **Tools** | Functions the LLM can invoke | `get_weather`, `query_database` |
| **Resources** | Data the LLM can read | Files, database records, API responses |
| **Prompts** | Reusable prompt templates | Guided workflows, structured interactions |

### TypeScript SDK

The official [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) provides everything needed to build MCP servers and clients in Node.js:

```bash
npm install @modelcontextprotocol/sdk
```

Key classes provided by the SDK:

- `McpServer` — High-level server class with `tool()`, `resource()`, and `prompt()` registration methods.
- `StreamableHTTPServerTransport` — Transport layer for HTTP-based MCP servers (recommended for remote servers).
- `StdioServerTransport` — Transport layer for local process-based MCP servers.

### Add MCP Server to Your Web App

The most common pattern is integrating an MCP server into an Express.js application. This exposes your backend capabilities as MCP tools that any MCP-compatible AI agent can discover and call.

#### Installation

```bash
npm install @modelcontextprotocol/sdk express zod
npm install -D typescript @types/node @types/express tsx
```

#### Basic MCP Server with Express

```typescript
import express from 'express';
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createExpressHandler } from "@modelcontextprotocol/express";
import { z } from "zod";

const app = express();
const mcpServer = new McpServer({
  name: "MyExpressMCPServer",
  version: "1.0.0"
});

// Register a tool (e.g., a calculator or data fetcher)
mcpServer.tool("echo", 
  { message: z.string() }, 
  async ({ message }) => ({
    content: [{ type: "text", text: `You said: ${message}` }]
  })
);

// Add the MCP handler to your Express app
app.use("/api/mcp", createExpressHandler(mcpServer));

app.listen(3000, () => console.log("MCP Server running on http://localhost:3000/api/mcp"));
```

#### Full MCP Server with StreamableHTTP Transport

For production use, the `StreamableHTTPServerTransport` is recommended. It runs in stateless mode (one transport instance per request) and supports HTTP Streaming — the standard for remote MCP servers:

```typescript
import express, { Request, Response } from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

const app = express();
app.use(express.json());

const mcpServer = new McpServer({
    name: "TasksMCP",
    version: "1.0.0",
});

// Register tools using Zod schemas for input validation
mcpServer.tool(
    "list_tasks",
    "List all tasks with their ID, title, and completion status.",
    {},
    async () => ({
        content: [{ type: "text", text: JSON.stringify(await getTasks()) }],
    })
);

mcpServer.tool(
    "create_task",
    "Create a new task with the given title and description.",
    {
        title: z.string().describe("A short title for the task"),
        description: z.string().describe("A detailed description of the task"),
    },
    async ({ title, description }) => {
        const task = await createTask(title, description);
        return {
            content: [{ type: "text", text: JSON.stringify(task) }],
        };
    }
);

// Health endpoint (required for cloud deployments)
app.get("/health", (_req: Request, res: Response) => {
    res.json({ status: "healthy" });
});

// Mount the MCP streamable HTTP transport
const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });

app.post("/mcp", async (req: Request, res: Response) => {
    await transport.handleRequest(req, res, req.body);
});
app.get("/mcp", async (req: Request, res: Response) => {
    await transport.handleRequest(req, res);
});
app.delete("/mcp", async (req: Request, res: Response) => {
    await transport.handleRequest(req, res);
});

// Connect transport to MCP server
await mcpServer.connect(transport);

const PORT = parseInt(process.env.PORT || "3000", 10);
app.listen(PORT, () => {
    console.log(`MCP server running on http://localhost:${PORT}/mcp`);
});
```

#### Registering the MCP Server with GitHub Copilot

Once your server is running, connect it to GitHub Copilot by adding a `.vscode/mcp.json` to your project:

```json
{
  "servers": {
    "my-mcp-server": {
      "type": "http",
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

Open Copilot Chat in Agent mode — your tools will be automatically discovered and available for use.

### MCP Transport Protocols

MCP supports multiple transport mechanisms depending on deployment context:

| Transport | Use Case | Notes |
|---|---|---|
| **Streamable HTTP** | Remote servers (recommended) | Stateless, scalable, works with Azure Functions and Container Apps |
| **SSE (Server-Sent Events)** | Legacy remote servers | Requires persistent connections, limited scalability |
| **Stdio** | Local process servers | Used by Claude Desktop and local tooling |

The **Streamable HTTP** transport is the recommended choice for Node.js web applications — it is stateless, supports horizontal scaling, and is compatible with all major AI clients.

### Deploy to Azure Functions

Azure Functions is a serverless platform that lets you host an MCP server without managing infrastructure. It automatically scales and you pay only for actual execution time.

**Why Azure Functions for MCP servers?**

- Zero infrastructure management — no servers to maintain.
- Automatic scaling from zero to hundreds of instances.
- Cost-effective — generous free grant (1 million requests/month).
- Built-in monitoring via Application Insights.
- Global distribution across Azure regions.

#### Step 1: Add `host.json` Configuration

Create a `host.json` file at the root of your Node.js MCP project:

```json
{
  "version": "2.0",
  "configurationProfile": "mcp-custom-handler",
  "customHandler": {
    "description": {
      "defaultExecutablePath": "node",
      "arguments": ["dist/server.js"]
    },
    "http": {
      "DefaultAuthorizationLevel": "anonymous"
    },
    "port": "3000"
  }
}
```

The `customHandler` section configures the Azure Functions runtime to run your Node.js MCP server as a custom handler, allowing any HTTP server framework (Express, Fastify, etc.) to work without modification.

#### Step 2: Deploy with Azure Developer CLI

```bash
# Login to Azure
azd auth login

# Provision resources and deploy (one command)
azd up
```

The Azure Developer CLI (`azd`) deploys your MCP server to a production-ready Azure Functions environment. For more details, see the [official guide](https://developer.microsoft.com/blog/host-your-node-js-mcp-server-on-azure-functions-in-3-simple-steps).

### Deploy to Azure Container Apps

For MCP servers that need persistent connections or have specific runtime requirements, Azure Container Apps provides a fully managed container hosting environment.

#### Project Setup

```bash
# Create and initialize project
mkdir tasks-mcp-server && cd tasks-mcp-server
npm init -y

# Install dependencies
npm install @modelcontextprotocol/sdk express zod
npm install -D typescript @types/node @types/express tsx
```

`tsconfig.json` targeting ES2022 with Node16 module resolution:

```json
{
    "compilerOptions": {
        "target": "ES2022",
        "module": "Node16",
        "moduleResolution": "Node16",
        "outDir": "./dist",
        "rootDir": "./src",
        "strict": true,
        "esModuleInterop": true
    },
    "include": ["src/**/*"]
}
```

#### Dockerfile for Container Apps

```dockerfile
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY tsconfig.json .
COPY src/ src/
RUN npm run build

FROM node:20-slim
WORKDIR /app
COPY package*.json .
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist
ENV PORT=8080
EXPOSE 8080
CMD ["node", "dist/index.js"]
```

#### Deploy via Azure CLI

```bash
# Set variables
RESOURCE_GROUP="mcp-tutorial-rg"
LOCATION="eastus"
ENVIRONMENT_NAME="mcp-env"
APP_NAME="tasks-mcp-server-node"

# Create resource group and Container Apps environment
az group create --name $RESOURCE_GROUP --location $LOCATION
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Deploy the container app (builds image in the cloud)
az containerapp up \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --source . \
    --ingress external \
    --target-port 8080

# Configure CORS
az containerapp ingress cors enable \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --allowed-origins "*" \
    --allowed-methods "GET,POST,DELETE,OPTIONS" \
    --allowed-headers "*"

# Keep at least one instance running to avoid cold-start delays
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --min-replicas 1
```

For a full step-by-step walkthrough, see the [Azure Container Apps tutorial](https://learn.microsoft.com/en-us/azure/container-apps/tutorial-mcp-server-nodejs).

#### Connect Deployed Server to GitHub Copilot

```json
{
    "servers": {
        "tasks-mcp-server": {
            "type": "http",
            "url": "https://<your-app-fqdn>/mcp"
        }
    }
}
```

#### Testing Locally with MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector
```

Open the URL in your browser, set the transport type to Streamable HTTP, enter `http://localhost:3000/mcp`, and click Connect. The Tools tab lists all registered tools.

### Security Considerations for MCP

Before deploying an MCP server to production:

- **Authentication** — Secure your server with Microsoft Entra ID or an equivalent identity provider.
- **Input validation** — Zod schemas provide type safety; add business-rule validation for tool parameters.
- **HTTPS** — Azure Container Apps enforces HTTPS by default with automatic TLS certificates.
- **Least privilege** — Expose only the tools your use case requires. Avoid tools that perform destructive operations without confirmation.
- **CORS** — Restrict allowed origins to trusted domains in production (replace wildcard `*`).
- **Prompt injection** — When an LLM calls your MCP server, be aware of [prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) attacks in tool inputs.
- **Logging** — Log MCP tool invocations for auditing. Use Azure Monitor and Log Analytics in cloud deployments.

## Project Structure

The NodeJS directory contains several examples.

```
NodeJS/
├── README.md                 # This document
├── MCP/                      # Model Context Protocol implementation
│   ├── src/
│   │   ├── server/          # MCP server with Ollama integration
│   │   ├── client/          # MCP client implementations
│   │   └── shared/          # Shared utilities and types
│   ├── examples/            # Usage examples
│   ├── docker-compose.yml   # Container orchestration
│   └── README.md            # MCP-specific documentation
├── express-api/             # Express.js backend examples
│   ├── routes/              # API route definitions
│   ├── middleware/          # Custom middleware
│   ├── models/              # Data models
│   └── server.js            # Express server entry point
├── nextjs-app/              # Next.js full-stack application
│   ├── pages/               # Next.js pages and API routes
│   │   ├── api/            # API endpoints
│   │   └── [dynamic].js    # Dynamic routing examples
│   ├── components/          # React components
│   ├── public/              # Static assets
│   └── next.config.js       # Next.js configuration
├── vite-frontend/           # Vite-based frontend
│   ├── src/
│   │   ├── components/      # React/Vue components
│   │   ├── pages/           # Application pages
│   │   └── main.js          # Application entry point
│   ├── public/              # Public assets
│   └── vite.config.js       # Vite configuration
└── fullstack-integration/   # Combined examples
    ├── backend/             # Node.js/Express backend
    ├── frontend/            # React/Vite frontend
    └── shared/              # Shared configurations
```

### Examples

Each subdirectory demonstrates different architectural patterns:

- **MCP/**: Advanced LLM integration with Model Context Protocol
- **express-api/**: Traditional REST API with Express.js
- **nextjs-app/**: Full-stack application with SSR/SSG
- **vite-frontend/**: Modern frontend development workflow
- **fullstack-integration/**: Microservices architecture example

## Deployment

### Vercel

Vercel specializes in frontend development and deployment, particularly for Next.js applications:

```json
{
  "builds": [
    { "src": "package.json", "use": "@vercel/node" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/$1" },
    { "src": "/(.*)", "dest": "/public/$1" }
  ]
}
```

### AWS vs Vercel Comparison

| Feature | Vercel | AWS |
|---------|---------|-----|
| **Specialization** | Frontend/Next.js | Full cloud services |
| **Complexity** | Simple deployment | Complex |
| **Cost** | Free tier generous | Pay-as-you-go |
| **Scalability** | Automatic | Manual configuration |
| **Best For** | JAMstack apps | Enterprise applications |

### Docker

```dockerfile
# Multi-stage build for Node.js application
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS production
WORKDIR /app
COPY --from=base /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package*.json ./
EXPOSE 3000
CMD ["npm", "start"]
```

## Best Practices

### Performance Optimization

1. **Code Splitting**: Use dynamic imports and lazy loading
2. **Image Optimization**: Leverage Next.js Image component or Vite plugins
3. **Caching Strategies**: Implement proper HTTP caching headers
4. **Bundle Analysis**: Regular bundle size monitoring

### Development Workflow

1. **TypeScript**: Use TypeScript for better development experience
2. **ESLint/Prettier**: Consistent code formatting and linting
3. **Testing**: Unit and integration testing with Jest/Vitest
4. **CI/CD**: Automated testing and deployment pipelines

### Security Considerations

1. **Environment Variables**: Secure API keys and configuration
2. **CORS**: Proper cross-origin resource sharing configuration
3. **Rate Limiting**: Protect APIs from abuse
4. **Input Validation**: Sanitize and validate all user inputs

## References

### Official Documentation
- [Next.js Documentation](https://nextjs.org/docs) - Complete Next.js guide and API reference
- [Next.js and React](https://nextjs.org/) - Getting started with Next.js
- [Node.js Documentation](https://nodejs.org/docs/) - Official Node.js documentation
- [Express.js Guide](https://expressjs.com/) - Express.js framework documentation
- [Vite Documentation](https://vitejs.dev/) - Vite build tool documentation

### Deployment Platforms
- [Vercel Documentation](https://vercel.com/docs) - Vercel deployment platform
- [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite) - Deploying Vite applications
- [Vue, Vite, and Tailwind on Vercel](https://my-vite-project.vercel.app/) - Example deployment

### LLM Integration Resources
- [Ollama GitHub Repository](https://github.com/ollama/ollama) - Local LLM inference
- [Hugging Face Transformers.js for Node.js](https://huggingface.co/docs/transformers.js/en/tutorials/node) - Server-side ML inference
- [LlamaNode Library](https://llama-node.vercel.app/) - Node.js library for large language models

### Model Context Protocol (MCP)
- [MCP Introduction](https://modelcontextprotocol.io/docs/getting-started/intro) - What is the Model Context Protocol
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) - Official TypeScript SDK for building MCP servers and clients
- [Host Node.js MCP Server on Azure Functions](https://developer.microsoft.com/blog/host-your-node-js-mcp-server-on-azure-functions-in-3-simple-steps) - Serverless MCP hosting guide
- [Deploy Node.js MCP Server to Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/tutorial-mcp-server-nodejs) - Container-based MCP hosting tutorial
- [Integrate App Service as MCP Server for GitHub Copilot](https://learn.microsoft.com/en-us/azure/app-service/tutorial-ai-model-context-protocol-server-node) - App Service MCP integration

### Advanced Topics
- [AWS vs Vercel Comparison](https://vercel.com/docs/concepts/infrastructure) - Platform selection guide
- [JAMstack Architecture](https://jamstack.org/) - Modern web development architecture

### Community Resources
- [Next.js Examples](https://github.com/vercel/next.js/tree/canary/examples) - Official Next.js examples
- [Awesome Vite](https://github.com/vitejs/awesome-vite) - Curated Vite resources
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices) - Production-ready Node.js guide 