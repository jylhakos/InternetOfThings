"""
# src/tools.py

External tools for the AI agent.

The Python script handles weather API integration and LLM communication.
It includes a WeatherTool for fetching weather data and an LLMTool for interacting with Ollama models.

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
    """Tool for communicating with Ollama LLM - Updated for Llama 4 Scout support."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama4:scout"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        self.chat_url = f"{base_url}/api/chat"
        # Support both Llama 3.1 and Llama 4 models
        self.is_llama4 = "llama4" in model.lower()
    
    def _create_llama4_prompt(self, user_message: str, system_message: str = "You are a helpful AI assistant.", 
                             tools: Optional[List[Dict]] = None) -> str:
        """
        Create a properly formatted Llama 4 prompt with tool support.
        
        Args:
            user_message: The user's message
            system_message: System instruction
            tools: Available tools for function calling
            
        Returns:
            Formatted prompt string
        """
        prompt = f"<|begin_of_text|><|header_start|>system<|header_end|>\n\n{system_message}"
        
        # Add tool definitions if provided
        if tools:
            prompt += "\n\nAvailable tools:"
            for tool in tools:
                prompt += f"\n- {tool['name']}: {tool['description']}"
        
        prompt += f"<|eot|><|header_start|>user<|header_end|>\n\n{user_message}<|eot|><|header_start|>assistant<|header_end|>\n\n"
        return prompt
    
    def _create_llama_legacy_prompt(self, user_message: str, system_message: str = "You are a helpful AI assistant.") -> str:
        """
        Create a properly formatted Llama 3.1 prompt for backward compatibility.
        
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
    
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for Llama 4 function calling."""
        return [
            {
                "name": "get_weather",
                "description": "Get current weather information for a specific city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name to get weather for"
                        },
                        "metric": {
                            "type": "string",
                            "description": "Temperature unit (celsius or fahrenheit)",
                            "default": "celsius"
                        }
                    },
                    "required": ["city"]
                }
            }
        ]
    
    async def generate_response(self, user_message: str, system_message: str = None, 
                               temperature: float = 0.7, use_tools: bool = True) -> Optional[str]:
        """
        Generate a response using Ollama with Llama 4 Scout or legacy Llama models.
        
        Args:
            user_message: The user's message
            system_message: Optional system message
            temperature: Sampling temperature (0.0 to 1.0)
            use_tools: Whether to enable tool calling for Llama 4
            
        Returns:
            Generated response or None if error
        """
        try:
            if system_message is None:
                system_message = "You are a helpful AI assistant. Be concise and friendly."
            
            # Use appropriate prompt format based on model
            if self.is_llama4:
                tools = self._get_available_tools() if use_tools else None
                prompt = self._create_llama4_prompt(user_message, system_message, tools)
            else:
                prompt = self._create_llama_legacy_prompt(user_message, system_message)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_ctx": 10000000 if self.is_llama4 else 4096,  # Use 10M context for Llama 4 Scout
                    "max_tokens": 512
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:  # Increased timeout for Llama 4
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                response_text = data.get("response", "").strip()
                
                # Check for tool calls in Llama 4 response
                if self.is_llama4 and use_tools and "[get_weather(" in response_text:
                    return await self._handle_tool_calls(response_text, user_message)
                
                return response_text
                
        except httpx.ConnectError:
            print("Error: Could not connect to Ollama. Make sure Ollama is running.")
            return None
        except httpx.TimeoutException:
            print("Error: Request to Ollama timed out.")
            return None
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return None
    
    async def _handle_tool_calls(self, response_text: str, original_message: str) -> str:
        """
        Handle tool calls from Llama 4 response.
        
        Args:
            response_text: The response containing tool calls
            original_message: Original user message
            
        Returns:
            Final response after tool execution
        """
        try:
            # Extract tool calls using regex
            import re
            tool_pattern = r'get_weather\(city="([^"]+)"(?:, metric="([^"]+)")?\)'
            matches = re.findall(tool_pattern, response_text)
            
            if not matches:
                return response_text
            
            # Execute weather tool calls
            from tools import WeatherTool
            weather_tool = WeatherTool()
            tool_results = []
            
            for match in matches:
                city = match[0]
                metric = match[1] if match[1] else "celsius"
                
                try:
                    weather_response = await weather_tool.get_temperature(city)
                    tool_results.append({
                        "response": weather_response if weather_response else f"Could not get weather for {city}"
                    })
                except Exception as e:
                    tool_results.append({
                        "response": f"Error getting weather for {city}: {str(e)}"
                    })
            
            # Format tool results for Llama 4
            tool_output = json.dumps(tool_results, indent=2)
            
            # Create follow-up prompt with tool results
            follow_up_prompt = f"""<|begin_of_text|><|header_start|>user<|header_end|>

{original_message}<|eot|><|header_start|>assistant<|header_end|>

{response_text}<|eot|><|header_start|>ipython<|header_end|>

{tool_output}<|eot|><|header_start|>assistant<|header_end|>

"""
            
            # Generate final response
            payload = {
                "model": self.model,
                "prompt": follow_up_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 512
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                return data.get("response", "").strip()
                
        except Exception as e:
            print(f"Error handling tool calls: {e}")
            return response_text  # Return original response on error
    
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
    """Manager class that orchestrates all tools with enhanced Llama 4 support."""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434", ollama_model: str = "llama4:scout"):
        self.weather_tool = WeatherTool()
        self.llm_tool = LLMTool(base_url=ollama_base_url, model=ollama_model)
        self.is_llama4 = "llama4" in ollama_model.lower()
    
    async def process_message(self, message: str, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Process a user message and return appropriate response with enhanced Llama 4 capabilities.
        
        Args:
            message: The user's message
            temperature: LLM temperature setting
            
        Returns:
            Dictionary with response data
        """
        try:
            message = message.strip()
            
            # For Llama 4, let the model handle tool detection and calling
            if self.is_llama4:
                return await self._process_with_llama4(message, temperature)
            
            # Legacy processing for Llama 3.x models
            return await self._process_with_legacy_llm(message, temperature)
        
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "type": "error",
                "content": "I encountered an error while processing your request. Please try again.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_with_llama4(self, message: str, temperature: float) -> Dict[str, Any]:
        """Process message with Llama 4 Scout's advanced capabilities."""
        try:
            # Enhanced system message for Llama 4
            system_msg = """You are an advanced AI assistant powered by Llama 4 Scout. You have access to tools for real-time information.

Available tools:
- get_weather(city, metric): Get current weather information for any city

When a user asks about weather, use the get_weather tool by responding with:
[get_weather(city="<city_name>", metric="celsius")]

For other queries, respond naturally and helpfully. Be concise but informative."""
            
            response = await self.llm_tool.generate_response(
                message, 
                system_message=system_msg, 
                temperature=temperature,
                use_tools=True
            )
            
            if response is None:
                response = "I'm here to help! I can answer questions, provide weather information for any city, or have a conversation. What would you like to know?"
            
            # Determine response type based on content
            response_type = "general"
            if "weather" in response.lower() or "temperature" in response.lower():
                response_type = "weather"
            elif any(greeting in response.lower() for greeting in ["hello", "hi", "hey", "good morning", "good afternoon"]):
                response_type = "greeting"
            
            return {
                "type": response_type,
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "model": "llama4-scout",
                "context_window": "10M tokens"
            }
            
        except Exception as e:
            print(f"Error in Llama 4 processing: {e}")
            return {
                "type": "error",
                "content": "I encountered an error while processing your request with Llama 4. Please try again.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_with_legacy_llm(self, message: str, temperature: float) -> Dict[str, Any]:
        """Process message with legacy Llama 3.x models (original logic)."""
        try:
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
                response = await self.llm_tool.generate_response(message, system_msg, temperature, use_tools=False)
                
                if response is None:
                    response = "Hello! I'm your AI assistant. How can I help you today? I can answer questions, provide weather information, or just have a conversation!"
                
                return {
                    "type": "greeting",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }
            
            # General LLM response for other queries
            else:
                response = await self.llm_tool.generate_response(message, temperature=temperature, use_tools=False)
                
                if response is None:
                    response = "I am your AI assistant. I can help you with various questions, provide weather information for different cities, or just have a conversation. What would you like to know?"
                
                return {
                    "type": "general",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Error in legacy processing: {e}")
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
    """Test the LLM tool functionality with Llama 4 support."""
    # Test both Llama 4 and legacy models
    models_to_test = ["llama4:scout", "llama3.1:8b-instruct-q4_0"]
    
    for model in models_to_test:
        print(f"\nTesting LLM Tool with {model}...")
        tool = LLMTool(model=model)
        
        # Test greeting detection (for legacy models)
        if not tool.is_llama4:
            greetings = ["Hello", "Hi there", "Good morning", "How are you?"]
            for greeting in greetings:
                is_greeting = await tool.is_greeting(greeting)
                print(f"'{greeting}' is greeting: {is_greeting}")
            
            # Test weather query detection (for legacy models)
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
        test_messages = [
            "Hello, how are you?",
            "What's the weather like in London?",
            "Explain quantum computing briefly"
        ]
        
        for message in test_messages:
            print(f"\nTesting message: '{message}'")
            response = await tool.generate_response(message, use_tools=tool.is_llama4)
            print(f"Response: {response}")
            print("-" * 40)


async def test_tool_manager():
    """Test the tool manager with both Llama 4 and legacy support."""
    models_to_test = [
        ("llama4:scout", "Llama 4 Scout"),
        ("llama3.1:8b-instruct-q4_0", "Llama 3.1")
    ]
    
    for model, model_name in models_to_test:
        print(f"\nTesting Tool Manager with {model_name}...")
        manager = ToolManager(ollama_model=model)
        
        test_messages = [
            "Hello, how are you?",
            "What's the temperature in London?",
            "Tell me about artificial intelligence",
            "Good morning!",
            "What's the weather like in Tokyo and Paris?"  # Multi-city for Llama 4
        ]
        
        for message in test_messages:
            result = await manager.process_message(message)
            print(f"Message: '{message}'")
            print(f"Type: {result['type']}")
            print(f"Response: {result['content']}")
            if 'model' in result:
                print(f"Model: {result['model']}")
            print("-" * 50)


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_weather_tool())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_llm_tool())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_tool_manager())
