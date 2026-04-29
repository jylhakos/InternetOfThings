/**
 * Test client for LangChain.js AI Agent
 */

import { AgentTester } from './agents.js';

/**
 * Test the AI Agent with various queries
 */
async function main() {
  const tester = new AgentTester('http://localhost:8000');
  
  console.log('🎯 Starting LangChain.js AI Agent Tests');
  console.log('======================================\n');
  
  // Wait a bit to ensure server is ready
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  await tester.runTests();
  
  console.log('\n✅ Tests completed!');
}

// Run the tests
main().catch(console.error);
