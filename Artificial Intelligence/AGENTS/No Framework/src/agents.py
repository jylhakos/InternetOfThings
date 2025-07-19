"""
AI Agent implementation without frameworks.

The Python script handles request routing, response formatting, and agent logic.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from tools import ToolManager


class AIAgent:
    """
    Main AI Agent class that processes user requests and generates responses.
    Uses external tools for weather and LLM capabilities.
    """
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434", 
                 ollama_model: str = "llama3.1:8b-instruct-q4_0"):
        """
        Initialize the AI Agent.
        
        Args:
            ollama_base_url: Base URL for Ollama API
            ollama_model: Name of the Ollama model to use
        """
        self.tool_manager = ToolManager(ollama_base_url, ollama_model)
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
    
    async def process_chat_completion(self, messages: List[Dict[str, str]], 
                                    temperature: float = 0.7, 
                                    max_tokens: int = 512) -> Dict[str, Any]:
        """
        Process chat completion request in OpenAI-compatible format.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            OpenAI-compatible response format
        """
        try:
            # Get the latest user message
            user_message = None
            for message in reversed(messages):
                if message.get("role") == "user":
                    user_message = message.get("content", "")
                    break
            
            if not user_message:
                return self._create_error_response("No user message found")
            
            # Process the message using tool manager
            result = await self.tool_manager.process_message(user_message, temperature)
            
            # Store in conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": result["content"], "timestamp": result["timestamp"]}
            ])
            
            # Create OpenAI-compatible response
            response = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": "ai-agent-no-framework",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result["content"]
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(user_message.split()),
                    "completion_tokens": len(result["content"].split()),
                    "total_tokens": len(user_message.split()) + len(result["content"].split())
                },
                "system_fingerprint": f"fp_{self.session_id[:16]}",
                "metadata": {
                    "agent_type": result["type"],
                    "timestamp": result["timestamp"],
                    "session_id": self.session_id
                }
            }
            
            # Add city information for weather responses
            if result["type"] == "weather" and "city" in result:
                response["metadata"]["city"] = result["city"]
            
            return response
            
        except Exception as e:
            return self._create_error_response(f"Error processing request: {str(e)}")
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error response in OpenAI format."""
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": "ai-agent-no-framework",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"I apologize, but I encountered an error: {error_message}"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": len(error_message.split()),
                "total_tokens": len(error_message.split())
            },
            "error": {
                "message": error_message,
                "type": "agent_error",
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on agent and its tools.
        
        Returns:
            Health status information
        """
        try:
            # Test LLM connectivity
            llm_status = "healthy"
            try:
                test_response = await self.tool_manager.llm_tool.generate_response("test", temperature=0.1)
                if test_response is None:
                    llm_status = "unhealthy"
            except Exception:
                llm_status = "unhealthy"
            
            # Test weather API connectivity
            weather_status = "healthy"
            try:
                test_coords = await self.tool_manager.weather_tool.get_coordinates("London")
                if test_coords is None:
                    weather_status = "unhealthy"
            except Exception:
                weather_status = "unhealthy"
            
            return {
                "status": "healthy" if llm_status == "healthy" and weather_status == "healthy" else "degraded",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "llm": llm_status,
                    "weather_api": weather_status
                },
                "session_id": self.session_id,
                "conversation_history_length": len(self.conversation_history),
                "agent_info": {
                    "name": "AI Agent No Framework",
                    "version": "1.0.0",
                    "capabilities": ["chat", "weather", "greetings"]
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "session_id": self.session_id
            }
    
    async def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation history.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of recent conversation messages
        """
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    async def clear_conversation_history(self) -> Dict[str, str]:
        """Clear conversation history."""
        self.conversation_history.clear()
        return {
            "status": "success",
            "message": "Conversation history cleared",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported model names."""
        return [
            "ai-agent-no-framework",
            "llama3.1:8b-instruct-q4_0",
            "llama3.1:8b-instruct-q8_0",
            "llama3.1:7b-instruct-q4_0"
        ]
    
    async def process_streaming_completion(self, messages: List[Dict[str, str]], 
                                         temperature: float = 0.7) -> Any:
        """
        Process streaming chat completion (future implementation).
        Currently returns regular completion.
        """
        # For now, return regular completion
        # In future, could implement streaming via Server-Sent Events
        result = await self.process_chat_completion(messages, temperature)
        return result


class AgentManager:
    """Manager for multiple agent instances (future scalability)."""
    
    def __init__(self):
        self.agents = {}
        self.default_agent = None
    
    def create_agent(self, agent_id: str = None, **kwargs) -> str:
        """Create a new agent instance."""
        if agent_id is None:
            agent_id = str(uuid.uuid4())
        
        self.agents[agent_id] = AIAgent(**kwargs)
        
        if self.default_agent is None:
            self.default_agent = agent_id
        
        return agent_id
    
    def get_agent(self, agent_id: str = None) -> Optional[AIAgent]:
        """Get an agent instance."""
        if agent_id is None:
            agent_id = self.default_agent
        
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agent instances."""
        return [
            {
                "agent_id": agent_id,
                "session_id": agent.session_id,
                "conversation_length": len(agent.conversation_history),
                "is_default": agent_id == self.default_agent
            }
            for agent_id, agent in self.agents.items()
        ]
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent instance."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            if self.default_agent == agent_id:
                self.default_agent = next(iter(self.agents.keys())) if self.agents else None
            return True
        return False


# Utility functions for testing
async def test_agent():
    """Test the AI agent functionality."""
    print("Testing AI Agent...")
    
    agent = AIAgent()
    
    # Test different types of messages
    test_messages = [
        [{"role": "user", "content": "Hello, how are you?"}],
        [{"role": "user", "content": "What's the temperature in London?"}],
        [{"role": "user", "content": "Tell me about Python programming"}],
        [{"role": "user", "content": "Good morning!"}]
    ]
    
    for messages in test_messages:
        print(f"\nTesting message: {messages[0]['content']}")
        result = await agent.process_chat_completion(messages)
        print(f"Response: {result['choices'][0]['message']['content']}")
        print(f"Agent type: {result.get('metadata', {}).get('agent_type', 'unknown')}")
    
    # Test health check
    print("\nTesting health check...")
    health = await agent.health_check()
    print(f"Health status: {health['status']}")
    print(f"Services: {health['services']}")
    
    # Test conversation history
    print("\nConversation history:")
    history = await agent.get_conversation_history()
    for msg in history:
        print(f"  {msg['role']}: {msg['content'][:50]}...")


async def test_agent_manager():
    """Test the agent manager."""
    print("Testing Agent Manager...")
    
    manager = AgentManager()
    
    # Create agents
    agent1_id = manager.create_agent()
    agent2_id = manager.create_agent()
    
    print(f"Created agents: {agent1_id}, {agent2_id}")
    
    # Test agents
    agent1 = manager.get_agent(agent1_id)
    if agent1:
        result = await agent1.process_chat_completion([{"role": "user", "content": "Hello"}])
        print(f"Agent1 response: {result['choices'][0]['message']['content']}")
    
    # List agents
    agents = manager.list_agents()
    print(f"Agents list: {agents}")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_agent())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_agent_manager())
