"""
Test suite for validating MCP clients and servers from the quickstart-resources repository.

This test suite demonstrates how to validate MCP implementations from:
- https://github.com/modelcontextprotocol/quickstart-resources

Tests cover:
- Tool Discovery: Verify that list_tools() returns all expected tools
- Parameter Validation: Test cases with missing or invalid parameters
- Resource/Prompt Handling: Validate that read_resource() and prompt handling work
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from mcp import types
from mcp.server import Server


# ========================================
# Mock Weather Server (Based on quickstart-resources/weather-server-python)
# ========================================

class MockWeatherServer:
    """
    Mock implementation of the MCP Weather Server from quickstart-resources.
    Simulates the weather server for testing purposes.
    """
    
    def __init__(self):
        self.app = Server("weather-server")
        self._list_tools_handler = None
        self._call_tool_handler = None
        self._list_resources_handler = None
        self._read_resource_handler = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers for weather tools."""
        
        @self.app.list_tools()
        async def list_tools_impl() -> list[types.Tool]:
            """List available weather tools."""
            return [
                types.Tool(
                    name="get_forecast",
                    description="Get weather forecast for a location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name or coordinates"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days (1-7)",
                                "default": 3
                            }
                        },
                        "required": ["location"]
                    }
                ),
                types.Tool(
                    name="get_current_weather",
                    description="Get current weather for a location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name or coordinates"
                            }
                        },
                        "required": ["location"]
                    }
                )
            ]
        
        self._list_tools_handler = list_tools_impl
        
        @self.app.call_tool()
        async def call_tool_impl(name: str, arguments: dict) -> list[types.TextContent]:
            """Execute weather tool with given parameters."""
            
            if name == "get_forecast":
                location = arguments.get("location")
                days = arguments.get("days", 3)
                
                if not location:
                    raise ValueError("Location parameter is required")
                
                if not isinstance(days, int) or days < 1 or days > 7:
                    raise ValueError("Days must be an integer between 1 and 7")
                
                forecast_data = {
                    "location": location,
                    "days": days,
                    "forecast": [
                        {"day": i+1, "temp": 20+i, "conditions": "Sunny"}
                        for i in range(days)
                    ]
                }
                
                return [
                    types.TextContent(
                        type="text",
                        text=f"Weather forecast for {location} ({days} days): {forecast_data}"
                    )
                ]
            
            elif name == "get_current_weather":
                location = arguments.get("location")
                
                if not location:
                    raise ValueError("Location parameter is required")
                
                weather_data = {
                    "location": location,
                    "temperature": 22,
                    "conditions": "Partly Cloudy",
                    "humidity": 65,
                    "wind_speed": 15
                }
                
                return [
                    types.TextContent(
                        type="text",
                        text=f"Current weather in {location}: {weather_data}"
                    )
                ]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        self._call_tool_handler = call_tool_impl
        
        @self.app.list_resources()
        async def list_resources_impl() -> list[types.Resource]:
            """List available weather resources."""
            return [
                types.Resource(
                    uri="weather://docs/api-guide",
                    name="Weather API Guide",
                    description="Documentation for weather API usage",
                    mimeType="text/plain"
                )
            ]
        
        self._list_resources_handler = list_resources_impl
        
        @self.app.read_resource()
        async def read_resource_impl(uri: str) -> str:
            """Read weather resource content."""
            # Convert URI to string if it's a URL object
            uri_str = str(uri).strip()
            if uri_str == "weather://docs/api-guide":
                return """
Weather API Guide
=================
Use get_current_weather for real-time conditions.
Use get_forecast for multi-day predictions (1-7 days).
All temperatures in Celsius.
"""
            raise ValueError(f"Unknown resource: {uri_str}")
        
        self._read_resource_handler = read_resource_impl


# ========================================
# Test Cases: Tool Discovery
# ========================================

@pytest.mark.asyncio
async def test_tool_discovery_lists_all_tools():
    """
    Test Case 1: Tool Discovery
    Verify that list_tools() returns all expected tools from the weather server.
    """
    server = MockWeatherServer()
    tools = await server._list_tools_handler()
    
    # Verify we have exactly 2 tools
    assert len(tools) == 2, "Expected 2 weather tools"
    
    # Extract tool names
    tool_names = [tool.name for tool in tools]
    
    # Verify both expected tools are present
    assert "get_forecast" in tool_names, "get_forecast tool should be available"
    assert "get_current_weather" in tool_names, "get_current_weather tool should be available"
    
    # Verify tool schemas
    forecast_tool = next(t for t in tools if t.name == "get_forecast")
    assert "location" in forecast_tool.inputSchema["properties"]
    assert "days" in forecast_tool.inputSchema["properties"]
    assert "location" in forecast_tool.inputSchema["required"]
    
    current_tool = next(t for t in tools if t.name == "get_current_weather")
    assert "location" in current_tool.inputSchema["properties"]
    assert "location" in current_tool.inputSchema["required"]


@pytest.mark.asyncio
async def test_tool_discovery_returns_correct_schemas():
    """
    Test Case 2: Tool Schema Validation
    Verify that each tool has proper input schema definitions.
    """
    server = MockWeatherServer()
    tools = await server._list_tools_handler()
    
    for tool in tools:
        # Each tool must have a name and description
        assert tool.name, "Tool must have a name"
        assert tool.description, "Tool must have a description"
        
        # Each tool must have an inputSchema
        assert tool.inputSchema, "Tool must have inputSchema"
        assert "type" in tool.inputSchema, "Schema must specify type"
        assert tool.inputSchema["type"] == "object", "Schema type should be object"
        assert "properties" in tool.inputSchema, "Schema must have properties"


# ========================================
# Test Cases: Parameter Validation
# ========================================

@pytest.mark.asyncio
async def test_parameter_validation_missing_required():
    """
    Test Case 3: Parameter Validation - Missing Required Parameters
    Verify that tools reject requests with missing required parameters.
    """
    server = MockWeatherServer()
    
    # Test get_forecast without location
    with pytest.raises(ValueError, match="Location parameter is required"):
        await server._call_tool_handler("get_forecast", {"days": 3})
    
    # Test get_current_weather without location
    with pytest.raises(ValueError, match="Location parameter is required"):
        await server._call_tool_handler("get_current_weather", {})


@pytest.mark.asyncio
async def test_parameter_validation_invalid_values():
    """
    Test Case 4: Parameter Validation - Invalid Parameter Values
    Verify that tools validate parameter values and reject invalid inputs.
    """
    server = MockWeatherServer()
    
    # Test with days < 1
    with pytest.raises(ValueError, match="Days must be an integer between 1 and 7"):
        await server._call_tool_handler("get_forecast", {"location": "New York", "days": 0})
    
    # Test with days > 7
    with pytest.raises(ValueError, match="Days must be an integer between 1 and 7"):
        await server._call_tool_handler("get_forecast", {"location": "New York", "days": 10})
    
    # Test with non-integer days
    with pytest.raises(ValueError, match="Days must be an integer between 1 and 7"):
        await server._call_tool_handler("get_forecast", {"location": "New York", "days": "three"})


@pytest.mark.asyncio
async def test_parameter_validation_valid_requests():
    """
    Test Case 5: Parameter Validation - Valid Requests
    Verify that tools accept and process valid parameters correctly.
    """
    server = MockWeatherServer()
    
    # Test get_current_weather with valid location
    result = await server._call_tool_handler("get_current_weather", {"location": "San Francisco"})
    assert len(result) == 1
    assert "San Francisco" in result[0].text
    
    # Test get_forecast with valid parameters
    result = await server._call_tool_handler("get_forecast", {"location": "London", "days": 5})
    assert len(result) == 1
    assert "London" in result[0].text
    assert "5 days" in result[0].text


@pytest.mark.asyncio
async def test_parameter_validation_unknown_tool():
    """
    Test Case 6: Parameter Validation - Unknown Tool Name
    Verify that calling an unknown tool raises an appropriate error.
    """
    server = MockWeatherServer()
    
    with pytest.raises(ValueError, match="Unknown tool"):
        await server._call_tool_handler("get_weather_alerts", {"location": "Miami"})


# ========================================
# Test Cases: Resource/Prompt Handling
# ========================================

@pytest.mark.asyncio
async def test_resource_listing():
    """
    Test Case 7: Resource Discovery
    Verify that list_resources() returns all available resources.
    """
    server = MockWeatherServer()
    resources = await server._list_resources_handler()
    
    # Verify resources are available
    assert len(resources) > 0, "Server should provide at least one resource"
    
    # Verify resource structure
    for resource in resources:
        assert resource.uri, "Resource must have URI"
        assert resource.name, "Resource must have name"
        assert resource.description, "Resource must have description"


@pytest.mark.asyncio
async def test_resource_reading_valid_uri():
    """
    Test Case 8: Resource Reading - Valid URI
    Verify that read_resource() returns content for valid resource URIs.
    """
    server = MockWeatherServer()
    
    # Read the API guide resource
    content = await server._read_resource_handler("weather://docs/api-guide")
    
    # Verify content is returned
    assert content, "Resource content should not be empty"
    assert "Weather API Guide" in content
    assert "get_current_weather" in content
    assert "get_forecast" in content


@pytest.mark.asyncio
async def test_resource_reading_invalid_uri():
    """
    Test Case 9: Resource Reading - Invalid URI
    Verify that reading an invalid resource URI raises an error.
    """
    server = MockWeatherServer()
    
    # Attempt to read non-existent resource
    with pytest.raises(ValueError, match="Unknown resource"):
        await server._read_resource_handler("weather://docs/nonexistent")


# ========================================
# Integration Test: Full Client-Server Flow
# ========================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_mcp_client_server_flow():
    """
    Test Case 10: Integration Test - Full MCP Client-Server Flow
    Simulates a complete interaction between MCP client and weather server.
    Tests the entire flow: discovery -> tool call -> resource access
    """
    server = MockWeatherServer()
    
    # Step 1: Tool Discovery
    tools = await server._list_tools_handler()
    assert len(tools) == 2, "Should discover 2 tools"
    
    # Step 2: Call a tool with valid parameters
    result = await server._call_tool_handler("get_current_weather", {"location": "Boston"})
    assert len(result) == 1
    assert "Boston" in result[0].text
    
    # Step 3: Access resources
    resources = await server._list_resources_handler()
    assert len(resources) > 0, "Should have resources available"
    
    content = await server._read_resource_handler(resources[0].uri)
    assert content, "Should read resource content successfully"
    
    print("✅ Full MCP client-server flow test passed!")


# ========================================
# Test Case: Default Parameter Handling
# ========================================

@pytest.mark.asyncio
async def test_default_parameter_handling():
    """
    Test Case 11: Default Parameters
    Verify that tools use default values when optional parameters are not provided.
    """
    server = MockWeatherServer()
    
    # Call get_forecast without specifying days (should use default: 3)
    result = await server._call_tool_handler("get_forecast", {"location": "Chicago"})
    assert len(result) == 1
    assert "Chicago" in result[0].text
    # The default is 3 days, verify in response
    assert "3 days" in result[0].text or "'days': 3" in result[0].text


# ========================================
# Test Helpers
# ========================================

def test_virtual_environment_active():
    """
    Test Case 12: Virtual Environment Check
    Verify that tests are running in the virtual environment.
    """
    import sys
    import os
    
    # Check if running in virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    assert venv_path is not None, "Tests must run in virtual environment"
    assert 'venv' in sys.prefix, "Python interpreter should be from venv"
    
    print(f"✅ Running in virtual environment: {venv_path}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
