"""
External tools for the AI agent.

The Python script handles weather API integration and LLM communication.
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime


class WeatherTool:
    """Tool for fetching weather information using Open-Meteo API."""
    
    def __init__(self):
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        
    async def get_coordinates(self, city_name: str) -> Optional[Dict[str, float]]:
        """
        Get latitude and longitude for a city using Open-Meteo Geocoding API.
        
        Args:
            city_name: Name of the city
            
        Returns:
            Dictionary with 'latitude' and 'longitude' keys, or None if not found
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "name": city_name,
                    "count": 1,
                    "language": "en",
                    "format": "json"
                }
                response = await client.get(self.geocoding_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    result = data["results"][0]
                    return {
                        "latitude": result["latitude"],
                        "longitude": result["longitude"],
                        "name": result["name"],
                        "country": result.get("country", "")
                    }
                return None
                
        except Exception as e:
            print(f"Error getting coordinates for {city_name}: {e}")
            return None
    
    async def get_weather(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Get current weather data using Open-Meteo API.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with weather data or None if error
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current_weather": True,
                    "timezone": "auto"
                }
                response = await client.get(self.weather_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                return data.get("current_weather")
                
        except Exception as e:
            print(f"Error getting weather data: {e}")
            return None
    
    async def get_temperature(self, city_name: str) -> Optional[str]:
        """
        Get current temperature for a city.
        
        Args:
            city_name: Name of the city
            
        Returns:
            Formatted temperature string or None if error
        """
        try:
            # Get coordinates
            coords = await self.get_coordinates(city_name)
            if not coords:
                return f"Sorry, I couldn't find the location '{city_name}'. Please check the city name and try again."
            
            # Get weather data
            weather = await self.get_weather(coords["latitude"], coords["longitude"])
            if not weather:
                return f"Sorry, I couldn't retrieve weather data for {city_name}."
            
            temperature = weather.get("temperature", "Unknown")
            weather_code = weather.get("weathercode", 0)
            
            # Basic weather code interpretation
            weather_description = self._interpret_weather_code(weather_code)
            
            return (f"The current temperature in {coords['name']}, {coords['country']} "
                   f"is {temperature}°C. Weather conditions: {weather_description}")
            
        except Exception as e:
            print(f"Error getting temperature for {city_name}: {e}")
            return f"Sorry, I encountered an error while fetching weather data for {city_name}."
    
    def _interpret_weather_code(self, code: int) -> str:
        """Interpret WMO weather code to description."""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")


class LLMTool:
    """Tool for communicating with Ollama LLM."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b-instruct-q4_0"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
    
    def _create_llama_prompt(self, user_message: str, system_message: str = "You are a helpful AI assistant.") -> str:
        """
        Create a properly formatted Llama-3.1 prompt.
        
        Args:
            user_message: The user's message
            system_message: System instruction
            
        Returns:
            Formatted prompt string
        """
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    async def generate_response(self, user_message: str, system_message: str = None, temperature: float = 0.7) -> Optional[str]:
        """
        Generate a response using Ollama.
        
        Args:
            user_message: The user's message
            system_message: Optional system message
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated response or None if error
        """
        try:
            if system_message is None:
                system_message = "You are a helpful AI assistant. Be concise and friendly."
            
            prompt = self._create_llama_prompt(user_message, system_message)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_tokens": 512
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                return data.get("response", "").strip()
                
        except httpx.ConnectError:
            print("Error: Could not connect to Ollama. Make sure Ollama is running.")
            return None
        except httpx.TimeoutException:
            print("Error: Request to Ollama timed out.")
            return None
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return None
    
    async def is_greeting(self, message: str) -> bool:
        """
        Check if a message is a greeting using pattern matching.
        
        Args:
            message: The message to check
            
        Returns:
            True if message is a greeting
        """
        greeting_patterns = [
            r'\bhello\b', r'\bhi\b', r'\bhey\b', r'\bgreetings\b',
            r'\bgood morning\b', r'\bgood afternoon\b', r'\bgood evening\b',
            r'\bhowdy\b', r'\bsup\b', r'\bwhat\'s up\b', r'\bhow are you\b',
            r'\bhow do you do\b', r'\bnice to meet you\b'
        ]
        
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in greeting_patterns)
    
    async def extract_city_name(self, message: str) -> Optional[str]:
        """
        Extract city name from a weather-related message.
        
        Args:
            message: The message to analyze
            
        Returns:
            Extracted city name or None
        """
        # Simple pattern matching for common weather query formats
        weather_patterns = [
            r'temperature in ([^?]+)',
            r'weather in ([^?]+)',
            r'temp in ([^?]+)',
            r'how.*warm.*in ([^?]+)',
            r'how.*cold.*in ([^?]+)',
            r'climate in ([^?]+)'
        ]
        
        message_lower = message.lower().strip()
        
        for pattern in weather_patterns:
            match = re.search(pattern, message_lower)
            if match:
                city = match.group(1).strip()
                # Clean up common words
                city = re.sub(r'\b(the|a|an|today|now|currently)\b', '', city).strip()
                return city.title()
        
        return None
    
    async def is_weather_query(self, message: str) -> bool:
        """
        Check if a message is asking about weather.
        
        Args:
            message: The message to check
            
        Returns:
            True if message is weather-related
        """
        weather_keywords = [
            'temperature', 'temp', 'weather', 'hot', 'cold', 'warm', 'cool',
            'celsius', 'fahrenheit', 'degrees', 'climate', 'forecast'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in weather_keywords)


class ToolManager:
    """Manager class that orchestrates all tools."""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434", ollama_model: str = "llama3.1:8b-instruct-q4_0"):
        self.weather_tool = WeatherTool()
        self.llm_tool = LLMTool(base_url=ollama_base_url, model=ollama_model)
    
    async def process_message(self, message: str, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Process a user message and return appropriate response.
        
        Args:
            message: The user's message
            temperature: LLM temperature setting
            
        Returns:
            Dictionary with response data
        """
        try:
            message = message.strip()
            
            # Check if it's a weather query
            if await self.llm_tool.is_weather_query(message):
                city = await self.llm_tool.extract_city_name(message)
                if city:
                    response = await self.weather_tool.get_temperature(city)
                    return {
                        "type": "weather",
                        "content": response,
                        "city": city,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    response = "I'd be happy to help with weather information! Please specify a city name, for example: 'What's the temperature in London?'"
                    return {
                        "type": "weather_clarification",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Check if it's a greeting
            elif await self.llm_tool.is_greeting(message):
                system_msg = "You are a friendly AI assistant. Respond to greetings warmly and offer to help."
                response = await self.llm_tool.generate_response(message, system_msg, temperature)
                
                if response is None:
                    response = "Hello! I'm your AI assistant. How can I help you today? I can answer questions, provide weather information, or just have a conversation!"
                
                return {
                    "type": "greeting",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }
            
            # General LLM response for other queries
            else:
                response = await self.llm_tool.generate_response(message, temperature=temperature)
                
                if response is None:
                    response = "I am your AI assistant. I can help you with various questions, provide weather information for different cities, or just have a conversation. What would you like to know?"
                
                return {
                    "type": "general",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "type": "error",
                "content": "I encountered an error while processing your request. Please try again.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Utility functions for testing
async def test_weather_tool():
    """Test the weather tool functionality."""
    tool = WeatherTool()
    
    print("Testing Weather Tool...")
    
    # Test coordinates
    coords = await tool.get_coordinates("London")
    print(f"London coordinates: {coords}")
    
    # Test weather
    if coords:
        weather = await tool.get_weather(coords["latitude"], coords["longitude"])
        print(f"London weather: {weather}")
    
    # Test temperature
    temp = await tool.get_temperature("Paris")
    print(f"Paris temperature: {temp}")


async def test_llm_tool():
    """Test the LLM tool functionality."""
    tool = LLMTool()
    
    print("Testing LLM Tool...")
    
    # Test greeting detection
    greetings = ["Hello", "Hi there", "Good morning", "How are you?"]
    for greeting in greetings:
        is_greeting = await tool.is_greeting(greeting)
        print(f"'{greeting}' is greeting: {is_greeting}")
    
    # Test weather query detection
    weather_queries = [
        "What's the temperature in London?",
        "How's the weather in Paris?",
        "Tell me about Tokyo weather"
    ]
    for query in weather_queries:
        is_weather = await tool.is_weather_query(query)
        city = await tool.extract_city_name(query)
        print(f"'{query}' is weather: {is_weather}, city: {city}")
    
    # Test LLM response
    response = await tool.generate_response("Hello, how are you?")
    print(f"LLM response: {response}")


async def test_tool_manager():
    """Test the tool manager."""
    manager = ToolManager()
    
    print("Testing Tool Manager...")
    
    test_messages = [
        "Hello, how are you?",
        "What's the temperature in London?",
        "Tell me about artificial intelligence",
        "Good morning!"
    ]
    
    for message in test_messages:
        result = await manager.process_message(message)
        print(f"Message: '{message}'")
        print(f"Response: {result}")
        print("-" * 50)


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_weather_tool())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_llm_tool())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_tool_manager())
