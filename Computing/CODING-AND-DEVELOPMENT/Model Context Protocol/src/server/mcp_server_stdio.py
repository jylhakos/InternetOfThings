#!/usr/bin/env python3
"""
Basic MCP Server using STDIO transport
This server exposes a simple weather tool as an example
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Create server instance
app = Server("example-weather-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_weather",
            description="Get weather information for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or location"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature units",
                        "default": "celsius"
                    }
                },
                "required": ["location"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    if name == "get_weather":
        location = arguments.get("location", "Unknown")
        units = arguments.get("units", "celsius")
        
        # Simulated weather data
        temp = 22 if units == "celsius" else 72
        weather_data = {
            "location": location,
            "temperature": temp,
            "units": units,
            "condition": "Sunny",
            "humidity": "65%"
        }
        
        return [
            TextContent(
                type="text",
                text=json.dumps(weather_data, indent=2)
            )
        ]
    
    raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
