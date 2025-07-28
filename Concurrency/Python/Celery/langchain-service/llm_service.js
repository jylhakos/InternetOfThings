const { Ollama } = require("@langchain/ollama");
const { formatPrompt } = require("./prompt_templates");
require('dotenv').config();

class LLMService {
  constructor() {
    this.ollamaUrl = process.env.OLLAMA_URL || 'http://localhost:11434';
    this.defaultModel = process.env.OLLAMA_MODEL || 'llama3.1';
    this.models = new Map();
    
    console.log(`Initializing LLM Service with Ollama at ${this.ollamaUrl}`);
  }

  /**
   * Get or create Ollama instance for a specific model
   */
  getOllamaInstance(modelName = this.defaultModel) {
    if (!this.models.has(modelName)) {
      const ollama = new Ollama({
        baseUrl: this.ollamaUrl,
        model: modelName,
        temperature: 0.7,
      });
      this.models.set(modelName, ollama);
      console.log(`Created Ollama instance for model: ${modelName}`);
    }
    return this.models.get(modelName);
  }

  /**
   * Generate response from LLM
   */
  async generateResponse(prompt, options = {}) {
    const startTime = Date.now();
    
    try {
      const {
        model = this.defaultModel,
        temperature = 0.7,
        maxTokens = 1000,
        templateType = 'default',
        templateVariables = {}
      } = options;

      console.log(`Generating response with model: ${model}`);
      
      // Format prompt using template if specified
      let formattedPrompt = prompt;
      if (templateType !== 'default' || Object.keys(templateVariables).length > 0) {
        const variables = { question: prompt, ...templateVariables };
        formattedPrompt = await formatPrompt(templateType, variables);
      }

      // Get Ollama instance
      const ollama = this.getOllamaInstance(model);
      
      // Configure model parameters
      ollama.temperature = temperature;
      ollama.numPredict = maxTokens;

      // Generate response
      console.log('Sending request to Ollama...');
      const response = await ollama.invoke(formattedPrompt);
      
      const endTime = Date.now();
      const processingTime = (endTime - startTime) / 1000;

      console.log(`Response generated in ${processingTime}s`);

      return {
        success: true,
        response: response,
        model: model,
        tokens_used: this.estimateTokens(formattedPrompt + response),
        processing_time: processingTime,
        timestamp: new Date().toISOString(),
        prompt_template: templateType
      };

    } catch (error) {
      const endTime = Date.now();
      const processingTime = (endTime - startTime) / 1000;
      
      console.error('Error generating response:', error);
      
      return {
        success: false,
        error: error.message,
        processing_time: processingTime,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Stream response from LLM (for future implementation)
   */
  async streamResponse(prompt, options = {}) {
    // Placeholder for streaming implementation
    // This would use Ollama's streaming capabilities
    throw new Error('Streaming not yet implemented');
  }

  /**
   * Get available models from Ollama
   */
  async getAvailableModels() {
    try {
      // This would typically make a request to Ollama's API to list models
      // For now, return commonly available models
      return {
        success: true,
        models: [
          {
            name: 'llama3.1',
            description: 'Llama 3.1 - General purpose LLM',
            size: '4.7GB'
          },
          {
            name: 'llama3.1:7b',
            description: 'Llama 3.1 7B parameters',
            size: '4.7GB'
          },
          {
            name: 'llama3.1:13b',
            description: 'Llama 3.1 13B parameters',
            size: '7.3GB'
          },
          {
            name: 'codellama',
            description: 'Code Llama - Specialized for code generation',
            size: '3.8GB'
          },
          {
            name: 'mistral',
            description: 'Mistral 7B - Fast and efficient',
            size: '4.1GB'
          }
        ],
        default: this.defaultModel
      };
    } catch (error) {
      console.error('Error getting available models:', error);
      return {
        success: false,
        error: error.message,
        models: []
      };
    }
  }

  /**
   * Health check for the LLM service
   */
  async healthCheck() {
    try {
      console.log('Performing health check...');
      
      // Test connection with a simple prompt
      const testPrompt = "Hello";
      const result = await this.generateResponse(testPrompt, {
        maxTokens: 10,
        temperature: 0.1
      });

      if (result.success) {
        return {
          success: true,
          status: 'healthy',
          ollama_url: this.ollamaUrl,
          default_model: this.defaultModel,
          response_time: result.processing_time,
          timestamp: new Date().toISOString()
        };
      } else {
        return {
          success: false,
          status: 'unhealthy',
          error: result.error,
          timestamp: new Date().toISOString()
        };
      }
    } catch (error) {
      console.error('Health check failed:', error);
      return {
        success: false,
        status: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Estimate token count (rough approximation)
   */
  estimateTokens(text) {
    // Rough estimation: ~4 characters per token
    return Math.ceil(text.length / 4);
  }

  /**
   * Validate model availability
   */
  async validateModel(modelName) {
    try {
      const models = await this.getAvailableModels();
      if (models.success) {
        return models.models.some(model => model.name === modelName);
      }
      return false;
    } catch (error) {
      console.error('Error validating model:', error);
      return false;
    }
  }
}

module.exports = LLMService;
