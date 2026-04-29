import { Client } from "@langchain/langgraph-sdk";
import { createTaxiAgent } from "../agents/taxi-booking-agent.js";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config();

/**
 * LangGraph SDK Integration Example
 * This demonstrates how to use the LangGraph SDK to interact with agents
 */

/**
 * Setup LangGraph Client for development server
 */
function createLangGraphClient() {
  const apiUrl = process.env.LANGGRAPH_API_URL || "http://localhost:2024";
  return new Client({ apiUrl });
}

/**
 * Stream responses from LangGraph server
 */
async function streamWithLangGraphSDK() {
  console.log("🌐 Testing LangGraph SDK Integration...\n");

  try {
    const client = createLangGraphClient();

    console.log("📡 Connecting to LangGraph server...");

    // Test message from the instructions
    const streamResponse = client.runs.stream(
      null, // Threadless run
      "agent", // Assistant ID
      {
        input: {
          "messages": [
            { "role": "user", "content": "I need a taxi in London from Heathrow Airport to Westminster for 2 passengers" }
          ]
        },
        streamMode: "messages-tuple",
      }
    );

    console.log("🚗 Requesting taxi booking...\n");

    for await (const chunk of streamResponse) {
      console.log(`📨 Receiving new event of type: ${chunk.event}...`);
      console.log(JSON.stringify(chunk.data, null, 2));
      console.log("\n" + "-".repeat(50) + "\n");
    }

  } catch (error) {
    console.error("❌ LangGraph SDK Error:", error.message);
    console.log("\n💡 Make sure the LangGraph development server is running:");
    console.log("   npx @langchain/langgraph-cli dev");
  }
}

/**
 * Direct agent usage (without SDK)
 */
async function directAgentUsage() {
  console.log("🤖 Testing Direct Agent Usage...\n");

  try {
    const agent = createTaxiAgent();

    const queries = [
      "What is LangGraph?",
      "I need a taxi in London from Heathrow Airport to Westminster for 2 passengers",
      "Find coordinates for Berlin",
      "Check status of booking taxi_example_123456"
    ];

    for (let i = 0; i < queries.length; i++) {
      const query = queries[i];
      console.log(`\n--- Query ${i + 1} ---`);
      console.log(`👤 User: ${query}`);

      const result = await agent.processMessage(query, {
        configurable: { thread_id: `direct_example_${i + 1}` }
      });

      if (result.success) {
        console.log(`🤖 Agent: ${result.response}`);
        if (result.toolCalls.length > 0) {
          console.log(`🔧 Tools used: ${result.toolCalls.map(tc => tc.name).join(", ")}`);
        }
      } else {
        console.log(`❌ Error: ${result.error}`);
      }

      // Add delay between queries
      await new Promise(resolve => setTimeout(resolve, 500));
    }

  } catch (error) {
    console.error("❌ Direct Agent Error:", error.message);
    if (error.message.includes("API key")) {
      console.log("💡 Please set your OPENAI_API_KEY in the .env file");
    }
  }
}

/**
 * Compare SDK vs Direct usage
 */
async function compareApproaches() {
  console.log("🔄 Comparing SDK vs Direct Agent Usage...\n");

  const testMessage = "Book a premium taxi in Berlin from Brandenburg Gate to Berlin Hauptbahnhof for 4 people";

  console.log("1️⃣ Using Direct Agent...");
  await directAgentUsage();

  console.log("\n" + "=".repeat(60) + "\n");

  console.log("2️⃣ Using LangGraph SDK...");
  await streamWithLangGraphSDK();
}

/**
 * Example of streaming responses
 */
async function streamingExample() {
  console.log("📡 Streaming Response Example...\n");

  try {
    const agent = createTaxiAgent();
    
    const userInput = "I want to book a luxury taxi in Paris from Eiffel Tower to Louvre Museum for 3 passengers";
    console.log(`👤 User: ${userInput}\n`);
    console.log("🤖 Agent (streaming): ");

    // Stream responses
    const stream = await agent.streamResponse(userInput, {
      configurable: { thread_id: "streaming_example" }
    });

    let stepCount = 0;
    for await (const output of stream) {
      stepCount++;
      console.log(`\n--- Step ${stepCount} ---`);
      
      // Extract the latest messages from the output
      const stateKey = Object.keys(output)[0];
      const state = output[stateKey];
      
      if (state && state.messages) {
        const lastMessage = state.messages[state.messages.length - 1];
        if (lastMessage.content) {
          console.log(`💬 ${lastMessage.content}`);
        }
        if (lastMessage.tool_calls && lastMessage.tool_calls.length > 0) {
          console.log(`🔧 Tool calls: ${lastMessage.tool_calls.map(tc => tc.name).join(", ")}`);
        }
      }
    }

    console.log("\n✅ Streaming completed!");

  } catch (error) {
    console.error("❌ Streaming Error:", error.message);
  }
}

/**
 * Main execution function
 */
async function main() {
  console.log("🚗 LangGraph SDK Integration Examples");
  console.log("=====================================\n");

  const examples = [
    { name: "Direct Agent Usage", fn: directAgentUsage },
    { name: "Streaming Example", fn: streamingExample },
    { name: "LangGraph SDK Integration", fn: streamWithLangGraphSDK }
  ];

  for (const example of examples) {
    try {
      console.log(`\n🎯 Running: ${example.name}`);
      console.log("=".repeat(40));
      await example.fn();
    } catch (error) {
      console.error(`❌ ${example.name} failed:`, error.message);
    }

    console.log("\n" + "⏸️  ".repeat(20));
    
    // Add pause between examples
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  console.log("\n🎉 All examples completed!");
}

// Export functions for use in other modules
export {
  createLangGraphClient,
  streamWithLangGraphSDK,
  directAgentUsage,
  compareApproaches,
  streamingExample
};

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
