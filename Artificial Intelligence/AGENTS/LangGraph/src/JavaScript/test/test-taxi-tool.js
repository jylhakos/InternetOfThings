import { taxiTools, geocodingTool, taxiBookingTool, taxiStatusTool } from "../tools/taxi-booking-tool.js";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config();

/**
 * Simple test suite for Taxi Booking Tools
 */

console.log("🚗 LangGraph Taxi Tools - Test Suite");
console.log("====================================\n");

let passed = 0;
let failed = 0;

async function runTest(testName, testFn) {
  console.log(`🧪 Running test: ${testName}`);
  try {
    await testFn();
    console.log(`✅ PASSED: ${testName}`);
    passed++;
  } catch (error) {
    console.log(`❌ FAILED: ${testName}`);
    console.log(`   Error: ${error.message}`);
    failed++;
  }
  console.log();
}

// Test 1: Tool Loading
await runTest("Tool Loading", async () => {
  if (taxiTools.length !== 3) {
    throw new Error(`Expected 3 tools, got ${taxiTools.length}`);
  }
  
  const toolNames = taxiTools.map(t => t.name);
  const expectedNames = ["geocodingTool", "bookTaxi", "checkTaxiStatus"];
  
  for (const expectedName of expectedNames) {
    if (!toolNames.includes(expectedName)) {
      throw new Error(`Missing expected tool: ${expectedName}`);
    }
  }
});

// Test 2: Geocoding Tool - London
await runTest("Geocoding Tool - London", async () => {
  const result = await geocodingTool.invoke({ city: "London" });
  if (!result.includes("Latitude: 51.5074")) {
    throw new Error("Expected London coordinates not found");
  }
});

// Test 3: Geocoding Tool - Unknown City
await runTest("Geocoding Tool - Unknown City", async () => {
  const result = await geocodingTool.invoke({ city: "UnknownCity" });
  if (!result.includes("Location not found")) {
    throw new Error("Expected 'Location not found' message");
  }
});

// Test 4: Taxi Booking Tool - London Economy
await runTest("Taxi Booking Tool - London Economy", async () => {
  const result = await taxiBookingTool.invoke({
    city: "London",
    pickup_address: "Heathrow Airport",
    destination_address: "Westminster",
    passenger_count: 2,
    taxi_type: "economy"
  });
  if (!result.includes("Taxi booked successfully")) {
    throw new Error("Expected successful booking message");
  }
  if (!result.includes("London")) {
    throw new Error("Expected city in response");
  }
});

// Test 5: Taxi Booking Tool - Berlin Premium
await runTest("Taxi Booking Tool - Berlin Premium", async () => {
  const result = await taxiBookingTool.invoke({
    city: "Berlin",
    pickup_address: "Brandenburg Gate",
    destination_address: "Berlin Hauptbahnhof",
    passenger_count: 4,
    taxi_type: "premium"
  });
  if (!result.includes("Taxi booked successfully")) {
    throw new Error("Expected successful booking message");
  }
  if (!result.includes("Berlin")) {
    throw new Error("Expected city in response");
  }
});

// Test 6: Taxi Status Tool
await runTest("Taxi Status Tool", async () => {
  const result = await taxiStatusTool.invoke({
    booking_id: "taxi_test_123456"
  });
  if (!result.includes("Taxi Status Update")) {
    throw new Error("Expected status update message");
  }
  if (!result.includes("taxi_test_123456")) {
    throw new Error("Expected booking ID in response");
  }
});

// Test 7: Multiple Cities
await runTest("Multiple Cities Support", async () => {
  const cities = ["Berlin", "Paris", "Madrid", "Rome"];
  
  for (const city of cities) {
    const result = await geocodingTool.invoke({ city });
    if (result.includes("Location not found")) {
      throw new Error(`Expected ${city} to be supported`);
    }
  }
});

// Test 8: Taxi Types
await runTest("All Taxi Types", async () => {
  const taxiTypes = ["economy", "premium", "luxury", "van"];
  
  for (const taxiType of taxiTypes) {
    const result = await taxiBookingTool.invoke({
      city: "London",
      pickup_address: "Test Location",
      destination_address: "Test Destination",
      passenger_count: 2,
      taxi_type: taxiType
    });
    
    if (!result.includes("Taxi booked successfully")) {
      throw new Error(`Expected successful booking for ${taxiType} taxi`);
    }
  }
});

// Print summary
console.log("=".repeat(50));
console.log("📊 TEST SUMMARY");
console.log("=".repeat(50));
console.log(`✅ Passed: ${passed}`);
console.log(`❌ Failed: ${failed}`);
console.log(`📈 Total:  ${passed + failed}`);

if (failed === 0) {
  console.log("🎉 All tests passed!");
} else {
  console.log(`⚠️  ${failed} test(s) failed`);
}
console.log("=".repeat(50));

// Manual tool demonstrations
console.log("\n🔧 Manual Tool Testing\n");

console.log("1. Testing Geocoding Tool:");
console.log(await geocodingTool.invoke({ city: "London" }));

console.log("\n2. Testing Taxi Booking Tool:");
console.log(await taxiBookingTool.invoke({
  city: "Berlin",
  pickup_address: "Berlin Central Station",
  destination_address: "Brandenburg Gate", 
  passenger_count: 2,
  taxi_type: "premium"
}));

console.log("\n3. Testing Status Check Tool:");
console.log(await taxiStatusTool.invoke({
  booking_id: "taxi_manual_test_123"
}));

console.log("\n🏁 All testing completed!");
