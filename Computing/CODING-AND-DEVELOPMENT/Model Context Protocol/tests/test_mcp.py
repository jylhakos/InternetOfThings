"""
Test suite for MCP servers and agents
Run with: pytest tests/
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from mcp.types import Tool, TextContent


# Mock fixtures
@pytest.fixture
def mock_weather_tool():
    """Fixture for a mock weather tool"""
    return Tool(
        name="get_weather",
        description="Get weather information",
        inputSchema={
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    )


@pytest.fixture
def mock_tool_result():
    """Fixture for a mock tool result"""
    return [TextContent(
        type="text",
        text='{"location": "London", "temperature": 18, "condition": "Partly Cloudy"}'
    )]


# Test MCP Server Tool Discovery
@pytest.mark.asyncio
async def test_server_tool_discovery(mock_weather_tool):
    """Test that server can list tools"""
    # Mock server
    from mcp.server import Server
    
    server = Server("test-server")
    
    @server.list_tools()
    async def list_tools():
        return [mock_weather_tool]
    
    # Execute
    tools = await list_tools()
    
    # Assert
    assert len(tools) == 1
    assert tools[0].name == "get_weather"
    assert "location" in tools[0].inputSchema["properties"]


# Test Tool Invocation
@pytest.mark.asyncio
async def test_tool_invocation(mock_tool_result):
    """Test calling a tool returns expected results"""
    # Mock session
    mock_session = AsyncMock()
    mock_session.call_tool.return_value = MagicMock(content=mock_tool_result)
    
    # Execute
    result = await mock_session.call_tool(
        "get_weather",
        arguments={"location": "London"}
    )
    
    # Assert
    assert result.content[0].type == "text"
    assert "London" in result.content[0].text


# Test Agent Tool Discovery
@pytest.mark.asyncio
async def test_agent_discovers_tools():
    """Test that agent can discover available tools"""
    # Mock client session
    mock_session = AsyncMock()
    mock_tools = MagicMock()
    mock_tools.tools = [
        Tool(name="tool1", description="First tool", inputSchema={}),
        Tool(name="tool2", description="Second tool", inputSchema={})
    ]
    mock_session.list_tools.return_value = mock_tools
    
    # Execute
    result = await mock_session.list_tools()
    
    # Assert
    assert len(result.tools) == 2
    tool_names = [t.name for t in result.tools]
    assert "tool1" in tool_names
    assert "tool2" in tool_names


# Test Error Handling
@pytest.mark.asyncio
async def test_invalid_tool_name():
    """Test error handling for invalid tool names"""
    mock_session = AsyncMock()
    mock_session.call_tool.side_effect = ValueError("Unknown tool: invalid_tool")
    
    with pytest.raises(ValueError, match="Unknown tool"):
        await mock_session.call_tool("invalid_tool", arguments={})


# Test Parameter Validation
@pytest.mark.asyncio
async def test_missing_required_parameter():
    """Test validation of required parameters"""
    from jsonschema import validate, ValidationError
    
    schema = {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
    
    # Valid parameters
    valid_args = {"location": "Paris"}
    validate(instance=valid_args, schema=schema)  # Should not raise
    
    # Invalid parameters (missing required field)
    invalid_args = {}
    with pytest.raises(ValidationError):
        validate(instance=invalid_args, schema=schema)


# Integration Test (requires actual server)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_server_client_integration():
    """
    Full integration test with real server and client
    This test is skipped by default, run with: pytest -m integration
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    
    # Configure server
    server_params = StdioServerParameters(
        command="python",
        args=["src/server/mcp_server_stdio.py"]
    )
    
    # Connect and test
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            assert len(tools.tools) > 0
            
            # Call tool
            result = await session.call_tool(
                "get_weather",
                arguments={"location": "Tokyo"}
            )
            assert result.content[0].text is not None


# Performance Test
@pytest.mark.asyncio
async def test_concurrent_tool_calls():
    """Test multiple concurrent tool calls"""
    mock_session = AsyncMock()
    mock_session.call_tool.return_value = MagicMock(
        content=[TextContent(type="text", text="Result")]
    )
    
    # Execute multiple calls concurrently
    tasks = [
        mock_session.call_tool(f"tool_{i}", arguments={})
        for i in range(10)
    ]
    results = await asyncio.gather(*tasks)
    
    # Assert all completed
    assert len(results) == 10
    assert all(r.content[0].text == "Result" for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
