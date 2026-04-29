#!/usr/bin/env node

/**
 * Project validation script for LangGraph Taxi Booking Agents
 */

import { existsSync, readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("🚗 LangGraph Taxi Booking Agents - Project Validation");
console.log("====================================================\n");

let checks = 0;
let passed = 0;
let failed = 0;

function check(description, condition) {
  checks++;
  if (condition) {
    console.log(`✅ ${description}`);
    passed++;
  } else {
    console.log(`❌ ${description}`);
    failed++;
  }
}

// File structure validation
console.log("📁 Checking project structure...");

const requiredFiles = [
  'package.json',
  'index.js', 
  'demo.js',
  'agents/taxi-booking-agent.js',
  'tools/taxi-booking-tool.js',
  'test/test-taxi-tool.js',
  'examples/langgraph-sdk-integration.js',
  'setup/install-deps.js',
  '.env.example',
  'config.json',
  'QUICKSTART.md'
];

requiredFiles.forEach(file => {
  check(`${file} exists`, existsSync(join(__dirname, file)));
});

// Package.json validation
console.log("\n📦 Checking package.json...");
try {
  const packageJson = JSON.parse(readFileSync(join(__dirname, 'package.json'), 'utf8'));
  
  check("package.json is valid JSON", true);
  check("name is set", packageJson.name === 'langgraph-taxi-agents');
  check("type is module", packageJson.type === 'module');
  check("has start script", packageJson.scripts && packageJson.scripts.start);
  check("has demo script", packageJson.scripts && packageJson.scripts.demo);
  check("has test script", packageJson.scripts && packageJson.scripts.test);
  
  const requiredDeps = [
    '@langchain/langgraph',
    '@langchain/core',
    '@langchain/openai',
    'dotenv',
    'zod',
    'axios'
  ];
  
  requiredDeps.forEach(dep => {
    check(`dependency ${dep}`, packageJson.dependencies && packageJson.dependencies[dep]);
  });
  
} catch (error) {
  check("package.json is valid", false);
}

// Dependencies check
console.log("\n📚 Checking node_modules...");
check("node_modules exists", existsSync(join(__dirname, 'node_modules')));

// Tool imports check
console.log("\n🔧 Checking tool imports...");
try {
  const { taxiTools } = await import('./tools/taxi-booking-tool.js');
  check("taxi tools import successfully", true);
  check("has 3 tools", taxiTools && taxiTools.length === 3);
  
  const expectedTools = ['geocodingTool', 'bookTaxi', 'checkTaxiStatus'];
  const toolNames = taxiTools.map(t => t.name);
  
  expectedTools.forEach(toolName => {
    check(`has ${toolName}`, toolNames.includes(toolName));
  });
  
} catch (error) {
  check("taxi tools import", false);
  console.log(`   Error: ${error.message}`);
}

// Agent import check
console.log("\n🤖 Checking agent imports...");
try {
  const { createTaxiAgent, TaxiBookingAgent } = await import('./agents/taxi-booking-agent.js');
  check("agent imports successfully", true);
  check("has createTaxiAgent function", typeof createTaxiAgent === 'function');
  
} catch (error) {
  check("agent imports", false);
  console.log(`   Error: ${error.message}`);
}

// Configuration check
console.log("\n⚙️ Checking configuration...");
try {
  const config = JSON.parse(readFileSync(join(__dirname, 'config.json'), 'utf8'));
  check("config.json is valid", true);
  check("has supported cities", config.config && config.config.supported_cities && config.config.supported_cities.length >= 5);
  check("has taxi types", config.config && config.config.taxi_types && config.config.taxi_types.length >= 4);
  
} catch (error) {
  check("config.json validation", false);
}

// Environment check
console.log("\n🌍 Checking environment...");
check(".env.example exists", existsSync(join(__dirname, '.env.example')));

if (existsSync(join(__dirname, '.env'))) {
  check(".env file exists", true);
  try {
    const envContent = readFileSync(join(__dirname, '.env'), 'utf8');
    check("has OPENAI_API_KEY placeholder", envContent.includes('OPENAI_API_KEY'));
  } catch (error) {
    check("can read .env file", false);
  }
} else {
  check(".env file exists (optional)", true); // Not required for basic functionality
}

// Tool functionality check
console.log("\n🧪 Testing tool functionality...");
try {
  const { geocodingTool, taxiBookingTool, taxiStatusTool } = await import('./tools/taxi-booking-tool.js');
  
  // Test geocoding
  const geocodeResult = await geocodingTool.invoke({ city: "London" });
  check("geocoding tool works", geocodeResult.includes("London"));
  
  // Test booking
  const bookingResult = await taxiBookingTool.invoke({
    city: "Berlin",
    pickup_address: "Test Location",
    destination_address: "Test Destination",
    passenger_count: 2,
    taxi_type: "economy"
  });
  check("booking tool works", bookingResult.includes("Taxi booked successfully"));
  
  // Test status
  const statusResult = await taxiStatusTool.invoke({ booking_id: "test_123" });
  check("status tool works", statusResult.includes("Taxi Status Update"));
  
} catch (error) {
  check("tool functionality", false);
  console.log(`   Error: ${error.message}`);
}

// Summary
console.log("\n" + "=".repeat(60));
console.log("📊 VALIDATION SUMMARY");
console.log("=".repeat(60));
console.log(`✅ Passed: ${passed}`);
console.log(`❌ Failed: ${failed}`);
console.log(`📈 Total:  ${checks}`);

if (failed === 0) {
  console.log("🎉 All validations passed! Project is ready to use.");
  console.log("\n🚀 Quick commands to get started:");
  console.log("• npm run demo    - See the tools in action");
  console.log("• npm test        - Run comprehensive tests");
  console.log("• npm start       - Run the main agent (requires OpenAI API key)");
} else {
  console.log(`⚠️  ${failed} validation(s) failed. Please check the issues above.`);
  
  if (failed < 5) {
    console.log("💡 Minor issues detected. The project should still work for basic functionality.");
  }
}

console.log("=".repeat(60));
