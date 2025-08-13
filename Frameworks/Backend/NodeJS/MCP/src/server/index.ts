/**
 * MCP Server Implementation
 * 
 * This module implements the Model Context Protocol server using the TypeScript SDK
 * with integration to Llama-3.x via Ollama for enhanced AI capabilities.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import express from 'express';
import type { Request, Response } from 'express';
import { OllamaClient } from '../shared/ollama.js';
import { logger } from '../shared/logger.js';
import type { 
  McpServerConfig, 
  SystemInfo, 
  WeatherData,
  FileSystemInfo,
  LlamaConfig 
} from '../shared/types.js';
import { promises as fs } from 'fs';
import { platform, arch } from 'os';
import process from 'process';

/**
 * Enhanced MCP Server with Llama-3.x Integration
 */
export class McpLlamaServer {
  private server: Server;
  private ollama: OllamaClient;
  private config: McpServerConfig;

  constructor(config: McpServerConfig) {
    this.config = config;
    
    // Initialize MCP Server
    this.server = new Server({
      name: 'mcp-llama-server',
      version: '1.0.0',
    }, {
      capabilities: {
        tools: {},
        resources: {},
        prompts: {},
        logging: {}
      }
    });

    // Initialize Ollama client
    const llamaConfig: LlamaConfig = {
      model: process.env.LLAMA_MODEL || 'llama3.2:latest',
      ollamaUrl: config.ollamaUrl || process.env.OLLAMA_URL || 'http://localhost:11434',
      temperature: 0.7,
      maxTokens: 2000,
      context: 4096
    };

    this.ollama = new OllamaClient(llamaConfig);
    this.setupHandlers();
  }

  /**
   * Setup request handlers for tools, resources, and prompts
   */
  private setupHandlers(): void {
    // Tools handlers
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'llama_generate',
          description: 'Generate text using Llama-3.x model via Ollama',
          inputSchema: {
            type: 'object',
            properties: {
              prompt: {
                type: 'string',
                description: 'The prompt to generate text from'
              },
              temperature: {
                type: 'number',
                description: 'Temperature for generation (0.0 to 1.0)',
                minimum: 0.0,
                maximum: 1.0,
                default: 0.7
              },
              max_tokens: {
                type: 'number',
                description: 'Maximum number of tokens to generate',
                default: 1000
              }
            },
            required: ['prompt']
          }
        },
        {
          name: 'llama_chat',
          description: 'Chat with Llama-3.x using conversation context',
          inputSchema: {
            type: 'object',
            properties: {
              messages: {
                type: 'array',
                description: 'Array of conversation messages',
                items: {
                  type: 'object',
                  properties: {
                    role: {
                      type: 'string',
                      enum: ['system', 'user', 'assistant']
                    },
                    content: {
                      type: 'string'
                    }
                  },
                  required: ['role', 'content']
                }
              },
              temperature: {
                type: 'number',
                minimum: 0.0,
                maximum: 1.0,
                default: 0.7
              }
            },
            required: ['messages']
          }
        },
        {
          name: 'get_system_info',
          description: 'Get current system information',
          inputSchema: {
            type: 'object',
            properties: {},
            additionalProperties: false
          }
        },
        {
          name: 'list_ollama_models',
          description: 'List available models in Ollama',
          inputSchema: {
            type: 'object',
            properties: {},
            additionalProperties: false
          }
        },
        {
          name: 'weather_forecast',
          description: 'Get weather forecast for a location (simulated)',
          inputSchema: {
            type: 'object',
            properties: {
              location: {
                type: 'string',
                description: 'Location to get weather for'
              },
              days: {
                type: 'number',
                description: 'Number of days to forecast',
                default: 1,
                minimum: 1,
                maximum: 7
              }
            },
            required: ['location']
          }
        },
        {
          name: 'file_operations',
          description: 'Perform file system operations',
          inputSchema: {
            type: 'object',
            properties: {
              operation: {
                type: 'string',
                enum: ['list', 'read', 'info'],
                description: 'File operation to perform'
              },
              path: {
                type: 'string',
                description: 'File or directory path'
              }
            },
            required: ['operation', 'path']
          }
        }
      ]
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'llama_generate':
            return await this.handleLlamaGenerate(args);
          
          case 'llama_chat':
            return await this.handleLlamaChat(args);
          
          case 'get_system_info':
            return await this.handleSystemInfo();
          
          case 'list_ollama_models':
            return await this.handleListModels();
          
          case 'weather_forecast':
            return await this.handleWeatherForecast(args);
          
          case 'file_operations':
            return await this.handleFileOperations(args);
          
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        logger.error(`Tool execution failed for ${name}:`, error);
        throw error;
      }
    });

    // Resources handlers
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
      resources: [
        {
          uri: 'system://info',
          name: 'System Information',
          description: 'Current system and server information',
          mimeType: 'application/json'
        },
        {
          uri: 'llama://models',
          name: 'Available Llama Models',
          description: 'List of available Llama models in Ollama',
          mimeType: 'application/json'
        },
        {
          uri: 'config://server',
          name: 'Server Configuration',
          description: 'Current server configuration',
          mimeType: 'application/json'
        }
      ]
    }));

    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;

      switch (uri) {
        case 'system://info': {
          const systemInfo = await this.getSystemInfo();
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(systemInfo, null, 2)
            }]
          };
        }

        case 'llama://models': {
          const models = await this.ollama.listModels();
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify({ models }, null, 2)
            }]
          };
        }

        case 'config://server': {
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(this.config, null, 2)
            }]
          };
        }

        default:
          throw new Error(`Unknown resource: ${uri}`);
      }
    });

    // Prompts handlers
    this.server.setRequestHandler(ListPromptsRequestSchema, async () => ({
      prompts: [
        {
          name: 'llama_system_prompt',
          description: 'System prompt for Llama-3.x with MCP context',
          arguments: [
            {
              name: 'context',
              description: 'Additional context information',
              required: false
            }
          ]
        },
        {
          name: 'code_assistant',
          description: 'Prompt for code assistance and debugging',
          arguments: [
            {
              name: 'language',
              description: 'Programming language',
              required: true
            },
            {
              name: 'task',
              description: 'Specific coding task',
              required: false
            }
          ]
        },
        {
          name: 'data_analyst',
          description: 'Prompt for data analysis tasks',
          arguments: [
            {
              name: 'data_type',
              description: 'Type of data to analyze',
              required: true
            }
          ]
        }
      ]
    }));

    this.server.setRequestHandler(GetPromptRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'llama_system_prompt':
          const context = args?.context || 'general assistance';
          return {
            description: 'System prompt for Llama-3.x with MCP integration',
            messages: [{
              role: 'system' as const,
              content: {
                type: 'text',
                text: `You are an advanced AI assistant powered by Llama-3.x with access to external tools and resources through the Model Context Protocol (MCP). 

You can:
- Generate text and provide detailed responses
- Access system information and resources
- Perform file operations
- Get weather information
- List and work with available AI models

Context: ${context}

When using tools, be specific about what you need and explain your reasoning. Always be helpful, accurate, and considerate of user needs.`
              }
            }]
          };

        case 'code_assistant':
          const language = args?.language || 'general';
          const task = args?.task || 'assistance';
          return {
            description: 'Code assistance prompt',
            messages: [{
              role: 'system' as const,
              content: {
                type: 'text',
                text: `You are an expert ${language} programmer and code assistant. Help with ${task} by providing:

- Clear, well-commented code
- Best practices and patterns
- Error analysis and debugging
- Performance optimization suggestions
- Security considerations

Be thorough but concise, and always explain your reasoning.`
              }
            }]
          };

        case 'data_analyst':
          const dataType = args?.data_type || 'general';
          return {
            description: 'Data analysis prompt',
            messages: [{
              role: 'system' as const,
              content: {
                type: 'text',
                text: `You are a skilled data analyst specializing in ${dataType} data. Provide:

- Clear data insights and patterns
- Statistical analysis and interpretations
- Visualization suggestions
- Actionable recommendations
- Data quality assessments

Focus on practical, business-relevant insights.`
              }
            }]
          };

        default:
          throw new Error(`Unknown prompt: ${name}`);
      }
    });
  }

  /**
   * Tool Handlers
   */
  private async handleLlamaGenerate(args: any) {
    const { prompt, temperature = 0.7, max_tokens = 1000 } = args;
    
    logger.info(`Generating text with Llama: ${prompt.substring(0, 100)}...`);
    
    const response = await this.ollama.generate(prompt, {
      options: {
        temperature,
        num_predict: max_tokens
      }
    });

    return {
      content: [{
        type: 'text',
        text: response
      }]
    };
  }

  private async handleLlamaChat(args: any) {
    const { messages, temperature = 0.7 } = args;
    
    logger.info(`Chat completion with ${messages.length} messages`);
    
    const response = await this.ollama.chatCompletion(messages, {
      options: { temperature }
    });

    return {
      content: [{
        type: 'text',
        text: response
      }]
    };
  }

  private async handleSystemInfo() {
    const systemInfo = await this.getSystemInfo();
    
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(systemInfo, null, 2)
      }]
    };
  }

  private async handleListModels() {
    const models = await this.ollama.listModels();
    
    return {
      content: [{
        type: 'text',
        text: `Available Ollama models:\n${models.map(m => `- ${m}`).join('\n')}`
      }]
    };
  }

  private async handleWeatherForecast(args: any): Promise<any> {
    const { location, days = 1 } = args;
    
    // Simulate weather data (in a real implementation, you'd call a weather API)
    const forecasts: WeatherData[] = [];
    for (let i = 0; i < days; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);
      
      forecasts.push({
        location,
        temperature: Math.round(Math.random() * 30 + 10), // 10-40°C
        description: ['sunny', 'cloudy', 'rainy', 'partly cloudy'][Math.floor(Math.random() * 4)],
        humidity: Math.round(Math.random() * 40 + 40), // 40-80%
        windSpeed: Math.round(Math.random() * 20 + 5), // 5-25 km/h
        timestamp: date.toISOString()
      });
    }
    
    return {
      content: [{
        type: 'text',
        text: `Weather forecast for ${location}:\n\n${forecasts.map(f => 
          `${new Date(f.timestamp).toDateString()}: ${f.temperature}°C, ${f.description}, ${f.humidity}% humidity, ${f.windSpeed} km/h wind`
        ).join('\n')}`
      }]
    };
  }

  private async handleFileOperations(args: any) {
    const { operation, path } = args;
    
    try {
      switch (operation) {
        case 'list':
          const items = await fs.readdir(path, { withFileTypes: true });
          const fileList = items.map(item => ({
            name: item.name,
            type: item.isDirectory() ? 'directory' : 'file'
          }));
          
          return {
            content: [{
              type: 'text',
              text: `Contents of ${path}:\n${fileList.map(f => `${f.type === 'directory' ? '📁' : '📄'} ${f.name}`).join('\n')}`
            }]
          };

        case 'read':
          const content = await fs.readFile(path, 'utf-8');
          return {
            content: [{
              type: 'text',
              text: `File contents of ${path}:\n\n${content}`
            }]
          };

        case 'info':
          const stats = await fs.stat(path);
          const info: FileSystemInfo = {
            path,
            type: stats.isDirectory() ? 'directory' : 'file',
            size: stats.size,
            modified: stats.mtime.toISOString(),
            permissions: stats.mode.toString(8)
          };
          
          return {
            content: [{
              type: 'text',
              text: `File info for ${path}:\n${JSON.stringify(info, null, 2)}`
            }]
          };

        default:
          throw new Error(`Unsupported file operation: ${operation}`);
      }
    } catch (error) {
      throw new Error(`File operation failed: ${error}`);
    }
  }

  /**
   * Helper Methods
   */
  private async getSystemInfo(): Promise<SystemInfo> {
    const memoryUsage = process.memoryUsage();
    
    return {
      timestamp: new Date().toISOString(),
      platform: platform(),
      arch: arch(),
      nodeVersion: process.version,
      memory: {
        total: memoryUsage.heapTotal,
        free: memoryUsage.heapUsed,
        used: memoryUsage.external + memoryUsage.arrayBuffers
      },
      uptime: process.uptime()
    };
  }

  /**
   * Start the server with specified transport
   */
  async start(): Promise<void> {
    // Check Ollama connection
    const isOllamaHealthy = await this.ollama.healthCheck();
    if (!isOllamaHealthy) {
      logger.warn('Ollama server not accessible, some features may be limited');
    }

    switch (this.config.transport) {
      case 'stdio':
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        logger.info('MCP Server running on stdio');
        break;

      case 'streamable-http':
      case 'http':
        await this.startHttpServer();
        break;

      default:
        throw new Error(`Unsupported transport: ${this.config.transport}`);
    }
  }

  private async startHttpServer(): Promise<void> {
    const app = express();
    
    app.use(express.json());
    
    // Health check endpoint
    app.get('/health', (req: Request, res: Response) => {
      res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      });
    });

    // MCP endpoints would be implemented here for HTTP transport
    app.post('/mcp', async (req: Request, res: Response) => {
      try {
        // This would handle MCP-over-HTTP requests
        res.json({ message: 'MCP HTTP transport not fully implemented yet' });
      } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
      }
    });

    app.listen(this.config.port, () => {
      logger.info(`MCP Server listening on port ${this.config.port}`);
      logger.info(`Health check: http://localhost:${this.config.port}/health`);
    });
  }
}

/**
 * Start the MCP server
 */
export async function startServer(config: McpServerConfig): Promise<void> {
  logger.info('🚀 Starting MCP Llama Server...');
  logger.info(`Configuration:`, config);

  const server = new McpLlamaServer(config);
  await server.start();
  
  logger.info('✅ MCP Server started successfully');
}
