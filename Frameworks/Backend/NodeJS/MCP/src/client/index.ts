/**
 * MCP Client Implementation
 * 
 * This module implements the Model Context Protocol client that can connect
 * to MCP servers and interact with Llama-3.x through the server's tools.
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { 
  ListToolsRequestSchema,
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

import { createInterface } from 'readline';
import { logger } from '../shared/logger.js';
import type { McpClientConfig } from '../shared/types.js';

/**
 * Enhanced MCP Client with Interactive Features
 */
export class McpLlamaClient {
  private client: Client;
  private config: McpClientConfig;
  private readline: any;

  constructor(config: McpClientConfig) {
    this.config = config;
    
    this.client = new Client({
      name: 'mcp-llama-client',
      version: '1.0.0',
    }, {
      capabilities: {
        sampling: {}
      }
    });

    this.readline = createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  /**
   * Connect to the MCP server
   */
  async connect(): Promise<void> {
    logger.info(`Connecting to MCP server: ${this.config.serverUrl}`);

    // For now, we'll use stdio transport
    // TODO: Implement HTTP transport based on serverUrl
    const transport = new StdioClientTransport({
      command: 'node',
      args: ['dist/server/index.js']
    });

    await this.client.connect(transport);
    logger.info('✅ Connected to MCP server');
  }

  /**
   * List available tools on the server
   */
  async listTools(): Promise<void> {
    try {
      const response = await this.client.request({
        method: 'tools/list'
      }, ListToolsRequestSchema);

      console.log('\n🔧 Available Tools:');
      console.log('==================');
      
      if (response.tools.length === 0) {
        console.log('No tools available');
        return;
      }

      response.tools.forEach((tool, index) => {
        console.log(`\n${index + 1}. ${tool.name}`);
        console.log(`   Description: ${tool.description}`);
        console.log(`   Schema: ${JSON.stringify(tool.inputSchema, null, 2)}`);
      });
    } catch (error) {
      logger.error('Failed to list tools:', error);
    }
  }

  /**
   * List available resources on the server
   */
  async listResources(): Promise<void> {
    try {
      const response = await this.client.request({
        method: 'resources/list'
      }, ListResourcesRequestSchema);

      console.log('\n📚 Available Resources:');
      console.log('=======================');
      
      if (response.resources.length === 0) {
        console.log('No resources available');
        return;
      }

      response.resources.forEach((resource, index) => {
        console.log(`\n${index + 1}. ${resource.name}`);
        console.log(`   URI: ${resource.uri}`);
        console.log(`   Description: ${resource.description || 'No description'}`);
        console.log(`   MIME Type: ${resource.mimeType || 'Not specified'}`);
      });
    } catch (error) {
      logger.error('Failed to list resources:', error);
    }
  }

  /**
   * List available prompts on the server
   */
  async listPrompts(): Promise<void> {
    try {
      const response = await this.client.request({
        method: 'prompts/list'
      }, ListPromptsRequestSchema);

      console.log('\n💬 Available Prompts:');
      console.log('=====================');
      
      if (response.prompts.length === 0) {
        console.log('No prompts available');
        return;
      }

      response.prompts.forEach((prompt, index) => {
        console.log(`\n${index + 1}. ${prompt.name}`);
        console.log(`   Description: ${prompt.description || 'No description'}`);
        if (prompt.arguments && prompt.arguments.length > 0) {
          console.log('   Arguments:');
          prompt.arguments.forEach(arg => {
            console.log(`     - ${arg.name}: ${arg.description} ${arg.required ? '(required)' : '(optional)'}`);
          });
        }
      });
    } catch (error) {
      logger.error('Failed to list prompts:', error);
    }
  }

  /**
   * Call a specific tool
   */
  async callTool(name: string, args: any): Promise<void> {
    try {
      console.log(`\n🔧 Calling tool: ${name}`);
      console.log(`Arguments: ${JSON.stringify(args, null, 2)}`);

      const response = await this.client.request({
        method: 'tools/call',
        params: {
          name,
          arguments: args
        }
      }, CallToolRequestSchema);

      console.log('\n📤 Tool Response:');
      console.log('=================');
      
      if (response.content && response.content.length > 0) {
        response.content.forEach(content => {
          if (content.type === 'text') {
            console.log(content.text);
          } else {
            console.log('Non-text content:', content);
          }
        });
      } else {
        console.log('No content in response');
      }
    } catch (error) {
      logger.error(`Failed to call tool ${name}:`, error);
      console.log(`❌ Error calling tool: ${error}`);
    }
  }

  /**
   * Read a specific resource
   */
  async readResource(uri: string): Promise<void> {
    try {
      console.log(`\n📚 Reading resource: ${uri}`);

      const response = await this.client.request({
        method: 'resources/read',
        params: { uri }
      }, ReadResourceRequestSchema);

      console.log('\n📄 Resource Content:');
      console.log('====================');
      
      if (response.contents && response.contents.length > 0) {
        response.contents.forEach(content => {
          console.log(`MIME Type: ${content.mimeType || 'Not specified'}`);
          if (content.text) {
            console.log(content.text);
          } else if (content.blob) {
            console.log(`Binary content (${content.blob.length} bytes)`);
          }
        });
      } else {
        console.log('No content in resource');
      }
    } catch (error) {
      logger.error(`Failed to read resource ${uri}:`, error);
      console.log(`❌ Error reading resource: ${error}`);
    }
  }

  /**
   * Get a specific prompt
   */
  async getPrompt(name: string, args: any = {}): Promise<void> {
    try {
      console.log(`\n💬 Getting prompt: ${name}`);
      console.log(`Arguments: ${JSON.stringify(args, null, 2)}`);

      const response = await this.client.request({
        method: 'prompts/get',
        params: {
          name,
          arguments: args
        }
      }, GetPromptRequestSchema);

      console.log('\n📝 Prompt Content:');
      console.log('==================');
      console.log(`Description: ${response.description || 'No description'}`);
      
      if (response.messages && response.messages.length > 0) {
        response.messages.forEach((message, index) => {
          console.log(`\nMessage ${index + 1} (${message.role}):`);
          if (message.content.type === 'text') {
            console.log(message.content.text);
          } else {
            console.log('Non-text content:', message.content);
          }
        });
      }
    } catch (error) {
      logger.error(`Failed to get prompt ${name}:`, error);
      console.log(`❌ Error getting prompt: ${error}`);
    }
  }

  /**
   * Interactive chat with Llama through MCP
   */
  async interactiveChat(): Promise<void> {
    console.log('\n🤖 Interactive Llama Chat via MCP');
    console.log('==================================');
    console.log('Type "exit" to quit, "help" for commands\n');

    const messages: Array<{role: 'system' | 'user' | 'assistant', content: string}> = [{
      role: 'system',
      content: 'You are a helpful AI assistant powered by Llama-3.x with access to various tools and resources through MCP.'
    }];

    while (true) {
      const input = await this.prompt('You: ');
      
      if (input.toLowerCase() === 'exit') {
        console.log('👋 Goodbye!');
        break;
      }

      if (input.toLowerCase() === 'help') {
        this.showHelpMenu();
        continue;
      }

      if (input.toLowerCase() === 'tools') {
        await this.listTools();
        continue;
      }

      if (input.toLowerCase() === 'resources') {
        await this.listResources();
        continue;
      }

      if (input.toLowerCase() === 'prompts') {
        await this.listPrompts();
        continue;
      }

      if (input.startsWith('/')) {
        await this.handleCommand(input);
        continue;
      }

      // Regular chat
      messages.push({ role: 'user', content: input });

      try {
        await this.callTool('llama_chat', { 
          messages,
          temperature: 0.7
        });
      } catch (error) {
        console.log('❌ Error in chat:', error);
      }
    }
  }

  /**
   * Handle special commands
   */
  private async handleCommand(command: string): Promise<void> {
    const parts = command.slice(1).split(' ');
    const cmd = parts[0];
    const args = parts.slice(1);

    switch (cmd) {
      case 'system':
        await this.callTool('get_system_info', {});
        break;

      case 'models':
        await this.callTool('list_ollama_models', {});
        break;

      case 'weather':
        if (args.length === 0) {
          console.log('Usage: /weather <location> [days]');
          break;
        }
        const location = args.join(' ');
        const days = parseInt(args[args.length - 1]) || 1;
        await this.callTool('weather_forecast', { location, days });
        break;

      case 'generate':
        if (args.length === 0) {
          console.log('Usage: /generate <prompt>');
          break;
        }
        const prompt = args.join(' ');
        await this.callTool('llama_generate', { prompt });
        break;

      case 'read':
        if (args.length === 0) {
          console.log('Usage: /read <resource_uri>');
          break;
        }
        await this.readResource(args[0]);
        break;

      case 'ls':
        if (args.length === 0) {
          console.log('Usage: /ls <directory_path>');
          break;
        }
        await this.callTool('file_operations', { operation: 'list', path: args[0] });
        break;

      default:
        console.log(`Unknown command: ${cmd}`);
        this.showHelpMenu();
    }
  }

  /**
   * Show help menu
   */
  private showHelpMenu(): void {
    console.log('\n📖 Available Commands:');
    console.log('======================');
    console.log('help          - Show this help menu');
    console.log('tools         - List available tools');
    console.log('resources     - List available resources');
    console.log('prompts       - List available prompts');
    console.log('exit          - Exit the chat');
    console.log('');
    console.log('Special Commands:');
    console.log('/system       - Get system information');
    console.log('/models       - List Ollama models');
    console.log('/weather <location> [days] - Get weather forecast');
    console.log('/generate <prompt> - Generate text with Llama');
    console.log('/read <uri>   - Read a resource');
    console.log('/ls <path>    - List directory contents');
    console.log('');
  }

  /**
   * Prompt user for input
   */
  private prompt(question: string): Promise<string> {
    return new Promise((resolve) => {
      this.readline.question(question, (answer: string) => {
        resolve(answer.trim());
      });
    });
  }

  /**
   * Run demonstration scenarios
   */
  async runDemo(): Promise<void> {
    console.log('\n🎭 Running MCP Llama Client Demo');
    console.log('=================================\n');

    // Demo 1: List capabilities
    console.log('1️⃣ Listing server capabilities...\n');
    await this.listTools();
    await this.listResources();
    await this.listPrompts();

    // Demo 2: System information
    console.log('\n2️⃣ Getting system information...\n');
    await this.callTool('get_system_info', {});

    // Demo 3: List models
    console.log('\n3️⃣ Listing Ollama models...\n');
    await this.callTool('list_ollama_models', {});

    // Demo 4: Generate text
    console.log('\n4️⃣ Generating text with Llama...\n');
    await this.callTool('llama_generate', {
      prompt: 'Explain the concept of Model Context Protocol in 3 sentences.',
      temperature: 0.7
    });

    // Demo 5: Weather forecast
    console.log('\n5️⃣ Getting weather forecast...\n');
    await this.callTool('weather_forecast', {
      location: 'Helsinki, Finland',
      days: 3
    });

    // Demo 6: Read resources
    console.log('\n6️⃣ Reading server resources...\n');
    await this.readResource('system://info');

    console.log('\n✅ Demo completed!\n');
  }

  /**
   * Cleanup resources
   */
  async cleanup(): Promise<void> {
    this.readline.close();
    // await this.client.close(); // Uncomment when SDK supports this
    logger.info('Client cleanup completed');
  }
}

/**
 * Start the MCP client
 */
export async function startClient(config: McpClientConfig): Promise<void> {
  logger.info('🔌 Starting MCP Llama Client...');
  logger.info(`Configuration:`, config);

  const client = new McpLlamaClient(config);

  try {
    await client.connect();
    logger.info('✅ MCP Client connected successfully');

    if (config.interactive) {
      await client.interactiveChat();
    } else {
      await client.runDemo();
    }
  } catch (error) {
    logger.error('❌ Client failed:', error);
    throw error;
  } finally {
    await client.cleanup();
  }
}
