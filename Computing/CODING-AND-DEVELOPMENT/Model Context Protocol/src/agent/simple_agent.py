#!/usr/bin/env python3
"""
Simple AI Agent using MCP for tool access
This agent connects to MCP servers and uses AI models to decide which tools to call
"""

import asyncio
import json
import os
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPAgent:
    """Simple AI agent that uses MCP to access tools"""
    
    def __init__(self, server_command: str, server_args: List[str]):
        self.server_params = StdioServerParameters(
            command=server_command,
            args=server_args,
            env=None
        )
        self.session = None
        self.available_tools = []
    
    async def connect(self):
        """Connect to MCP server"""
        print("🔌 Connecting to MCP server...")
        
        self.read, self.write = await stdio_client(self.server_params).__aenter__()
        self.session = await ClientSession(self.read, self.write).__aenter__()
        await self.session.initialize()
        
        # Discover available tools
        tools_result = await self.session.list_tools()
        self.available_tools = tools_result.tools
        
        print(f"✓ Connected! Found {len(self.available_tools)} tools:")
        for tool in self.available_tools:
            print(f"  • {tool.name}: {tool.description}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool via MCP"""
        print(f"\n🔧 Calling tool: {tool_name}")
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")
        
        result = await self.session.call_tool(tool_name, arguments=arguments)
        
        # Extract text from result
        response_text = ""
        for content in result.content:
            if hasattr(content, 'text'):
                response_text += content.text
        
        return response_text
    
    def get_tool_descriptions(self) -> str:
        """Get formatted tool descriptions for LLM"""
        descriptions = []
        for tool in self.available_tools:
            desc = f"Tool: {tool.name}\n"
            desc += f"Description: {tool.description}\n"
            desc += f"Parameters: {json.dumps(tool.inputSchema, indent=2)}"
            descriptions.append(desc)
        return "\n\n".join(descriptions)
    
    async def execute_task(self, task_description: str):
        """
        Execute a task using available tools
        
        In a real implementation, this would:
        1. Send task + tool descriptions to an LLM
        2. LLM decides which tools to call
        3. Execute the tool calls
        4. Return results to LLM for synthesis
        
        For this demo, we'll use simple rule-based logic
        """
        print(f"\n📋 Task: {task_description}")
        
        # Simple rule-based tool selection (replace with LLM in production)
        if "weather" in task_description.lower():
            # Extract location from task (simplified)
            result = await self.call_tool(
                "get_weather",
                {"location": "San Francisco", "units": "celsius"}
            )
            print(f"\n✅ Result:\n{result}")
            return result
        else:
            print("❌ No suitable tool found for this task")
            return None
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'read'):
            await self.read.__aexit__(None, None, None)
        print("\n🔌 Disconnected from MCP server")


async def main():
    """Main agent execution"""
    
    # Create agent connected to weather server
    agent = MCPAgent(
        server_command="python3",
        server_args=["src/server/mcp_server_stdio.py"]
    )
    
    try:
        # Connect to MCP server
        await agent.connect()
        
        # Show available tools
        print("\n" + "=" * 60)
        print("AVAILABLE TOOLS")
        print("=" * 60)
        print(agent.get_tool_descriptions())
        
        # Execute sample tasks
        print("\n" + "=" * 60)
        print("EXECUTING TASKS")
        print("=" * 60)
        
        await agent.execute_task("What's the weather in San Francisco?")
        
    finally:
        await agent.disconnect()


if __name__ == "__main__":
    print("=" * 60)
    print("MCP-POWERED AI AGENT")
    print("=" * 60)
    
    asyncio.run(main())
