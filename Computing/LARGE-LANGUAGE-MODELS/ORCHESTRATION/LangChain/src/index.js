#!/usr/bin/env node

/**
 * Main entry point for LangChain.js AI Agent Server
 * Production-ready Node.js/Express.js RESTful API server
 */

import LangChainAIAgent from './agents.js';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import process from 'process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Production configuration with environment variables
 */
const config = {
  port: process.env.PORT || process.env.AGENT_PORT || 8000,
  ollamaBaseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
  ollamaModel: process.env.OLLAMA_MODEL || 'llama3.1:8b-instruct-q4_0',
  nodeEnv: process.env.NODE_ENV || 'development',
  logLevel: process.env.LOG_LEVEL || 'info'
};

/**
 * Production logging setup
 */
function setupLogging() {
  const originalLog = console.log;
  const originalError = console.error;
  const originalWarn = console.warn;

  console.log = (...args) => {
    const timestamp = new Date().toISOString();
    originalLog(`[${timestamp}] [INFO]`, ...args);
  };

  console.error = (...args) => {
    const timestamp = new Date().toISOString();
    originalError(`[${timestamp}] [ERROR]`, ...args);
  };

  console.warn = (...args) => {
    const timestamp = new Date().toISOString();
    originalWarn(`[${timestamp}] [WARN]`, ...args);
  };
}

/**
 * Production error handlers
 */
function setupErrorHandlers() {
  process.on('uncaughtException', (error) => {
    console.error('🚨 Uncaught Exception:', error);
    console.error('Stack:', error.stack);
    process.exit(1);
  });

  process.on('unhandledRejection', (reason, promise) => {
    console.error('🚨 Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
  });

  process.on('SIGTERM', () => {
    console.log('🛑 Received SIGTERM signal. Shutting down gracefully...');
    process.exit(0);
  });

  process.on('SIGINT', () => {
    console.log('\n🛑 Received SIGINT signal. Shutting down gracefully...');
    process.exit(0);
  });
}

/**
 * Health check for external dependencies
 */
async function checkDependencies() {
  const checks = [];
  
  // Check Ollama service
  try {
    const response = await fetch(`${config.ollamaBaseUrl}/api/tags`);
    if (response.ok) {
      const data = await response.json();
      const hasModel = data.models?.some(model => model.name.includes(config.ollamaModel.split(':')[0]));
      checks.push({
        service: 'Ollama',
        status: hasModel ? '✅ Ready' : '⚠️ Model not found',
        url: config.ollamaBaseUrl,
        model: config.ollamaModel
      });
    } else {
      checks.push({
        service: 'Ollama',
        status: '❌ Not available',
        url: config.ollamaBaseUrl
      });
    }
  } catch (error) {
    checks.push({
      service: 'Ollama',
      status: '❌ Connection failed',
      url: config.ollamaBaseUrl,
      error: error.message
    });
  }

  // Check Open-Meteo API
  try {
    const response = await fetch('https://api.open-meteo.com/v1/forecast?latitude=0&longitude=0&current_weather=true');
    checks.push({
      service: 'Open-Meteo API',
      status: response.ok ? '✅ Available' : '❌ Not available'
    });
  } catch (error) {
    checks.push({
      service: 'Open-Meteo API',
      status: '⚠️ Limited connectivity',
      error: error.message
    });
  }

  return checks;
}

/**
 * Display startup banner
 */
function displayBanner() {
  console.log('\n🚀 LangChain.js AI Agent Server');
  console.log('================================');
  console.log('📍 Production-Ready JavaScript Implementation');
  console.log('🏢 Designed for Enterprise DevOps & System Administrators');
  console.log('\n📊 Configuration:');
  console.log(`  🌐 Server Port: ${config.port}`);
  console.log(`  🧠 LLM Service: ${config.ollamaBaseUrl}`);
  console.log(`  🤖 Model: ${config.ollamaModel}`);
  console.log(`  🏃 Environment: ${config.nodeEnv}`);
  console.log(`  📝 Log Level: ${config.logLevel}`);
  console.log('\n⚡ Framework: LangChain.js + Express.js + Node.js');
  console.log('================================\n');
}

/**
 * Main application startup
 */
async function main() {
  try {
    // Setup production environment
    if (config.nodeEnv === 'production') {
      setupLogging();
    }
    setupErrorHandlers();
    
    // Display banner
    displayBanner();

    // Check dependencies
    console.log('🔍 Checking external dependencies...');
    const dependencyChecks = await checkDependencies();
    dependencyChecks.forEach(check => {
      console.log(`  ${check.service}: ${check.status}`);
      if (check.url) console.log(`    URL: ${check.url}`);
      if (check.model) console.log(`    Model: ${check.model}`);
      if (check.error) console.log(`    Error: ${check.error}`);
    });

    // Check for critical dependencies
    const ollamaCheck = dependencyChecks.find(c => c.service === 'Ollama');
    if (ollamaCheck && ollamaCheck.status.includes('❌')) {
      console.warn('\n⚠️  WARNING: Ollama service is not available!');
      console.warn('   Please ensure Ollama is running and has the required model:');
      console.warn(`   ollama serve & ollama pull ${config.ollamaModel}`);
      
      if (config.nodeEnv === 'production') {
        console.error('❌ Cannot start in production without Ollama service');
        process.exit(1);
      } else {
        console.warn('⚠️  Continuing in development mode...\n');
      }
    }

    // Initialize and start the AI Agent
    console.log('🚀 Starting LangChain.js AI Agent...');
    const agent = new LangChainAIAgent({
      port: config.port,
      ollamaBaseUrl: config.ollamaBaseUrl,
      ollamaModel: config.ollamaModel
    });

    await agent.start();

    // Production readiness indicators
    console.log('\n🎯 Production Readiness:');
    console.log('  ✅ RESTful API endpoints active');
    console.log('  ✅ OpenAI-compatible interface');
    console.log('  ✅ Health monitoring available');
    console.log('  ✅ Error handling configured');
    console.log('  ✅ Graceful shutdown enabled');
    console.log('\n🔗 Integration Endpoints:');
    console.log(`  📊 Health Check: http://localhost:${config.port}/health`);
    console.log(`  💬 OpenAI API: http://localhost:${config.port}/v1/chat/completions`);
    console.log(`  🤖 Direct Query: http://localhost:${config.port}/agent/query`);
    console.log(`  🛠️  Tools Info: http://localhost:${config.port}/agent/tools`);
    
    console.log('\n🌐 Open WebUI Integration:');
    console.log(`  Base URL: http://localhost:${config.port}/v1`);
    console.log('  API Key: Not required');
    
    console.log('\n✅ LangChain.js AI Agent is ready for production use!');

  } catch (error) {
    console.error('❌ Failed to start AI Agent:', error);
    console.error('Stack trace:', error.stack);
    process.exit(1);
  }
}

// Export for testing
export { config, checkDependencies };

// Start the application if this file is executed directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main();
}
