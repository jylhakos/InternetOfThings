#!/usr/bin/env python3
"""
Test script for Llama 4 Scout AI Agent integration.
This script tests the key features and capabilities.
"""

import asyncio
import sys
import os
import json
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from tools import ToolManager, LLMTool, WeatherTool
    from agents import AIAgent
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root and have installed dependencies")
    sys.exit(1)


async def test_weather_tool():
    """Test weather functionality."""
    print("🌤️  Testing Weather Tool...")
    weather_tool = WeatherTool()
    
    # Test coordinates
    coords = await weather_tool.get_coordinates("London")
    if coords:
        print(f"✅ London coordinates: {coords['latitude']}, {coords['longitude']}")
    else:
        print("❌ Failed to get London coordinates")
        return False
    
    # Test weather data
    if coords:
        weather = await weather_tool.get_weather(coords['latitude'], coords['longitude'])
        if weather:
            print(f"✅ London weather: {weather['temperature']}°C")
        else:
            print("❌ Failed to get London weather")
            return False
    
    # Test full temperature function
    temp_response = await weather_tool.get_temperature("Paris")
    if temp_response and "temperature" in temp_response.lower():
        print(f"✅ Paris temperature response: {temp_response[:100]}...")
    else:
        print(f"❌ Failed to get Paris temperature: {temp_response}")
        return False
    
    return True


async def test_llm_tool(model: str):
    """Test LLM functionality with specified model."""
    print(f"🧠 Testing LLM Tool with {model}...")
    llm_tool = LLMTool(model=model)
    
    # Test basic response
    response = await llm_tool.generate_response(
        "Hello, please respond with exactly 'Test successful' to confirm you're working.",
        temperature=0.1
    )
    
    if response:
        print(f"✅ LLM response: {response[:100]}...")
        
        # Check if it's Llama 4 and test tool calling
        if llm_tool.is_llama4:
            print("🌟 Testing Llama 4 Scout tool calling...")
            tool_response = await llm_tool.generate_response(
                "What's the weather like in Tokyo?",
                temperature=0.7,
                use_tools=True
            )
            if tool_response and "weather" in tool_response.lower():
                print(f"✅ Llama 4 tool calling: {tool_response[:100]}...")
            else:
                print(f"⚠️  Llama 4 tool calling unclear: {tool_response}")
        
        return True
    else:
        print("❌ Failed to get LLM response")
        return False


async def test_tool_manager(model: str):
    """Test tool manager with specified model."""
    print(f"🔧 Testing Tool Manager with {model}...")
    manager = ToolManager(ollama_model=model)
    
    test_cases = [
        ("Hello, how are you?", "greeting"),
        ("What's the temperature in London?", "weather"),
        ("Tell me about Python programming", "general"),
    ]
    
    success_count = 0
    for message, expected_type in test_cases:
        result = await manager.process_message(message)
        if result and result.get('content'):
            print(f"✅ '{message}' → {result['type']}: {result['content'][:50]}...")
            if result['type'] == expected_type:
                success_count += 1
            else:
                print(f"   ⚠️  Expected {expected_type}, got {result['type']}")
        else:
            print(f"❌ Failed to process: '{message}'")
    
    print(f"Tool Manager: {success_count}/{len(test_cases)} tests matched expected types")
    return success_count > 0


async def test_ai_agent(model: str):
    """Test AI agent with specified model."""
    print(f"🤖 Testing AI Agent with {model}...")
    agent = AIAgent(ollama_model=model)
    
    # Test chat completion
    messages = [{"role": "user", "content": "Hello! What's the weather in London?"}]
    response = await agent.process_chat_completion(messages)
    
    if response and response.get('choices'):
        content = response['choices'][0]['message']['content']
        print(f"✅ AI Agent response: {content[:100]}...")
        
        # Check metadata
        if 'metadata' in response:
            metadata = response['metadata']
            print(f"   Agent type: {metadata.get('agent_type')}")
            print(f"   Model: {response.get('model')}")
            
            if agent.is_llama4 and metadata.get('llama4_features'):
                print("🌟 Llama 4 features detected in response")
        
        return True
    else:
        print("❌ Failed to get AI agent response")
        return False


async def test_health_check(model: str):
    """Test health check functionality."""
    print(f"🏥 Testing Health Check with {model}...")
    agent = AIAgent(ollama_model=model)
    
    health = await agent.health_check()
    if health:
        print(f"✅ Health status: {health['status']}")
        print(f"   LLM status: {health['services']['llm']}")
        print(f"   Weather API status: {health['services']['weather_api']}")
        
        if 'agent_info' in health:
            info = health['agent_info']
            print(f"   Agent: {info['name']} v{info['version']}")
            print(f"   Capabilities: {info['capabilities']}")
            
            if 'features' in info:
                features = info['features']
                print(f"   Features: MoE={features.get('mixture_of_experts', False)}, "
                     f"Tools={features.get('tool_calling', False)}, "
                     f"Context={features.get('extended_context', False)}")
        
        return health['status'] in ['healthy', 'degraded']
    else:
        print("❌ Failed to get health check")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Llama 4 Scout AI Agent Tests...\n")
    
    # Models to test
    models_to_test = []
    
    # Check which models are available
    print("🔍 Checking available models...")
    
    # Test if Ollama is running
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                print(f"✅ Ollama is running. Available models: {len(available_models)}")
                
                # Prefer Llama 4 models
                for model in ['llama4:scout', 'ingu627/llama4-scout-q4']:
                    if model in available_models:
                        models_to_test.append(model)
                        print(f"🌟 Found Llama 4 model: {model}")
                        break
                
                # Fallback to Llama 3.x
                for model in ['llama3.1:8b-instruct-q4_0', 'llama3.1:7b-instruct-q4_0']:
                    if model in available_models:
                        models_to_test.append(model)
                        print(f"📝 Found legacy model: {model}")
                        break
                        
            else:
                print("❌ Ollama API not responding properly")
                models_to_test = ['llama4:scout']  # Try anyway
                
    except Exception as e:
        print(f"⚠️  Could not check Ollama status: {e}")
        print("Will attempt tests with default model")
        models_to_test = ['llama4:scout']
    
    if not models_to_test:
        print("❌ No models available for testing")
        return
    
    # Run tests for each model
    for model in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing with model: {model}")
        print(f"{'='*60}")
        
        # Test individual components
        weather_ok = await test_weather_tool()
        llm_ok = await test_llm_tool(model)
        manager_ok = await test_tool_manager(model)
        agent_ok = await test_ai_agent(model)
        health_ok = await test_health_check(model)
        
        # Summary for this model
        total_tests = 5
        passed_tests = sum([weather_ok, llm_ok, manager_ok, agent_ok, health_ok])
        
        print(f"\n📊 Results for {model}: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed!")
        elif passed_tests >= 3:
            print("✅ Most tests passed - system is functional")
        else:
            print("⚠️  Several tests failed - check configuration")
    
    print(f"\n{'='*60}")
    print("🏁 Test suite completed!")
    print("Next steps:")
    print("1. Start the agent: python src/index.py")
    print("2. Test the API: curl http://localhost:8000/health")
    print("3. Try the web interface: make full-stack")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
