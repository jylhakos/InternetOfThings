/**
 * Comprehensive example client for LangChain.js AI Agent
 * Demonstrates all available features and endpoints
 */

import fetch from 'node-fetch';

class LangChainAgentClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = `demo-${Date.now()}`;
  }

  /**
   * Test agent health
   */
  async testHealth() {
    console.log('🏥 Testing Agent Health...');
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      const health = await response.json();
      
      console.log(`✅ Status: ${health.status}`);
      console.log(`🧠 Model: ${health.services.llm}`);
      console.log(`🛠️ Tools: ${health.services.tools.join(', ')}`);
      console.log(`📡 Framework: ${health.framework}`);
      return true;
    } catch (error) {
      console.error('❌ Health check failed:', error.message);
      return false;
    }
  }

  /**
   * Test OpenAI-compatible endpoint
   */
  async testChatCompletion(message) {
    try {
      const response = await fetch(`${this.baseUrl}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [{ role: 'user', content: message }],
          temperature: 0.7
        })
      });

      const result = await response.json();
      return result.choices[0].message.content;
    } catch (error) {
      return `Error: ${error.message}`;
    }
  }

  /**
   * Test direct agent query endpoint
   */
  async testAgentQuery(query) {
    try {
      const response = await fetch(`${this.baseUrl}/agent/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          session_id: this.sessionId
        })
      });

      const result = await response.json();
      return result.response;
    } catch (error) {
      return `Error: ${error.message}`;
    }
  }

  /**
   * Test conversation history
   */
  async testConversationHistory() {
    try {
      const response = await fetch(`${this.baseUrl}/agent/history/${this.sessionId}`);
      const result = await response.json();
      
      console.log(`\n📜 Conversation History (${result.message_count} messages):`);
      result.history.forEach((entry, index) => {
        console.log(`\n${index + 1}. 👤 User: ${entry.user.substring(0, 80)}...`);
        console.log(`   🤖 Agent: ${entry.assistant.substring(0, 80)}...`);
      });
    } catch (error) {
      console.error('❌ History fetch failed:', error.message);
    }
  }

  /**
   * Test available tools
   */
  async testAvailableTools() {
    try {
      const response = await fetch(`${this.baseUrl}/agent/tools`);
      const result = await response.json();
      
      console.log('\n🛠️ Available Tools:');
      result.tools.forEach(tool => {
        console.log(`  • ${tool.name}: ${tool.description}`);
      });
    } catch (error) {
      console.error('❌ Tools fetch failed:', error.message);
    }
  }

  /**
   * Run comprehensive demo
   */
  async runDemo() {
    console.log('🎯 LangChain.js AI Agent Demo');
    console.log('============================\n');

    // Health check
    const isHealthy = await this.testHealth();
    if (!isHealthy) {
      console.log('\n❌ Agent is not healthy. Make sure it\'s running on', this.baseUrl);
      return;
    }

    // Show available tools
    await this.testAvailableTools();

    // Test different types of queries
    const testCases = [
      {
        category: '👋 Greetings',
        queries: [
          'Hello, how are you?',
          'Good morning!',
          'Hey there!'
        ]
      },
      {
        category: '🌤️ Weather Queries',
        queries: [
          'What is the weather in London?',
          'Temperature in Tokyo?',
          'How\'s the climate in Paris today?'
        ]
      },
      {
        category: '📍 Location Queries', 
        queries: [
          'Where is New York located?',
          'What are the coordinates of Berlin?',
          'Tell me about the location of Sydney'
        ]
      },
      {
        category: '🧠 General Questions',
        queries: [
          'Explain artificial intelligence',
          'What is machine learning?',
          'How do neural networks work?'
        ]
      }
    ];

    for (const testCase of testCases) {
      console.log(`\n${testCase.category}`);
      console.log('='.repeat(testCase.category.length));

      for (const query of testCase.queries) {
        console.log(`\n👤 User: ${query}`);
        
        // Use agent query endpoint for demo
        const response = await this.testAgentQuery(query);
        const truncated = response.length > 200 
          ? response.substring(0, 200) + '...' 
          : response;
        console.log(`🤖 Agent: ${truncated}`);

        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
    }

    // Show conversation history
    await this.testConversationHistory();

    console.log('\n✅ Demo completed successfully!');
    console.log('\n🔗 Try these endpoints:');
    console.log(`  • Health: curl ${this.baseUrl}/health`);
    console.log(`  • Chat: curl -X POST ${this.baseUrl}/v1/chat/completions -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"Hello!"}]}'`);
    console.log(`  • Query: curl -X POST ${this.baseUrl}/agent/query -H "Content-Type: application/json" -d '{"query":"Weather in London"}'`);
  }
}

// Create and run demo
const client = new LangChainAgentClient();
client.runDemo().catch(console.error);
