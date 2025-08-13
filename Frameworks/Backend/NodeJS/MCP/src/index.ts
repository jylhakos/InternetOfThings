#!/usr/bin/env node

/**
 * MCP Server and Client CLI
 * 
 * This is the main entry point for the MCP (Model Context Protocol) implementation
 * providing both server and client functionality with Llama-3.x integration.
 */

import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Import package.json for version info
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const packageJson = JSON.parse(readFileSync(join(__dirname, '../package.json'), 'utf-8'));

async function main() {
  const argv = await yargs(hideBin(process.argv))
    .version(packageJson.version)
    .command('server', 'Start the MCP server', {
      port: {
        alias: 'p',
        type: 'number',
        default: 3000,
        description: 'Port to run the server on'
      },
      transport: {
        alias: 't',
        type: 'string',
        choices: ['stdio', 'http', 'streamable-http'],
        default: 'streamable-http',
        description: 'Transport protocol to use'
      }
    }, async (args) => {
      console.log('🚀 Starting MCP Server...');
      const { startServer } = await import('./server/index.js');
      await startServer({
        port: args.port,
        transport: args.transport as 'stdio' | 'http' | 'streamable-http'
      });
    })
    .command('client', 'Start the MCP client', {
      server: {
        alias: 's',
        type: 'string',
        default: 'http://localhost:3000/mcp',
        description: 'MCP server URL to connect to'
      },
      interactive: {
        alias: 'i',
        type: 'boolean',
        default: true,
        description: 'Run in interactive mode'
      }
    }, async (args) => {
      console.log('🔌 Starting MCP Client...');
      const { startClient } = await import('./client/index.js');
      await startClient({
        serverUrl: args.server,
        interactive: args.interactive
      });
    })
    .command('demo', 'Run a demonstration of server and client interaction', {
      port: {
        alias: 'p',
        type: 'number',
        default: 3000,
        description: 'Port to run the demo server on'
      }
    }, async (args) => {
      console.log('🎭 Starting MCP Demo...');
      // Start server in background
      const { startServer } = await import('./server/index.js');
      const { startClient } = await import('./client/index.js');
      
      console.log('Starting demo server...');
      startServer({
        port: args.port,
        transport: 'streamable-http'
      });
      
      // Wait a moment for server to start
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      console.log('Starting demo client...');
      await startClient({
        serverUrl: `http://localhost:${args.port}/mcp`,
        interactive: false
      });
    })
    .demandCommand(1, 'Please specify a command')
    .help()
    .alias('h', 'help')
    .example('$0 server --port 3000', 'Start MCP server on port 3000')
    .example('$0 client --server http://localhost:3000/mcp', 'Connect client to MCP server')
    .example('$0 demo', 'Run a complete demonstration')
    .epilog('For more information, visit: https://modelcontextprotocol.io/')
    .parseAsync();

  if (!argv._[0]) {
    console.log('🎯 MCP Node.js Implementation');
    console.log('=====================================');
    console.log(`Version: ${packageJson.version}`);
    console.log('Run with --help for usage information');
  }
}

// Handle uncaught exceptions and rejections
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Gracefully shutting down...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n👋 Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

main().catch((error) => {
  console.error('❌ Application failed to start:', error);
  process.exit(1);
});
