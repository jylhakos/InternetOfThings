import { createOllamaTaxiAgent } from "./agents/ollama-taxi-agent.js";
import { taxiTools } from "./tools/taxi-booking-tool.js";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config();

/**
 * Ollama Taxi Booking Agent Demo
 * Demonstrates using local LLMs instead of OpenAI
 */
async function ollamaDemo() {
  console.log("🦙 Ollama Taxi Booking Agent Demo");
  console.log("==================================\n");

  try {
    // Create the Ollama taxi booking agent
    const agent = createOllamaTaxiAgent({
      model: process.env.OLLAMA_MODEL || "llama3.1:8b",
      baseUrl: process.env.OLLAMA_BASE_URL || "http://localhost:11434",
      temperature: 0.1
    });

    console.log("🔧 Testing Ollama connection...");
    const connectionTest = await agent.testConnection();
    
    if (!connectionTest.success) {
      console.log("❌ Ollama connection failed:");
      console.log(`   Error: ${connectionTest.error}`);
      console.log("\n💡 Troubleshooting steps:");
      connectionTest.suggestions.forEach(suggestion => {
        console.log(`   • ${suggestion}`);
      });
      return;
    }

    console.log("✅ Ollama connection successful!");
    console.log(`   Model: ${connectionTest.model}`);
    console.log(`   Base URL: ${connectionTest.baseUrl}`);
    console.log("📋 Available tools:", agent.getAvailableTools().map(t => t.name).join(", "));
    console.log("🌍 Supported cities: London, Berlin, Paris, Madrid, Rome\n");

    // Example interactions
    const examples = [
      "Hello! Can you help me book a taxi?",
      "I need a taxi in London from Heathrow Airport to Westminster for 2 passengers.",
      "What are the coordinates of Berlin?",
      "Book a luxury taxi in Paris from Eiffel Tower to Louvre Museum for 4 people",
      "Check the status of booking taxi_1234567890_test"
    ];

    console.log("🎯 Running example interactions with Ollama...\n");

    for (let i = 0; i < examples.length; i++) {
      const example = examples[i];
      console.log(`\n--- Example ${i + 1} ---`);
      console.log(`👤 User: ${example}`);
      console.log("🦙 Ollama Agent: Processing...");

      try {
        const result = await agent.processMessage(example, {
          configurable: { thread_id: `ollama_example_${i + 1}` }
        });

        if (result.success) {
          console.log(`🤖 Agent: ${result.response}`);
          if (result.toolCalls.length > 0) {
            console.log(`🔧 Tools used: ${result.toolCalls.map(tc => tc.name).join(", ")}`);
          }
        } else {
          console.log(`❌ Error: ${result.error}`);
        }
      } catch (error) {
        console.log(`❌ Unexpected error: ${error.message}`);
      }

      // Add a delay between examples
      await new Promise(resolve => setTimeout(resolve, 1500));
    }

    console.log("\n🎉 Ollama demo completed successfully!");
    console.log("\n🔄 Performance Comparison:");
    console.log("┌─────────────────┬──────────────┬─────────────────┐");
    console.log("│ Aspect          │ OpenAI API   │ Ollama Local    │");
    console.log("├─────────────────┼──────────────┼─────────────────┤");
    console.log("│ Privacy         │ Cloud-based  │ 100% Local      │");
    console.log("│ Cost            │ Pay per token│ Free            │");
    console.log("│ Internet        │ Required     │ Optional        │");
    console.log("│ Customization   │ Limited      │ Full control    │");
    console.log("│ Setup           │ API key only │ Install + model │");
    console.log("└─────────────────┴──────────────┴─────────────────┘");

  } catch (error) {
    console.error("❌ Failed to run Ollama demo:", error.message);
    console.error("\n💡 Make sure:");
    console.log("   • Ollama is installed and running: ollama serve");
    console.log("   • Model is downloaded: ollama pull llama3.1:8b");
    console.log("   • Ollama is accessible at http://localhost:11434");
    console.log("\n🔗 Installation guide: https://ollama.com/download");
  }
}

/**
 * Test individual tools with Ollama (for debugging)
 */
async function testOllamaTools() {
  console.log("\n🧪 Testing Tools with Ollama Integration\n");

  try {
    const agent = createOllamaTaxiAgent();

    // Test simple tool usage prompts that work well with local LLMs
    const toolTests = [
      {
        prompt: "Find the coordinates of Madrid",
        expectedTool: "geocodingTool"
      },
      {
        prompt: "Book an economy taxi in Berlin from Brandenburg Gate to Hauptbahnhof for 1 person",
        expectedTool: "bookTaxi"
      },
      {
        prompt: "Check booking status for taxi_test_12345",
        expectedTool: "checkTaxiStatus"  
      }
    ];

    for (const test of toolTests) {
      console.log(`🔍 Testing: ${test.prompt}`);
      console.log(`   Expected tool: ${test.expectedTool}`);
      
      const result = await agent.processMessage(test.prompt);
      
      if (result.success) {
        const usedTools = result.toolCalls.map(tc => tc.name);
        const correctTool = usedTools.includes(test.expectedTool);
        console.log(`   ✅ ${correctTool ? 'PASS' : 'PARTIAL'}: Used tools: ${usedTools.join(', ') || 'none'}`);
      } else {
        console.log(`   ❌ FAIL: ${result.error}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

  } catch (error) {
    console.log(`❌ Tool testing error: ${error.message}`);
  }
}

/**
 * Show model recommendations
 */
function showModelRecommendations() {
  console.log("\n🦙 Ollama Model Recommendations for Taxi Booking Agent:");
  console.log("┌─────────────────┬─────────────┬─────────────┬─────────────────────┐");
  console.log("│ Model           │ Size        │ RAM Needed  │ Best For            │");
  console.log("├─────────────────┼─────────────┼─────────────┼─────────────────────┤");
  console.log("│ llama3.2:3b     │ ~2GB        │ 4GB+        │ Fast, basic tasks   │");
  console.log("│ llama3.1:8b     │ ~4.7GB      │ 8GB+        │ Good balance (⭐)    │");
  console.log("│ llama3.1:13b    │ ~7.3GB      │ 12GB+       │ Best quality        │");
  console.log("│ codellama:7b    │ ~3.8GB      │ 8GB+        │ Tool calling        │");
  console.log("│ mistral:7b      │ ~4.1GB      │ 8GB+        │ Efficient           │");
  console.log("└─────────────────┴─────────────┴─────────────┴─────────────────────┘");
  
  console.log("\n📥 Installation commands:");
  console.log("   ollama pull llama3.1:8b      # Recommended");
  console.log("   ollama pull codellama:7b     # For tool calling");
  console.log("   ollama pull llama3.2:3b      # Lightweight option");
}

// Run the demo
if (import.meta.url === `file://${process.argv[1]}`) {
  await ollamaDemo();
  await testOllamaTools();
  showModelRecommendations();
  
  console.log("\n🚗 Ollama Taxi Booking Demo Complete! 🦙");
}
