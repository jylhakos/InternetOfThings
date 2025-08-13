#!/usr/bin/env python3

"""
Python MCP Client Example

This example shows how to interact with the Node.js MCP server from Python.
Useful for integrating with existing Python applications.
"""

import asyncio
import json
import subprocess
from typing import Dict, Any, List


class MCPClient:
    """Simple Python MCP client using subprocess communication"""
    
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process = None
        self.request_id = 0
    
    async def start(self):
        """Start the MCP server process"""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize the connection
        init_message = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "python-mcp-client",
                    "version": "1.0.0"
                }
            }
        }
        
        await self.send_message(init_message)
        response = await self.read_message()
        print(f"Server initialized: {response}")
        
        # Send initialized notification
        initialized_message = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self.send_message(initialized_message)
    
    def get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def send_message(self, message: Dict[str, Any]):
        """Send JSON-RPC message to server"""
        json_str = json.dumps(message) + '\n'
        self.process.stdin.write(json_str.encode())
        await self.process.stdin.drain()
    
    async def read_message(self) -> Dict[str, Any]:
        """Read JSON-RPC message from server"""
        line = await self.process.stdout.readline()
        return json.loads(line.decode().strip())
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        message = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        await self.send_message(message)
        return await self.read_message()
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        message = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/list"
        }
        
        await self.send_message(message)
        return await self.read_message()
    
    async def close(self):
        """Close the connection"""
        if self.process:
            self.process.stdin.close()
            await self.process.wait()


async def main():
    """Main example function"""
    print("🐍 Python MCP Client Example")
    print("============================\n")
    
    # Create client (adjust path to your compiled server)
    client = MCPClient(['node', '../dist/server/index.js'])
    
    try:
        # Start the client
        print("🔌 Starting MCP client...")
        await client.start()
        print("✅ Connected successfully!\n")
        
        # List available tools
        print("📋 Listing available tools...")
        tools_response = await client.list_tools()
        
        if 'result' in tools_response:
            tools = tools_response['result']['tools']
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool['name']}: {tool['description']}")
        print()
        
        # Example 1: Get system information
        print("💻 Getting system information...")
        system_info = await client.call_tool('get_system_info')
        
        if 'result' in system_info:
            content = system_info['result']['content'][0]['text']
            print(f"System Info: {content}")
        print()
        
        # Example 2: Generate text with Llama
        print("🦙 Generating a joke with Llama...")
        joke_response = await client.call_tool('llama_generate', {
            'prompt': 'Tell me a programming joke',
            'temperature': 0.9,
            'max_tokens': 100
        })
        
        if 'result' in joke_response:
            content = joke_response['result']['content'][0]['text']
            print(f"Generated joke: {content}")
        print()
        
        # Example 3: Weather forecast (if available)
        print("🌤️ Getting weather forecast...")
        weather_response = await client.call_tool('weather_forecast', {
            'location': 'San Francisco',
            'days': 3
        })
        
        if 'result' in weather_response:
            content = weather_response['result']['content'][0]['text']
            print(f"Weather: {content}")
        
        print("\n✨ Python example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
