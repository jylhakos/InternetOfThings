"""
Weather data service for fetching weather information
"""
import os
import asyncio
from datetime import datetime
from typing import Dict, Any

import httpx
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    def __init__(self):
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Schiphol Airport coordinates (EHAM)
        self.schiphol_lat = 52.31
        self.schiphol_lon = 4.76
    
    async def get_schiphol_weather(self) -> Dict[str, Any]:
        """Get current weather data for Schiphol Airport"""
        if not self.openweather_api_key:
            # Return mock data if no API key is provided
            return self._get_mock_weather_data()
        
        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/weather"
                params = {
                    "lat": self.schiphol_lat,
                    "lon": self.schiphol_lon,
                    "appid": self.openweather_api_key,
                    "units": "metric"
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                return self._format_weather_data(data)
                
            except httpx.HTTPError as e:
                print(f"HTTP error occurred: {e}")
                return self._get_mock_weather_data()
            except Exception as e:
                print(f"Error fetching weather data: {e}")
                return self._get_mock_weather_data()
    
    def _format_weather_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw weather data from OpenWeatherMap"""
        main = raw_data.get("main", {})
        weather = raw_data.get("weather", [{}])[0]
        wind = raw_data.get("wind", {})
        
        return {
            "temperature": round(main.get("temp", 0), 1),
            "humidity": main.get("humidity", 0),
            "pressure": main.get("pressure", 0),
            "wind_speed": round(wind.get("speed", 0), 1),
            "wind_direction": wind.get("deg", 0),
            "description": weather.get("description", "Unknown"),
            "condition": weather.get("main", "Unknown"),
            "visibility": raw_data.get("visibility", 0) / 1000 if raw_data.get("visibility") else 10.0,  # Convert to km
            "timestamp": datetime.now().isoformat(),
            "location": "Amsterdam Airport Schiphol"
        }
    
    def _get_mock_weather_data(self) -> Dict[str, Any]:
        """Return mock weather data when API is not available"""
        import random
        
        conditions = ["Clear", "Clouds", "Rain", "Snow", "Mist"]
        descriptions = ["clear sky", "partly cloudy", "light rain", "light snow", "mist"]
        
        condition = random.choice(conditions)
        description = random.choice(descriptions)
        
        return {
            "temperature": round(random.uniform(5, 25), 1),
            "humidity": random.randint(40, 90),
            "pressure": random.randint(1005, 1025),
            "wind_speed": round(random.uniform(5, 20), 1),
            "wind_direction": random.randint(0, 360),
            "description": description,
            "condition": condition,
            "visibility": round(random.uniform(5, 15), 1),
            "timestamp": datetime.now().isoformat(),
            "location": "Amsterdam Airport Schiphol (Mock Data)"
        }
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    def __init__(self):
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.checkwx_api_key = os.getenv("CHECKWX_API_KEY")
        
        # Schiphol Airport coordinates
        self.schiphol_lat = 52.31
        self.schiphol_lon = 4.76
        self.schiphol_icao = "EHAM"
        
        # Base URLs
        self.openweather_base_url = "https://api.openweathermap.org/data/2.5"
        self.open_meteo_base_url = "https://api.open-meteo.com/v1"
        self.checkwx_base_url = "https://api.checkwx.com"
    
    async def get_schiphol_weather(self) -> Dict[str, Any]:
        """Get weather data for Schiphol Airport"""
        weather_data = {
            "location": "Amsterdam Airport Schiphol (EHAM)",
            "coordinates": {
                "latitude": self.schiphol_lat,
                "longitude": self.schiphol_lon
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": "multiple_apis"
        }
        
        # Try different weather APIs
        try:
            # Try Open-Meteo first (free, no API key required)
            meteo_data = await self._fetch_open_meteo_weather()
            if meteo_data:
                weather_data.update(meteo_data)
                weather_data["source"] = "open-meteo"
                return weather_data
        except Exception as e:
            print(f"Open-Meteo API error: {e}")
        
        try:
            # Try OpenWeatherMap if API key is available
            if self.openweather_api_key:
                openweather_data = await self._fetch_openweather_data()
                if openweather_data:
                    weather_data.update(openweather_data)
                    weather_data["source"] = "openweathermap"
                    return weather_data
        except Exception as e:
            print(f"OpenWeatherMap API error: {e}")
        
        try:
            # Try CheckWX if API key is available
            if self.checkwx_api_key:
                checkwx_data = await self._fetch_checkwx_data()
                if checkwx_data:
                    weather_data.update(checkwx_data)
                    weather_data["source"] = "checkwx"
                    return weather_data
        except Exception as e:
            print(f"CheckWX API error: {e}")
        
        # Fallback to mock data if all APIs fail
        weather_data.update(self._get_mock_weather_data())
        weather_data["source"] = "mock_data"
        return weather_data
    
    async def _fetch_open_meteo_weather(self) -> Optional[Dict[str, Any]]:
        """Fetch weather data from Open-Meteo API (free, no API key required)"""
        url = f"{self.open_meteo_base_url}/forecast"
        params = {
            "latitude": self.schiphol_lat,
            "longitude": self.schiphol_lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code",
            "timezone": "Europe/Amsterdam"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            weather_code = current.get("weather_code", 0)
            
            return {
                "temperature": current.get("temperature_2m", 0),
                "humidity": current.get("relative_humidity_2m", 0),
                "wind_speed": current.get("wind_speed_10m", 0),
                "wind_direction": current.get("wind_direction_10m", 0),
                "weather_condition": self._weather_code_to_condition(weather_code),
                "weather_code": weather_code
            }
    
    async def _fetch_openweather_data(self) -> Optional[Dict[str, Any]]:
        """Fetch weather data from OpenWeatherMap API"""
        url = f"{self.openweather_base_url}/weather"
        params = {
            "lat": self.schiphol_lat,
            "lon": self.schiphol_lon,
            "appid": self.openweather_api_key,
            "units": "metric"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            main = data.get("main", {})
            wind = data.get("wind", {})
            weather = data.get("weather", [{}])[0]
            
            return {
                "temperature": main.get("temp", 0),
                "humidity": main.get("humidity", 0),
                "wind_speed": wind.get("speed", 0),
                "wind_direction": wind.get("deg", 0),
                "weather_condition": weather.get("main", "Unknown"),
                "description": weather.get("description", "")
            }
    
    async def _fetch_checkwx_data(self) -> Optional[Dict[str, Any]]:
        """Fetch weather data from CheckWX API"""
        url = f"{self.checkwx_base_url}/metar/{self.schiphol_icao}/decoded"
        headers = {
            "X-API-Key": self.checkwx_api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results") > 0:
                metar_data = data["data"][0]
                
                return {
                    "temperature": metar_data.get("temperature", {}).get("celsius", 0),
                    "humidity": metar_data.get("humidity", {}).get("percent", 0),
                    "wind_speed": metar_data.get("wind", {}).get("speed_kts", 0),
                    "wind_direction": metar_data.get("wind", {}).get("degrees", 0),
                    "weather_condition": self._parse_checkwx_conditions(metar_data),
                    "visibility": metar_data.get("visibility", {}).get("meters", 0)
                }
    
    def _weather_code_to_condition(self, code: int) -> str:
        """Convert Open-Meteo weather code to readable condition"""
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
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")
    
    def _parse_checkwx_conditions(self, data: Dict[str, Any]) -> str:
        """Parse CheckWX METAR data for weather conditions"""
        conditions = data.get("conditions", [])
        if conditions:
            return conditions[0].get("text", "Unknown")
        
        # Fallback based on other data
        if data.get("clouds"):
            return "Cloudy"
        return "Clear"
    
    def _get_mock_weather_data(self) -> Dict[str, Any]:
        """Fallback mock weather data"""
        return {
            "temperature": 15.5,
            "humidity": 75,
            "wind_speed": 12.5,
            "wind_direction": 240,
            "weather_condition": "Partly cloudy",
            "description": "Mock weather data - API unavailable"
        }

# Test the weather service
async def test_weather_service():
    """Test the weather service"""
    service = WeatherService()
    weather_data = await service.get_schiphol_weather()
    print("Weather data:", weather_data)

if __name__ == "__main__":
    asyncio.run(test_weather_service())