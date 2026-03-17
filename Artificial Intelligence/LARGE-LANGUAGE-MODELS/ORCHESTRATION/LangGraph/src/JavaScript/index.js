import { createTaxiAgent, TAXI_AGENT_SYSTEM_PROMPT } from "./agents/taxi-booking-agent.js";
import { taxiTools } from "./tools/taxi-booking-tool.js";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config();

/**
 * Main application for LangGraph Taxi Booking Agent
 */
async function main() {
  console.log("🚗 LangGraph Taxi Booking Agent Starting...\n");

  try {
    // Create the taxi booking agent
    const agent = createTaxiAgent({
      model: "gpt-3.5-turbo",
      temperature: 0.1
    });

    console.log("✅ Agent initialized successfully!");
    console.log("📋 Available tools:", agent.getAvailableTools().map(t => t.name).join(", "));
    console.log("🌍 Supported cities: London, Berlin, Paris, Madrid, Rome\n");

    // Example interactions
    const examples = [
      "I need a taxi in London from Heathrow Airport to Westminster. I'm traveling with 2 passengers.",
      "Can you find the coordinates for Berlin?",
      "Book a luxury taxi in Paris from Eiffel Tower to Louvre Museum for 4 people",
      "Check the status of booking taxi_1735123456789_abc123def"
    ];

    console.log("🎯 Running example interactions...\n");

    for (let i = 0; i < examples.length; i++) {
      const example = examples[i];
      console.log(`\n--- Example ${i + 1} ---`);
      console.log(`👤 User: ${example}`);
      console.log("🤖 Agent: Processing...");

      try {
        const result = await agent.processMessage(example, {
          configurable: { thread_id: `example_${i + 1}` }
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

      // Add a small delay between examples
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    console.log("\n🎉 Demo completed successfully!");
    console.log("\n📖 To run your own queries, modify the examples array or create an interactive version.");

  } catch (error) {
    console.error("❌ Failed to initialize agent:", error.message);
    console.error("💡 Make sure you have set your OPENAI_API_KEY in .env file");
  }
}

/**
 * Interactive mode for testing
 */
async function interactiveMode() {
  console.log("🚗 Interactive Taxi Booking Agent");
  console.log("Type your requests or 'exit' to quit\n");

  const agent = createTaxiAgent();
  
  // This would be implemented with readline for actual interactive use
  console.log("💡 Interactive mode would be implemented here with readline");
  console.log("For now, running the demo examples...\n");
  
  await main();
}

// Run the main function
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}