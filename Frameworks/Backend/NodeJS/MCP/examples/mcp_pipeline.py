"""
Open WebUI Pipeline for MCP Integration

This pipeline connects Open WebUI to the MCP server, enabling
Llama-3.x models to access tools and resources through MCP.

Installation:
1. Save this file as mcp_pipeline.py
2. Go to Open WebUI Admin Panel > Settings > Pipelines
3. Upload this file
4. Configure the MCP_SERVER_URL in the pipeline settings

Usage:
- The pipeline will automatically forward messages to the MCP server
- Tools and resources will be available through the MCP protocol
- Responses will include context from MCP tools when appropriate
"""

from typing import List, Optional, Dict, Any
import requests
import json
import logging
from pydantic import BaseModel

class Pipeline:
    class Valves(BaseModel):
        # MCP Server Configuration
        MCP_SERVER_URL: str = "http://localhost:3000"
        MCP_ENABLED: bool = True
        
        # Model Configuration
        DEFAULT_MODEL: str = "llama3.2:latest"
        TEMPERATURE: float = 0.7
        MAX_TOKENS: int = 2000
        
        # Tool Configuration
        ENABLE_SYSTEM_INFO: bool = True
        ENABLE_WEATHER: bool = True
        ENABLE_FILE_OPS: bool = False  # Disabled for security
        
        # Logging
        DEBUG_MODE: bool = False

    def __init__(self):
        self.type = "manifold"
        self.name = "MCP Integration Pipeline"
        self.valves = self.Valves()
        self.logger = logging.getLogger(__name__)
        
        if self.valves.DEBUG_MODE:
            logging.basicConfig(level=logging.DEBUG)

    async def on_startup(self):
        """Initialize the pipeline"""
        self.logger.info("🚀 MCP Pipeline starting up...")
        
        # Test MCP server connection
        if await self.test_mcp_connection():
            self.logger.info("✅ MCP server connection successful")
        else:
            self.logger.warning("⚠️ MCP server not accessible")

    async def on_shutdown(self):
        """Cleanup when pipeline shuts down"""
        self.logger.info("👋 MCP Pipeline shutting down...")

    def pipes(self) -> List[Dict[str, Any]]:
        """Return available model pipes"""
        return [
            {
                "id": "mcp-llama3.2",
                "name": "Llama-3.2 with MCP Tools"
            },
            {
                "id": "mcp-llama3.2:1b", 
                "name": "Llama-3.2 1B with MCP Tools"
            },
            {
                "id": "mcp-llama3.2:3b",
                "name": "Llama-3.2 3B with MCP Tools" 
            }
        ]

    async def test_mcp_connection(self) -> bool:
        """Test if MCP server is accessible"""
        try:
            response = requests.get(
                f"{self.valves.MCP_SERVER_URL}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"MCP connection test failed: {e}")
            return False

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from MCP server"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": "tools_list"
            }
            
            response = requests.post(
                f"{self.valves.MCP_SERVER_URL}/mcp",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", {}).get("tools", [])
                
        except Exception as e:
            self.logger.error(f"Failed to get MCP tools: {e}")
            
        return []

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Call a specific MCP tool"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": f"tool_call_{tool_name}"
            }
            
            response = requests.post(
                f"{self.valves.MCP_SERVER_URL}/mcp",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("result", {}).get("content", [])
                
                if content and len(content) > 0:
                    return content[0].get("text", "")
                    
        except Exception as e:
            self.logger.error(f"MCP tool call failed for {tool_name}: {e}")
            
        return None

    def should_use_tools(self, messages: List[Dict[str, Any]]) -> bool:
        """Determine if the conversation should use MCP tools"""
        if not self.valves.MCP_ENABLED:
            return False
            
        # Get the last user message
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        if not user_messages:
            return False
            
        last_message = user_messages[-1].get("content", "").lower()
        
        # Keywords that suggest tool usage
        tool_keywords = [
            "system", "weather", "file", "model", "info",
            "list", "generate", "analyze", "help me",
            "what can you do", "available tools"
        ]
        
        return any(keyword in last_message for keyword in tool_keywords)

    async def pipe(
        self,
        prompt: str,
        model_id: str,
        messages: List[Dict[str, Any]],
        body: Dict[str, Any]
    ) -> str:
        """Main pipeline processing function"""
        
        if self.valves.DEBUG_MODE:
            self.logger.debug(f"Processing request for model: {model_id}")
            self.logger.debug(f"Messages: {json.dumps(messages, indent=2)}")

        # Check if we should use MCP tools
        use_tools = self.should_use_tools(messages)
        
        if not use_tools or not self.valves.MCP_ENABLED:
            # Direct Ollama request without MCP
            return await self.direct_ollama_request(messages, body)

        try:
            # Enhanced processing with MCP tools
            return await self.process_with_mcp(messages, body)
            
        except Exception as e:
            self.logger.error(f"MCP processing failed: {e}")
            # Fallback to direct request
            return await self.direct_ollama_request(messages, body)

    async def direct_ollama_request(
        self, 
        messages: List[Dict[str, Any]], 
        body: Dict[str, Any]
    ) -> str:
        """Make direct request to Ollama without MCP"""
        try:
            # Convert messages to Ollama format
            ollama_payload = {
                "model": self.valves.DEFAULT_MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": body.get("temperature", self.valves.TEMPERATURE),
                    "num_predict": body.get("max_tokens", self.valves.MAX_TOKENS)
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/chat",
                json=ollama_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
                
        except Exception as e:
            self.logger.error(f"Direct Ollama request failed: {e}")
            
        return "I'm having trouble processing your request. Please try again."

    async def process_with_mcp(
        self,
        messages: List[Dict[str, Any]], 
        body: Dict[str, Any]
    ) -> str:
        """Process request with MCP tool integration"""
        
        # Get the last user message
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        if not user_messages:
            return "No user message found."
            
        last_message = user_messages[-1].get("content", "").lower()
        
        # Determine which tools to use based on content
        tool_responses = []
        
        # System information
        if any(word in last_message for word in ["system", "info", "status"]):
            if self.valves.ENABLE_SYSTEM_INFO:
                system_info = await self.call_mcp_tool("get_system_info", {})
                if system_info:
                    tool_responses.append(f"System Information:\n{system_info}")

        # Weather information  
        if any(word in last_message for word in ["weather", "forecast", "temperature"]):
            if self.valves.ENABLE_WEATHER:
                # Extract location from message (simple approach)
                location = "Helsinki, Finland"  # Default location
                weather_info = await self.call_mcp_tool(
                    "weather_forecast", 
                    {"location": location, "days": 1}
                )
                if weather_info:
                    tool_responses.append(f"Weather Information:\n{weather_info}")

        # Available models
        if any(word in last_message for word in ["models", "available", "ollama"]):
            models_info = await self.call_mcp_tool("list_ollama_models", {})
            if models_info:
                tool_responses.append(f"Available Models:\n{models_info}")

        # If we got tool responses, use them to enhance the context
        if tool_responses:
            # Add tool information to context
            enhanced_messages = messages.copy()
            enhanced_messages.append({
                "role": "system",
                "content": f"Additional context from tools:\n\n{chr(10).join(tool_responses)}\n\nPlease incorporate this information in your response."
            })
        else:
            enhanced_messages = messages

        # Now make the chat request with enhanced context
        try:
            chat_response = await self.call_mcp_tool(
                "llama_chat",
                {
                    "messages": enhanced_messages,
                    "temperature": body.get("temperature", self.valves.TEMPERATURE)
                }
            )
            
            if chat_response:
                return chat_response
                
        except Exception as e:
            self.logger.error(f"MCP chat failed: {e}")

        # Fallback to direct request
        return await self.direct_ollama_request(messages, body)
