#!/usr/bin/env python3
"""
MCP Server using SSE (Server-Sent Events) transport
Run this server and connect to it via HTTP on port 8000
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, Resource, ResourceTemplate
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route


# Create server instance
mcp_server = Server("example-sse-server")


@mcp_server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="resource://docs/mcp-guide",
            name="MCP Getting Started Guide",
            mimeType="text/plain",
            description="Introduction to Model Context Protocol"
        )
    ]


@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    if uri == "resource://docs/mcp-guide":
        return """
        Model Context Protocol (MCP) Getting Started
        ============================================
        
        MCP allows AI agents to connect to external data sources and tools.
        
        Key Concepts:
        - Resources: Read-only data sources
        - Tools: Functions agents can invoke
        - Prompts: Reusable templates
        
        Architecture:
        - Client: Runs within host application
        - Server: Exposes tools and resources
        - Transport: STDIO or SSE communication
        """
    raise ValueError(f"Unknown resource: {uri}")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="calculate",
            description="Perform basic mathematical calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "Mathematical operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    if name == "calculate":
        operation = arguments.get("operation")
        a = arguments.get("a")
        b = arguments.get("b")
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return [TextContent(type="text", text="Error: Division by zero")]
            result = a / b
        else:
            return [TextContent(type="text", text=f"Unknown operation: {operation}")]
        
        return [
            TextContent(
                type="text",
                text=f"Result: {a} {operation} {b} = {result}"
            )
        ]
    
    raise ValueError(f"Unknown tool: {name}")


# Create SSE transport
sse = SseServerTransport("/messages")


async def handle_sse(request):
    """Handle SSE connections"""
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options()
        )


# Create Starlette app
app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
    ]
)


if __name__ == "__main__":
    print("Starting MCP Server on http://localhost:8000")
    print("Connect to SSE endpoint: http://localhost:8000/sse")
    uvicorn.run(app, host="0.0.0.0", port=8000)
