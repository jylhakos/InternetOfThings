const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const LLMService = require('./llm_service');
require('dotenv').config();

// Initialize Express app
const app = express();
const port = process.env.PORT || 3000;

// Initialize LLM service
const llmService = new LLMService();

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(morgan('combined')); // Logging
app.use(express.json({ limit: '10mb' })); // Parse JSON bodies
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded bodies

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'LangChain.js LLM Service',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      'POST /generate': 'Generate LLM response',
      'GET /models': 'Get available models',
      'GET /health': 'Health check'
    },
    timestamp: new Date().toISOString()
  });
});

// Generate LLM response endpoint
app.post('/generate', async (req, res) => {
  try {
    const {
      prompt,
      model,
      temperature = 0.7,
      max_tokens = 1000,
      template_type = 'default',
      template_variables = {}
    } = req.body;

    // Validate required fields
    if (!prompt) {
      return res.status(400).json({
        success: false,
        error: 'Prompt is required'
      });
    }

    console.log(`Processing LLM request: model=${model || 'default'}, template=${template_type}`);

    // Generate response using LLM service
    const result = await llmService.generateResponse(prompt, {
      model,
      temperature,
      maxTokens: max_tokens,
      templateType: template_type,
      templateVariables: template_variables
    });

    // Return response
    if (result.success) {
      res.json(result);
    } else {
      res.status(500).json(result);
    }

  } catch (error) {
    console.error('Error in /generate endpoint:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Get available models endpoint
app.get('/models', async (req, res) => {
  try {
    console.log('Fetching available models...');
    const result = await llmService.getAvailableModels();
    
    if (result.success) {
      res.json(result);
    } else {
      res.status(500).json(result);
    }
  } catch (error) {
    console.error('Error in /models endpoint:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    console.log('Performing health check...');
    const result = await llmService.healthCheck();
    
    const statusCode = result.success ? 200 : 503;
    res.status(statusCode).json(result);
  } catch (error) {
    console.error('Error in /health endpoint:', error);
    res.status(503).json({
      success: false,
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Validate model endpoint
app.get('/models/:modelName/validate', async (req, res) => {
  try {
    const { modelName } = req.params;
    console.log(`Validating model: ${modelName}`);
    
    const isValid = await llmService.validateModel(modelName);
    
    res.json({
      model: modelName,
      valid: isValid,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error in model validation:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// OpenAI-compatible chat completions endpoint (for Open WebUI integration)
app.post('/v1/chat/completions', async (req, res) => {
  try {
    const { messages, model, temperature = 0.7, max_tokens = 1000 } = req.body;

    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({
        error: {
          message: 'Messages array is required and must not be empty',
          type: 'invalid_request_error'
        }
      });
    }

    // Extract the last user message as the prompt
    const lastMessage = messages[messages.length - 1];
    const prompt = lastMessage.content;

    // Build conversation history for context
    const history = messages.slice(0, -1).map(msg => 
      `${msg.role}: ${msg.content}`
    ).join('\n');

    console.log(`OpenAI-compatible request: model=${model || 'default'}`);

    // Generate response
    const result = await llmService.generateResponse(prompt, {
      model,
      temperature,
      maxTokens: max_tokens,
      templateType: history ? 'conversation' : 'default',
      templateVariables: { history }
    });

    if (result.success) {
      // Format response in OpenAI format
      const openAIResponse = {
        id: `chatcmpl-${Date.now()}`,
        object: 'chat.completion',
        created: Math.floor(Date.now() / 1000),
        model: result.model,
        choices: [
          {
            index: 0,
            message: {
              role: 'assistant',
              content: result.response
            },
            finish_reason: 'stop'
          }
        ],
        usage: {
          prompt_tokens: Math.ceil(prompt.length / 4),
          completion_tokens: Math.ceil(result.response.length / 4),
          total_tokens: result.tokens_used
        }
      };

      res.json(openAIResponse);
    } else {
      res.status(500).json({
        error: {
          message: result.error,
          type: 'internal_server_error'
        }
      });
    }

  } catch (error) {
    console.error('Error in OpenAI-compatible endpoint:', error);
    res.status(500).json({
      error: {
        message: error.message,
        type: 'internal_server_error'
      }
    });
  }
});

// OpenAI-compatible models endpoint
app.get('/v1/models', async (req, res) => {
  try {
    const result = await llmService.getAvailableModels();
    
    if (result.success) {
      const openAIModels = {
        object: 'list',
        data: result.models.map(model => ({
          id: model.name,
          object: 'model',
          created: Math.floor(Date.now() / 1000),
          owned_by: 'ollama',
          permission: [],
          root: model.name,
          parent: null
        }))
      };
      
      res.json(openAIModels);
    } else {
      res.status(500).json({
        error: {
          message: result.error,
          type: 'internal_server_error'
        }
      });
    }
  } catch (error) {
    console.error('Error in OpenAI models endpoint:', error);
    res.status(500).json({
      error: {
        message: error.message,
        type: 'internal_server_error'
      }
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
    available_endpoints: {
      'POST /generate': 'Generate LLM response',
      'GET /models': 'Get available models',
      'GET /health': 'Health check',
      'POST /v1/chat/completions': 'OpenAI-compatible chat endpoint',
      'GET /v1/models': 'OpenAI-compatible models endpoint'
    },
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(port, () => {
  console.log(`🚀 LangChain.js LLM Service running on port ${port}`);
  console.log(`📚 API Documentation available at http://localhost:${port}`);
  console.log(`🏥 Health check: http://localhost:${port}/health`);
  console.log(`🤖 OpenAI-compatible endpoint: http://localhost:${port}/v1/chat/completions`);
});

module.exports = app;
