"""
Weather Forecaster Agent Example

This example demonstrates how to integrate the Strands Agents SDK with tool use,
specifically using the http_request tool to build a weather forecasting agent 
that connects with the National Weather Service API.
"""

from strands import Agent
from strands_tools import http_request

# Define a weather-focused system prompt
WEATHER_SYSTEM_PROMPT = """You are a weather assistant with HTTP capabilities. You can:

1. Make HTTP requests to the National Weather Service API
2. Process and display weather forecast data
3. Provide weather information for locations in the United States

When retrieving weather information:
1. First get the coordinates or grid information using https://api.weather.gov/points/{latitude},{longitude} or https://api.weather.gov/points/{zipcode}
2. Then use the returned forecast URL to get the actual forecast

When displaying responses:
- Format weather data in a human-readable way
- Highlight important information like temperature, precipitation, and alerts
- Handle errors appropriately
- Convert technical terms to user-friendly language

Always explain the weather conditions clearly and provide context for the forecast.
"""

# Create an agent with HTTP capabilities
weather_agent = Agent(
    system_prompt=WEATHER_SYSTEM_PROMPT,
    tools=[http_request],  # Explicitly enable http_request tool
)

def main():
    """Main function to run the weather forecaster agent."""
    print("Weather Forecaster Agent")
    print("=" * 50)
    print("Ask me about weather conditions in the United States!")
    print("Examples:")
    print("  - What's the weather like in Seattle?")
    print("  - Will it rain tomorrow in Miami?")
    print("  - Compare temperature in New York and Chicago")
    print("=" * 50)
    
    while True:
        try:
            # Get user input
            user_query = input("\nYour question (or 'quit' to exit): ")
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_query.strip():
                continue
            
            # Get response from the agent
            print("\nAgent is processing your request...\n")
            response = weather_agent(user_query)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again with a different question.\n")

if __name__ == "__main__":
    main()
