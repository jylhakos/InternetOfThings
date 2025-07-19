"""
Test script for individual components of the AI Agent.
Run this to test tools and agent functionality without the web server.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools import ToolManager, WeatherTool, LLMTool
from agents import AIAgent


async def test_weather_tool():
    """Test weather functionality."""
    print("🌤️  Testing Weather Tool")
    print("-" * 30)
    
    weather_tool = WeatherTool()
    
    # Test city coordinates
    print("Getting coordinates for London...")
    coords = await weather_tool.get_coordinates("London")
    if coords:
        print(f"✅ London: {coords['latitude']}, {coords['longitude']}")
        
        # Test weather data
        print("Getting weather data...")
        weather = await weather_tool.get_weather(coords['latitude'], coords['longitude'])
        if weather:
            print(f"✅ Weather: {weather['temperature']}°C")
        else:
            print("❌ Failed to get weather data")
    else:
        print("❌ Failed to get coordinates")
    
    # Test temperature function
    print("\nGetting temperature for Paris...")
    temp_response = await weather_tool.get_temperature("Paris")
    print(f"Response: {temp_response}")


async def test_llm_tool():
    """Test LLM functionality."""
    print("\n🤖 Testing LLM Tool")
    print("-" * 30)
    
    llm_tool = LLMTool()
    
    # Test greeting detection
    test_messages = [
        "Hello world",
        "What's the weather like?",
        "Good morning",
        "How are you doing?"
    ]
    
    print("Testing greeting detection...")
    for msg in test_messages:
        is_greeting = await llm_tool.is_greeting(msg)
        print(f"  '{msg}' -> {'Greeting' if is_greeting else 'Not greeting'}")
    
    # Test weather query detection
    print("\nTesting weather query detection...")
    weather_messages = [
        "What's the temperature in London?",
        "Tell me about the weather in Paris",
        "How hot is it in Tokyo?",
        "Hello, how are you?"
    ]
    
    for msg in weather_messages:
        is_weather = await llm_tool.is_weather_query(msg)
        city = await llm_tool.extract_city_name(msg) if is_weather else None
        print(f"  '{msg}' -> {'Weather' if is_weather else 'Not weather'} {f'(City: {city})' if city else ''}")
    
    # Test LLM response generation
    print("\nTesting LLM response generation...")
    print("Sending: 'Hello, how are you?'")
    response = await llm_tool.generate_response("Hello, how are you?")
    if response:
        print(f"✅ LLM Response: {response}")
    else:
        print("❌ Failed to get LLM response (Ollama might not be running)")


async def test_tool_manager():
    """Test the integrated tool manager."""
    print("\n🔧 Testing Tool Manager")
    print("-" * 30)
    
    tool_manager = ToolManager()
    
    test_cases = [
        "Hello, nice to meet you!",
        "What's the temperature in Tokyo?",
        "Tell me about artificial intelligence",
        "Good evening!",
        "How's the weather in New York?"
    ]
    
    for message in test_cases:
        print(f"\nProcessing: '{message}'")
        result = await tool_manager.process_message(message)
        print(f"Type: {result['type']}")
        print(f"Response: {result['content'][:100]}..." if len(result['content']) > 100 else f"Response: {result['content']}")


async def test_ai_agent():
    """Test the complete AI agent."""
    print("\n🤖 Testing AI Agent")
    print("-" * 30)
    
    agent = AIAgent()
    
    # Test health check
    print("Testing health check...")
    health = await agent.health_check()
    print(f"Health Status: {health['status']}")
    print(f"LLM: {health['services']['llm']}")
    print(f"Weather API: {health['services']['weather_api']}")
    
    # Test chat completions
    print("\nTesting chat completions...")
    messages = [
        [{"role": "user", "content": "Hello!"}],
        [{"role": "user", "content": "What's the temperature in London?"}],
        [{"role": "user", "content": "Tell me a joke"}]
    ]
    
    for msg_list in messages:
        print(f"\nSending: {msg_list[0]['content']}")
        response = await agent.process_chat_completion(msg_list)
        print(f"Response: {response['choices'][0]['message']['content']}")
        print(f"Agent Type: {response.get('metadata', {}).get('agent_type', 'unknown')}")


async def main():
    """Run all tests."""
    print("🚀 AI Agent Component Tests")
    print("=" * 40)
    
    try:
        # Test individual components
        await test_weather_tool()
        await test_llm_tool()
        await test_tool_manager()
        await test_ai_agent()
        
        print("\n✅ All tests completed!")
        print("\nNotes:")
        print("- If LLM tests fail, make sure Ollama is running and llama3.1:8b-instruct-q4_0 is installed")
        print("- Weather tests should work without additional setup")
        print("- To run the full server, use: python src/index.py")
        
    except KeyboardInterrupt:
        print("\n⛔ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
