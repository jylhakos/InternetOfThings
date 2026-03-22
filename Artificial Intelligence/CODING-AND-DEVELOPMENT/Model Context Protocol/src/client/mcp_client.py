#!/usr/bin/env python3
"""
Basic MCP Client Example
This demonstrates how to connect to an MCP server and use its tools
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_client():
    """Connect to MCP server and call tools"""
    
    # Configure server parameters
    server_params = StdioServerParameters(
        command="python3",
        args=["src/server/mcp_server_stdio.py"],
        env=None
    )
    
    print("Connecting to MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            print("\n✓ Connected to MCP server")
            
            # List available tools
            tools_result = await session.list_tools()
            print(f"\n📋 Available tools: {len(tools_result.tools)}")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Call the weather tool
            print("\n🔧 Calling get_weather tool...")
            result = await session.call_tool(
                "get_weather",
                arguments={
                    "location": "San Francisco",
                    "units": "celsius"
                }
            )
            
            print(f"\n📊 Result:")
            for content in result.content:
                print(content.text)


async def run_sse_client():
    """Connect to SSE-based MCP server"""
    import httpx
    
    print("\nConnecting to SSE MCP server...")
    print("Note: Make sure mcp_server_sse.py is running on port 8000")
    
    # SSE client implementation would go here
    # This is a placeholder showing the concept
    async with httpx.AsyncClient() as client:
        print("SSE connection would be established here")
        # Implementation details depend on the SSE transport specifics


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Client Example")
    print("=" * 60)
    
    asyncio.run(run_client())
