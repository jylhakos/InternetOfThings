/**
 * Ollama Client for Llama-3.x Integration
 * 
 * This module provides integration with Ollama to interact with Llama-3.x models
 */

import axios, { AxiosInstance } from 'axios';
import type { 
  OllamaResponse, 
  OllamaGenerateRequest, 
  LlamaConfig 
} from './types.js';

export class OllamaClient {
  private client: AxiosInstance;
  private config: LlamaConfig;

  constructor(config: LlamaConfig) {
    this.config = {
      temperature: 0.7,
      maxTokens: 1000,
      context: 4096,
      ...config
    };

    this.client = axios.create({
      baseURL: this.config.ollamaUrl,
      timeout: 60000, // 60 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      }
    });
  }

  /**
   * Check if Ollama server is running and accessible
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/api/version');
      return response.status === 200;
    } catch (error) {
      console.error('Ollama health check failed:', error);
      return false;
    }
  }

  /**
   * List available models in Ollama
   */
  async listModels(): Promise<string[]> {
    try {
      const response = await this.client.get('/api/tags');
      return response.data.models?.map((model: any) => model.name) || [];
    } catch (error) {
      console.error('Failed to list models:', error);
      return [];
    }
  }

  /**
   * Generate text using Llama-3.x model
   */
  async generate(
    prompt: string, 
    options: Partial<OllamaGenerateRequest> = {}
  ): Promise<string> {
    const request: OllamaGenerateRequest = {
      model: this.config.model,
      prompt,
      options: {
        temperature: this.config.temperature,
        num_ctx: this.config.context,
        num_predict: this.config.maxTokens,
        ...options.options
      },
      stream: false,
      ...options
    };

    try {
      const response = await this.client.post('/api/generate', request);
      const data: OllamaResponse = response.data;
      return data.response || '';
    } catch (error) {
      console.error('Generation failed:', error);
      throw new Error(`Failed to generate response: ${error}`);
    }
  }

  /**
   * Generate text with streaming response
   */
  async *generateStream(
    prompt: string,
    options: Partial<OllamaGenerateRequest> = {}
  ): AsyncGenerator<string, void, unknown> {
    const request: OllamaGenerateRequest = {
      model: this.config.model,
      prompt,
      options: {
        temperature: this.config.temperature,
        num_ctx: this.config.context,
        num_predict: this.config.maxTokens,
        ...options.options
      },
      stream: true,
      ...options
    };

    try {
      const response = await this.client.post('/api/generate', request, {
        responseType: 'stream'
      });

      let buffer = '';
      for await (const chunk of response.data) {
        buffer += chunk.toString();
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data: OllamaResponse = JSON.parse(line);
              if (data.response) {
                yield data.response;
              }
              if (data.done) {
                return;
              }
            } catch (parseError) {
              // Ignore malformed JSON lines
              continue;
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming generation failed:', error);
      throw new Error(`Failed to generate streaming response: ${error}`);
    }
  }

  /**
   * Chat completion with conversation context
   */
  async chatCompletion(
    messages: Array<{role: 'system' | 'user' | 'assistant', content: string}>,
    options: Partial<OllamaGenerateRequest> = {}
  ): Promise<string> {
    // Convert chat messages to a single prompt
    const prompt = messages
      .map(msg => {
        switch (msg.role) {
          case 'system': return `System: ${msg.content}`;
          case 'user': return `Human: ${msg.content}`;
          case 'assistant': return `Assistant: ${msg.content}`;
          default: return msg.content;
        }
      })
      .join('\n\n') + '\n\nAssistant:';

    return await this.generate(prompt, options);
  }

  /**
   * Pull a model if it doesn't exist
   */
  async pullModel(modelName: string): Promise<boolean> {
    try {
      const response = await this.client.post('/api/pull', {
        name: modelName,
        stream: false
      });
      return response.status === 200;
    } catch (error) {
      console.error(`Failed to pull model ${modelName}:`, error);
      return false;
    }
  }

  /**
   * Check if a specific model is available
   */
  async isModelAvailable(modelName: string): Promise<boolean> {
    const models = await this.listModels();
    return models.some(model => model.includes(modelName));
  }

  /**
   * Get model information
   */
  async getModelInfo(modelName: string): Promise<any> {
    try {
      const response = await this.client.post('/api/show', {
        name: modelName
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to get model info for ${modelName}:`, error);
      return null;
    }
  }
}
