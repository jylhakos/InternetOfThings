import { taxiTools, geocodingTool, taxiBookingTool, taxiStatusTool } from "./tools/taxi-booking-tool.js";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config();

/**
 * Demo application showing LangGraph taxi booking tools in action
 * This works without OpenAI API key by directly using the tools
 */

console.log("🚗 LangGraph Taxi Booking Tools - Demo");
console.log("======================================\n");

// Show available tools
console.log("📋 Available Tools:");
taxiTools.forEach((tool, index) => {
  console.log(`${index + 1}. ${tool.name} - ${tool.description}`);
});
console.log();

console.log("🌍 Supported Cities: London, Berlin, Paris, Madrid, Rome");
console.log("🚗 Taxi Types: economy, premium, luxury, van\n");

// Demo scenarios
const demoScenarios = [
  {
    title: "🌍 Geocoding Demo - Find London Coordinates",
    action: async () => {
      console.log("👤 User: What are the coordinates of London?");
      const result = await geocodingTool.invoke({ city: "London" });
      console.log(`🤖 Tool Response: ${result}`);
    }
  },
  {
    title: "🚗 Taxi Booking Demo - London Economy",
    action: async () => {
      console.log("👤 User: I need a taxi in London from Heathrow Airport to Westminster for 2 passengers");
      const result = await taxiBookingTool.invoke({
        city: "London",
        pickup_address: "Heathrow Airport",
        destination_address: "Westminster",
        passenger_count: 2,
        taxi_type: "economy"
      });
      console.log(`🤖 Tool Response:\n${result}`);
    }
  },
  {
    title: "🚗 Taxi Booking Demo - Berlin Premium",
    action: async () => {
      console.log("👤 User: Book a premium taxi in Berlin from Brandenburg Gate to Berlin Hauptbahnhof for 4 people");
      const result = await taxiBookingTool.invoke({
        city: "Berlin",
        pickup_address: "Brandenburg Gate",
        destination_address: "Berlin Hauptbahnhof",
        passenger_count: 4,
        taxi_type: "premium"
      });
      console.log(`🤖 Tool Response:\n${result}`);
    }
  },
  {
    title: "🚗 Luxury Taxi Demo - Paris",
    action: async () => {
      console.log("👤 User: I want a luxury taxi in Paris from Eiffel Tower to Louvre Museum for 3 people");
      const result = await taxiBookingTool.invoke({
        city: "Paris",
        pickup_address: "Eiffel Tower",
        destination_address: "Louvre Museum",
        passenger_count: 3,
        taxi_type: "luxury"
      });
      console.log(`🤖 Tool Response:\n${result}`);
    }
  },
  {
    title: "📊 Status Check Demo",
    action: async () => {
      // First, let's get a booking ID from a booking
      const booking = await taxiBookingTool.invoke({
        city: "Madrid",
        pickup_address: "Madrid Airport",
        destination_address: "Plaza Mayor",
        passenger_count: 1,
        taxi_type: "economy"
      });
      
      // Extract booking ID from the response
      const bookingIdMatch = booking.match(/Booking ID: (taxi_\w+)/);
      const bookingId = bookingIdMatch ? bookingIdMatch[1] : "taxi_demo_123456";
      
      console.log(`👤 User: Check status of booking ${bookingId}`);
      const result = await taxiStatusTool.invoke({ booking_id: bookingId });
      console.log(`🤖 Tool Response:\n${result}`);
    }
  },
  {
    title: "🌍 Multiple Cities Demo",
    action: async () => {
      console.log("👤 User: Show me coordinates for all supported cities");
      const cities = ["London", "Berlin", "Paris", "Madrid", "Rome"];
      
      for (const city of cities) {
        const result = await geocodingTool.invoke({ city });
        console.log(`🌍 ${result}`);
      }
    }
  },
  {
    title: "🚐 Van Booking Demo - Large Group",
    action: async () => {
      console.log("👤 User: Book a van in Rome for 8 passengers from Colosseum to Vatican City");
      const result = await taxiBookingTool.invoke({
        city: "Rome",
        pickup_address: "Colosseum",
        destination_address: "Vatican City",
        passenger_count: 8,
        taxi_type: "van"
      });
      console.log(`🤖 Tool Response:\n${result}`);
    }
  },
  {
    title: "❌ Error Handling Demo",
    action: async () => {
      console.log("👤 User: Find coordinates for an unsupported city");
      const result = await geocodingTool.invoke({ city: "Tokyo" });
      console.log(`🤖 Tool Response: ${result}`);
    }
  }
];

// Run all demo scenarios
for (let i = 0; i < demoScenarios.length; i++) {
  const scenario = demoScenarios[i];
  
  console.log(`\n--- Demo ${i + 1}: ${scenario.title} ---`);
  
  try {
    await scenario.action();
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
  }
  
  // Add a small delay between demos for readability
  await new Promise(resolve => setTimeout(resolve, 800));
}

console.log("\n" + "=".repeat(60));
console.log("🎉 Demo completed successfully!");
console.log("=".repeat(60));

console.log("\n📖 How LangGraph Agents Use These Tools:");
console.log("1. 🔨 Tool Creation - Tools defined with schemas using LangChain's tool() function");
console.log("2. 🔗 Tool Binding - Tools connected to model that supports tool calling");
console.log("3. 📞 Tool Calling - Model decides when to call tools based on user input");
console.log("4. ⚙️ Tool Execution - Tools executed using arguments provided by the model");

console.log("\n🔧 Tool Function Explanations:");
console.log("• geocodingTool - Converts city names to coordinates using mock geocoding data");
console.log("• bookTaxi - Books taxi reservations with comprehensive validation and pricing");
console.log("• checkTaxiStatus - Monitors existing bookings with real-time status updates");

console.log("\n🌐 API Integration:");
console.log("• Geocoding: https://docs.maptiler.com/server/api/geocoding/");
console.log("• Taxi API: https://api.taxicode.com/");
console.log("• LangGraph: https://langchain-ai.github.io/langgraphjs/");

console.log("\n⚡ Next Steps:");
console.log("1. Set OPENAI_API_KEY in .env to enable full agent functionality");
console.log("2. Run 'npx @langchain/langgraph-cli dev' to start the LangGraph server");
console.log("3. Use 'npm run sdk-example' to test LangGraph SDK integration");
console.log("4. Extend tools with real API integrations for production use");

console.log("\n🚗 Happy taxi booking with LangGraph! 🤖");
