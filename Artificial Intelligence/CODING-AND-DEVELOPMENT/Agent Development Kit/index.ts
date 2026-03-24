/**
 * ADK TypeScript Example: First Agent
 * 
 * This example demonstrates how to create a simple AI agent using
 * Google's Agent Development Kit (ADK) with TypeScript.
 */

import { Agent, createAgent } from '@google/adk';

// Define your agent with specific capabilities
const myAgent = createAgent({
  name: 'MyFirstAgent',
  model: 'gemini-pro',
  memory: true,  // Enable stateful memory
  systemPrompt: 'You are a helpful assistant designed to help with software development tasks.',
  tools: [
    // Add custom tools and functions here
    // Example tool structure:
    // {
    //   name: 'calculator',
    //   description: 'Performs basic math operations',
    //   parameters: {
    //     type: 'object',
    //     properties: {
    //       operation: { type: 'string', enum: ['add', 'subtract', 'multiply', 'divide'] },
    //       a: { type: 'number' },
    //       b: { type: 'number' }
    //     },
    //     required: ['operation', 'a', 'b']
    //   },
    //   execute: async ({ operation, a, b }) => {
    //     switch (operation) {
    //       case 'add': return a + b;
    //       case 'subtract': return a - b;
    //       case 'multiply': return a * b;
    //       case 'divide': return a / b;
    //       default: throw new Error('Invalid operation');
    //     }
    //   }
    // }
  ]
});

// Main function to run the agent
async function main() {
  try {
    console.log('🤖 Starting ADK Agent...\n');
    
    // Example 1: Simple prompt
    console.log('Example 1: Simple interaction');
    const response1 = await myAgent.run({
      prompt: 'Hello, how can you help me with software development?'
    });
    console.log('Agent:', response1);
    console.log('\n---\n');
    
    // Example 2: Follow-up conversation (demonstrating stateful memory)
    console.log('Example 2: Follow-up with memory');
    const response2 = await myAgent.run({
      prompt: 'What programming languages are you most familiar with?'
    });
    console.log('Agent:', response2);
    console.log('\n---\n');
    
    // Example 3: Multi-turn conversation
    console.log('Example 3: Multi-turn conversation');
    const response3 = await myAgent.run({
      prompt: 'Can you help me debug a TypeScript error?'
    });
    console.log('Agent:', response3);
    
  } catch (error) {
    console.error('Error running agent:', error);
    process.exit(1);
  }
}

// Run the agent if this file is executed directly
if (require.main === module) {
  main();
}

// Export for use in other modules
export { myAgent };
