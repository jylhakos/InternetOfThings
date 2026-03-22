#!/usr/bin/env python3
"""
AI Agent using OpenAI and MCP
This agent uses OpenAI's GPT models to intelligently choose and use MCP tools
"""

import asyncio
import json
import os
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Uncomment to use OpenAI
# from openai import AsyncOpenAI


class OpenAIAgent:
    """
    AI Agent that uses OpenAI for reasoning and MCP for tool access
    
    Note: Requires OPENAI_API_KEY environment variable
    """
    
    def __init__(self, server_command: str, server_args: List[str], model: str = "gpt-4"):
        self.server_params = StdioServerParameters(
            command=server_command,
            args=server_args,
            env=None
        )
        self.model = model
        self.session = None
        self.available_tools = []
        
        # Initialize OpenAI client
        # self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def connect_to_mcp(self):
        """Connect to MCP server and discover tools"""
        print("🔌 Connecting to MCP server...")
        
        self.read, self.write = await stdio_client(self.server_params).__aenter__()
        self.session = await ClientSession(self.read, self.write).__aenter__()
        await self.session.initialize()
        
        # Discover available tools
        tools_result = await self.session.list_tools()
        self.available_tools = tools_result.tools
        
        print(f"✓ Connected! Discovered {len(self.available_tools)} MCP tools")
    
    def convert_mcp_tools_to_openai_format(self) -> List[Dict]:
        """Convert MCP tool schemas to OpenAI function calling format"""
        openai_tools = []
        
        for tool in self.available_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools
    
    async def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool via MCP"""
        print(f"  🔧 Executing MCP tool: {tool_name}")
        
        result = await self.session.call_tool(tool_name, arguments=arguments)
        
        response_text = ""
        for content in result.content:
            if hasattr(content, 'text'):
                response_text += content.text
        
        return response_text
    
    async def chat(self, user_message: str) -> str:
        """
        Process user message using OpenAI with MCP tool access
        
        This method would:
        1. Send message to OpenAI with available MCP tools
        2. If OpenAI requests a tool call, execute it via MCP
        3. Send tool results back to OpenAI
        4. Return final response
        """
        print(f"\n💬 User: {user_message}")
        
        # Example of how this would work with OpenAI
        # (Commented out to avoid API calls without key)
        
        """
        messages = [{"role": "user", "content": user_message}]
        tools = self.convert_mcp_tools_to_openai_format()
        
        # Initial request to OpenAI
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        # Check if OpenAI wants to call a tool
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                # Execute tool via MCP
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                tool_result = await self.execute_mcp_tool(tool_name, arguments)
                
                # Add tool result to messages
                messages.append({
                    "role": "function",
                    "name": tool_name,
                    "content": tool_result
                })
            
            # Get final response from OpenAI
            final_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            return final_response.choices[0].message.content
        
        return response.choices[0].message.content
        """
        
        # Placeholder response
        return "OpenAI integration requires OPENAI_API_KEY. See comments in code for implementation."
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        print("🔌 Disconnected from MCP")


async def demo():
    """Demonstrate the OpenAI + MCP agent"""
    
    agent = OpenAIAgent(
        server_command="python3",
        server_args=["src/server/mcp_server_stdio.py"],
        model="gpt-4"
    )
    
    try:
        await agent.connect_to_mcp()
        
        print("\n" + "=" * 60)
        print("OPENAI + MCP AGENT DEMO")
        print("=" * 60)
        
        # Show converted tools
        openai_tools = agent.convert_mcp_tools_to_openai_format()
        print("\nTools available to OpenAI:")
        print(json.dumps(openai_tools, indent=2))
        
        # Attempt chat (will show placeholder without API key)
        response = await agent.chat("What's the weather like in Tokyo?")
        print(f"\n🤖 Agent: {response}")
        
    finally:
        await agent.disconnect()


if __name__ == "__main__":
    asyncio.run(demo())
