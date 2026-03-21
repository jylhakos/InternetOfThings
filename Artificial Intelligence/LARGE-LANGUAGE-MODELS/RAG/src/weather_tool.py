"""
Weather API Tool for LlamaIndex Agent

This module provides a weather tool that can be used by LlamaIndex agents
to fetch current weather information for any city.
"""

import os
import requests
from llama_index.core.tools import FunctionTool


def get_weather(location: str) -> str:
    """
    Get current weather information for a given location.
    
    Args:
        location (str): City name (e.g., 'Paris', 'Tokyo', 'New York')
        
    Returns:
        str: Weather description with temperature, or error message
        
    Example:
        >>> get_weather("London")
        "The weather in London is clear sky with a temperature of 15.5°C."
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        return "Weather API key not found. Please set OPENWEATHER_API_KEY in .env file."
    
    try:
        # OpenWeatherMap current weather API endpoint
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("cod") == 200:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            
            return (
                f"The weather in {location} is {weather_desc} with a temperature of {temp}°C "
                f"(feels like {feels_like}°C). Humidity: {humidity}%."
            )
        else:
            return f"Could not retrieve weather for {location}: {data.get('message', 'Unknown error')}"
            
    except requests.exceptions.Timeout:
        return f"Request timed out while fetching weather for {location}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to weather API: {str(e)}"


def create_weather_tool() -> FunctionTool:
    """
    Create a LlamaIndex FunctionTool for weather queries.
    
    Returns:
        FunctionTool: A tool that can be used by LlamaIndex agents
        
    Example:
        >>> weather_tool = create_weather_tool()
        >>> agent = ReActAgent.from_tools([weather_tool], llm=llm)
    """
    return FunctionTool.from_defaults(
        fn=get_weather,
        name="weather_tool",
        description=(
            "Useful for getting the current weather for a given location. "
            "Input should be a city name like 'Paris' or 'New York'."
        )
    )


if __name__ == "__main__":
    # Test the weather function
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing weather tool...")
    print(get_weather("London"))
    print(get_weather("Tokyo"))
