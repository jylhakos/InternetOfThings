/**
 * AI Agent Implementation using LangChain.js
 * Handles greetings, weather queries, and LLM interactions with Ollama
 */

import { ChatOllama } from '@langchain/ollama';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { AgentExecutor, createReactAgent } from 'langchain/agents';
import { pull } from 'langchain/hub';
import express from 'express';
import cors from 'cors';
import { WeatherTool, GreetingTool, LocationTool, ToolManager } from './tools.js';
import 'dotenv/config';

/**
 * AI Agent class using LangChain.js framework
 */
export class LangChainAIAgent {
  constructor(options = {}) {
    this.ollamaBaseUrl = options.ollamaBaseUrl || process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
    this.ollamaModel = options.ollamaModel || process.env.OLLAMA_MODEL || 'llama3.1:8b-instruct-q4_0';
    this.port = options.port || process.env.AGENT_PORT || 8000;
    
    // Initialize LangChain components
    this.initializeLangChain();
    
    // Initialize Express app
    this.app = express();
    this.setupMiddleware();
    this.setupRoutes();
    
    // Track conversations
    this.conversations = new Map();
  }

  /**
   * Initialize LangChain components (LLM, Tools, Agent)
   */
  async initializeLangChain() {
    try {
      // Initialize Ollama LLM
      this.llm = new ChatOllama({
        baseUrl: this.ollamaBaseUrl,
        model: this.ollamaModel,
        temperature: 0.7,
        maxTokens: 512,
        topP: 0.9,
      });

      // Initialize tools
      this.toolManager = new ToolManager();
      this.tools = this.toolManager.getAllTools();

      // Create the agent prompt template
      this.agentPrompt = ChatPromptTemplate.fromTemplate(`
You are a helpful AI assistant powered by LangChain.js and Ollama. You can:

1. 🤖 Handle greetings and friendly conversations
2. 🌤️ Provide weather information for any city worldwide
3. 📍 Give detailed location information with coordinates
4. 💬 Answer general questions and have conversations

Instructions:
- For greetings (hello, hi, good morning, etc.), use the greeting tool to respond warmly
- For weather queries (temperature, weather, forecast), use the weather tool to get current conditions
- For location questions (coordinates, timezone, elevation), use the location tool
- For other questions, provide helpful and informative responses
- Always be friendly, helpful, and conversational
- When using tools, provide clear and formatted responses

Current conversation:
{chat_history}

User: {input}

{agent_scratchpad}
`);

      // Pull the React agent prompt from LangChain Hub (fallback if needed)
      try {
        const hubPrompt = await pull('hwchase17/react');
        this.reactPrompt = hubPrompt;
      } catch (error) {
        console.warn('Could not pull React prompt from hub, using default');
        this.reactPrompt = this.agentPrompt;
      }

      // Create the ReAct agent
      this.agent = await createReactAgent({
        llm: this.llm,
        tools: this.tools,
        prompt: this.reactPrompt,
      });

      // Create agent executor
      this.agentExecutor = new AgentExecutor({
        agent: this.agent,
        tools: this.tools,
        verbose: true,
        maxIterations: 3,
        returnIntermediateSteps: false,
      });

      console.log('✅ LangChain.js AI Agent initialized successfully');
      console.log(`📡 Connected to Ollama: ${this.ollamaBaseUrl}`);
      console.log(`🧠 Using model: ${this.ollamaModel}`);
      console.log(`🛠️ Available tools: ${this.tools.length}`);

    } catch (error) {
      console.error('❌ Error initializing LangChain components:', error);
      throw error;
    }
  }

  /**
   * Setup Express middleware
   */
  setupMiddleware() {
    this.app.use(cors());
    this.app.use(express.json({ limit: '10mb' }));
    
    // Request logging
    this.app.use((req, res, next) => {
      console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
      next();
    });
  }

  /**
   * Setup Express routes
   */
  setupRoutes() {
    // Health check endpoint
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: {
          llm: `${this.ollamaBaseUrl} (${this.ollamaModel})`,
          tools: this.tools.map(tool => tool.name),
          weather_api: 'Open-Meteo API',
          geocoding_api: 'Open-Meteo Geocoding API'
        },
        framework: 'LangChain.js',
        version: '1.0.0'
      });
    });

    // OpenAI-compatible chat completions endpoint
    this.app.post('/v1/chat/completions', async (req, res) => {
      try {
        const { messages, temperature = 0.7, max_tokens = 512 } = req.body;

        if (!messages || !Array.isArray(messages) || messages.length === 0) {
          return res.status(400).json({
            error: {
              message: 'Invalid messages format',
              type: 'invalid_request_error'
            }
          });
        }

        // Get the latest user message
        const userMessage = messages[messages.length - 1]?.content || '';
        
        // Generate session ID from request or create new one
        const sessionId = req.headers['x-session-id'] || `session-${Date.now()}`;

        // Get conversation history
        const chatHistory = this.getConversationHistory(sessionId);

        // Process with LangChain agent
        const result = await this.agentExecutor.invoke({
          input: userMessage,
          chat_history: chatHistory
        });

        // Update conversation history
        this.updateConversationHistory(sessionId, userMessage, result.output);

        // Return OpenAI-compatible response
        res.json({
          id: `chatcmpl-${Date.now()}`,
          object: 'chat.completion',
          created: Math.floor(Date.now() / 1000),
          model: this.ollamaModel,
          choices: [{
            index: 0,
            message: {
              role: 'assistant',
              content: result.output
            },
            finish_reason: 'stop'
          }],
          usage: {
            prompt_tokens: userMessage.length,
            completion_tokens: result.output.length,
            total_tokens: userMessage.length + result.output.length
          }
        });

      } catch (error) {
        console.error('❌ Error processing chat completion:', error);
        res.status(500).json({
          error: {
            message: 'Internal server error',
            type: 'server_error',
            details: error.message
          }
        });
      }
    });

    // Direct agent query endpoint
    this.app.post('/agent/query', async (req, res) => {
      try {
        const { query, session_id } = req.body;

        if (!query) {
          return res.status(400).json({ error: 'Query is required' });
        }

        const sessionId = session_id || `session-${Date.now()}`;
        const chatHistory = this.getConversationHistory(sessionId);

        const result = await this.agentExecutor.invoke({
          input: query,
          chat_history: chatHistory
        });

        this.updateConversationHistory(sessionId, query, result.output);

        res.json({
          response: result.output,
          session_id: sessionId,
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        console.error('❌ Error processing agent query:', error);
        res.status(500).json({
          error: 'Internal server error',
          details: error.message
        });
      }
    });

    // Get conversation history endpoint
    this.app.get('/agent/history/:sessionId', (req, res) => {
      const { sessionId } = req.params;
      const history = this.conversations.get(sessionId) || [];
      
      res.json({
        session_id: sessionId,
        history: history,
        message_count: history.length
      });
    });

    // Clear conversation history endpoint
    this.app.delete('/agent/history/:sessionId', (req, res) => {
      const { sessionId } = req.params;
      this.conversations.delete(sessionId);
      
      res.json({
        message: `Conversation history cleared for session ${sessionId}`
      });
    });

    // List available tools endpoint
    this.app.get('/agent/tools', (req, res) => {
      res.json({
        tools: this.tools.map(tool => ({
          name: tool.name,
          description: tool.description,
          schema: tool.schema
        }))
      });
    });
  }

  /**
   * Get conversation history for a session
   */
  getConversationHistory(sessionId) {
    const history = this.conversations.get(sessionId) || [];
    return history.map(entry => `Human: ${entry.user}\nAssistant: ${entry.assistant}`).join('\n\n');
  }

  /**
   * Update conversation history
   */
  updateConversationHistory(sessionId, userMessage, assistantResponse) {
    if (!this.conversations.has(sessionId)) {
      this.conversations.set(sessionId, []);
    }
    
    const history = this.conversations.get(sessionId);
    history.push({
      user: userMessage,
      assistant: assistantResponse,
      timestamp: new Date().toISOString()
    });

    // Keep only last 20 exchanges to manage memory
    if (history.length > 20) {
      history.splice(0, history.length - 20);
    }
  }

  /**
   * Start the Express server
   */
  async start() {
    try {
      // Initialize LangChain if not already done
      if (!this.agentExecutor) {
        await this.initializeLangChain();
      }

      // Start server
      this.server = this.app.listen(this.port, () => {
        console.log('\n🚀 LangChain.js AI Agent Server Started!');
        console.log('========================================');
        console.log(`� Server running on: http://localhost:${this.port}`);
        console.log(`🧠 LLM Model: ${this.ollamaModel}`);
        console.log(`🔗 Ollama URL: ${this.ollamaBaseUrl}`);
        console.log(`🛠️ Tools: ${this.tools.length} available`);
        console.log('\n📋 Available Endpoints:');
        console.log(`  • GET  /health - Health check`);
        console.log(`  • POST /v1/chat/completions - OpenAI-compatible chat`);
        console.log(`  • POST /agent/query - Direct agent query`);
        console.log(`  • GET  /agent/history/:sessionId - Get conversation history`);
        console.log(`  • DELETE /agent/history/:sessionId - Clear history`);
        console.log(`  • GET  /agent/tools - List available tools`);
        console.log('\n🎯 Ready to process requests!');
      });

      // Graceful shutdown
      process.on('SIGINT', () => {
        console.log('\n🛑 Shutting down server...');
        this.server.close(() => {
          console.log('✅ Server closed gracefully');
          process.exit(0);
        });
      });

    } catch (error) {
      console.error('❌ Error starting server:', error);
      throw error;
    }
  }
}

/**
 * Example usage and testing functions
 */
export class AgentTester {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Test the agent with various queries
   */
  async runTests() {
    console.log('🧪 Running LangChain.js AI Agent Tests');
    console.log('=====================================');

    const testQueries = [
      'Hello, how are you?',
      'Good morning!',
      'What is the temperature in London?',
      'Tell me about the weather in Tokyo',
      'Where is Paris located?',
      'What are the coordinates of New York?',
      'Tell me about Python programming',
      'How does machine learning work?',
      'Good evening, what can you do?'
    ];

    try {
      // Health check first
      console.log('\n🏥 Health Check...');
      const healthResponse = await fetch(`${this.baseUrl}/health`);
      const health = await healthResponse.json();
      console.log(`Status: ${health.status}`);
      console.log(`Framework: ${health.framework}`);
      console.log(`Tools: ${health.services.tools.join(', ')}`);

      // Test queries
      console.log('\n💬 Testing Queries...');
      const sessionId = `test-session-${Date.now()}`;
      
      for (const query of testQueries) {
        console.log(`\n👤 User: ${query}`);
        
        try {
          const response = await fetch(`${this.baseUrl}/agent/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, session_id: sessionId })
          });

          const result = await response.json();
          const truncatedResponse = result.response.length > 100 
            ? result.response.substring(0, 100) + '...' 
            : result.response;
          console.log(`🤖 Agent: ${truncatedResponse}`);

        } catch (error) {
          console.log(`❌ Error: ${error.message}`);
        }

        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

    } catch (error) {
      console.error('❌ Test Error:', error.message);
      console.log('\n💡 Make sure the AI Agent server is running:');
      console.log('  npm start');
    }
  }
}

// Export the main components
export default LangChainAIAgent;

// If this file is run directly, start the server
if (import.meta.url === `file://${process.argv[1]}`) {
  const agent = new LangChainAIAgent();
  agent.start().catch(error => {
    console.error('Failed to start agent:', error);
    process.exit(1);
  });
}