"""
Unit tests for the weather tool.

These tests verify weather API integration and tool creation.
Run with: pytest tests/test_weather.py -v
"""

import pytest
import os
from unittest.mock import Mock, patch


class TestWeatherFunction:
    """Test the get_weather function."""
    
    def test_get_weather_no_api_key(self, monkeypatch):
        """Test behavior when API key is not set."""
        from src.weather_tool import get_weather
        
        # Remove API key if exists
        monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
        
        result = get_weather("London")
        assert "Weather API key not found" in result
    
    @patch('src.weather_tool.requests.get')
    def test_get_weather_success(self, mock_get, mock_weather_api_key):
        """Test successful weather API response."""
        from src.weather_tool import get_weather
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "cod": 200,
            "weather": [{"description": "clear sky"}],
            "main": {
                "temp": 20.5,
                "feels_like": 19.0,
                "humidity": 65
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_weather("Paris")
        
        assert "Paris" in result
        assert "clear sky" in result
        assert "20.5°C" in result
        assert "humidity" in result.lower()
    
    @patch('src.weather_tool.requests.get')
    def test_get_weather_city_not_found(self, mock_get, mock_weather_api_key):
        """Test handling of invalid city name."""
        from src.weather_tool import get_weather
        
        # Mock city not found response
        mock_response = Mock()
        mock_response.json.return_value = {
            "cod": 404,
            "message": "city not found"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_weather("InvalidCityName123")
        
        assert "Could not retrieve weather" in result
    
    @patch('src.weather_tool.requests.get')
    def test_get_weather_timeout(self, mock_get, mock_weather_api_key):
        """Test handling of API timeout."""
        from src.weather_tool import get_weather
        import requests
        
        # Mock timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = get_weather("Tokyo")
        
        assert "timed out" in result.lower()
    
    @patch('src.weather_tool.requests.get')
    def test_get_weather_network_error(self, mock_get, mock_weather_api_key):
        """Test handling of network errors."""
        from src.weather_tool import get_weather
        import requests
        
        # Mock connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        result = get_weather("Berlin")
        
        assert "Error connecting" in result


class TestWeatherTool:
    """Test the weather tool creation."""
    
    def test_create_weather_tool(self):
        """Test that weather tool can be created."""
        from src.weather_tool import create_weather_tool
        
        tool = create_weather_tool()
        
        assert tool is not None
        assert hasattr(tool, 'metadata'), "Tool missing metadata"
        assert tool.metadata.name == "weather_tool"
    
    def test_weather_tool_has_description(self):
        """Test that weather tool has a description."""
        from src.weather_tool import create_weather_tool
        
        tool = create_weather_tool()
        
        assert hasattr(tool.metadata, 'description')
        assert len(tool.metadata.description) > 0
        assert "weather" in tool.metadata.description.lower()
    
    @patch('src.weather_tool.requests.get')
    def test_weather_tool_callable(self, mock_get, mock_weather_api_key):
        """Test that the weather tool can be called."""
        from src.weather_tool import create_weather_tool
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "cod": 200,
            "weather": [{"description": "sunny"}],
            "main": {"temp": 25, "feels_like": 24, "humidity": 50}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = create_weather_tool()
        result = tool.fn("Madrid")
        
        assert "Madrid" in result
        assert "sunny" in result


@pytest.mark.integration
class TestWeatherIntegration:
    """Integration tests for weather functionality."""
    
    @pytest.mark.skipif(
        not os.getenv("OPENWEATHER_API_KEY"),
        reason="Requires OPENWEATHER_API_KEY environment variable"
    )
    def test_real_weather_api_call(self):
        """Test actual weather API call (requires valid API key)."""
        from src.weather_tool import get_weather
        
        result = get_weather("London")
        
        # Should not contain error messages
        assert "Error" not in result
        assert "not found" not in result
        assert "London" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
