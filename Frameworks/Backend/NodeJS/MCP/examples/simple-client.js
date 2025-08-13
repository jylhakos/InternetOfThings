#!/usr/bin/env node

/**
 * Simple MCP Client Example
 * 
 * This example demonstrates how to connect to an MCP server and use its tools.
 * It shows basic interaction patterns that can be adapted for different use cases.
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

async function main() {
  console.log('🤖 Simple MCP Client Example');
  console.log('=============================\n');

  // Create MCP client
  const client = new Client({
    name: 'simple-mcp-client',
    version: '1.0.0',
  }, {
    capabilities: {
      sampling: {}
    }
  });

  try {
    // Connect to MCP server (adjust path as needed)
    console.log('🔌 Connecting to MCP server...');
    const transport = new StdioClientTransport({
      command: 'node',
      args: ['../dist/server/index.js']
    });
    
    await client.connect(transport);
    console.log('✅ Connected successfully!\n');

    // List available tools
    console.log('📋 Available tools:');
    const toolsResponse = await client.request({
      method: 'tools/list'
    });
    
    toolsResponse.tools.forEach((tool, index) => {
      console.log(`${index + 1}. ${tool.name}: ${tool.description}`);
    });
    console.log();

    // Example 1: Get system information
    console.log('💻 Getting system information...');
    const systemInfo = await client.request({
      method: 'tools/call',
      params: {
        name: 'get_system_info',
        arguments: {}
      }
    });
    
    console.log('System Info:', systemInfo.content[0].text);
    console.log();

    // Example 2: Generate text with Llama
    console.log('🦙 Generating text with Llama...');
    const textGeneration = await client.request({
      method: 'tools/call',
      params: {
        name: 'llama_generate',
        arguments: {
          prompt: 'Write a haiku about artificial intelligence',
          temperature: 0.8
        }
      }
    });
    
    console.log('Generated text:', textGeneration.content[0].text);
    console.log();

    // Example 3: List available Ollama models
    console.log('📦 Available Ollama models...');
    const models = await client.request({
      method: 'tools/call',
      params: {
        name: 'list_ollama_models',
        arguments: {}
      }
    });
    
    console.log('Models:', models.content[0].text);
    console.log();

    console.log('✨ Example completed successfully!');

  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

// Run the example
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
