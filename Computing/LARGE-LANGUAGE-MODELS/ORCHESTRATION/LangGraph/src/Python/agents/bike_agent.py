from typing import Dict, Any, List, Annotated, Optional
import json
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.tools import BaseTool
from typing_extensions import TypedDict

# Import tools
from agents.tools.bike_tools import (
    find_stations_tool, 
    check_availability_tool, 
    calculate_cost_tool
)
from agents.tools.location_tools import (
    geocode_tool,
    distance_tool, 
    nearby_locations_tool
)
from agents.tools.python_repl import python_repl_tool

from services.ollama_service import OllamaService
from utils.config import Config
from utils.logger import logger

# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    user_request: str
    city: Optional[str]
    location: Optional[str]
    bike_type: Optional[str]
    context: Dict[str, Any]

class BikeRentalAgent:
    def __init__(self):
        self.ollama_service = OllamaService()
        
        # Initialize Ollama Chat model
        self.llm = ChatOllama(
            base_url=Config.OLLAMA_BASE_URL,
            model=Config.OLLAMA_MODEL,
            temperature=0.1,
            top_k=10,
            top_p=0.3,
        )
        
        # Available tools
        self.tools = [
            find_stations_tool,
            check_availability_tool,
            calculate_cost_tool,
            geocode_tool,
            distance_tool,
            nearby_locations_tool,
            python_repl_tool
        ]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Create the agent graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        graph.set_entry_point("agent")
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        graph.add_edge("tools", "agent")
        
        return graph.compile()
    
    def _agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Main agent reasoning node"""
        messages = state.get("messages", [])
        
        # Add system prompt if this is the first message
        if not messages or not isinstance(messages[0], type(AIMessage)):
            system_prompt = self._get_system_prompt()
            messages = [HumanMessage(content=system_prompt)] + messages
        
        # Invoke the LLM with tools
        try:
            response = self.llm_with_tools.invoke(messages)
            messages.append(response)
            
            return {"messages": messages}
            
        except Exception as e:
            logger.error(f"Error in agent node: {e}")
            error_message = AIMessage(
                content=f"I apologize, but I encountered an error: {str(e)}. Please try again."
            )
            messages.append(error_message)
            return {"messages": messages}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine whether to continue to tools or end"""
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        
        if last_message and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        return "end"
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the bike rental agent"""
        return """You are an expert AI assistant for bike rental services in European cities. 
You help users find, rent, and get information about bicycles in cities like Amsterdam, Paris, Berlin, and other European destinations.

Your capabilities include:
- Finding available bike stations and rental locations
- Checking real-time bike availability  
- Calculating rental costs and pricing
- Providing location information and directions
- Geocoding addresses and landmarks
- Finding nearby points of interest
- Performing calculations with Python code

Supported cities: Amsterdam, Paris, Berlin, London, Barcelona, Madrid, Copenhagen, Vienna

When a user asks about bike rental:
1. First understand their location and requirements
2. Find nearby bike stations with availability
3. Provide pricing information
4. Offer additional helpful information about the area

Be helpful, concise, and always prioritize user safety. If you need to perform calculations or data processing, use the Python REPL tool.

Always respond in a friendly, informative manner and provide actionable advice."""

    async def process_request(self, user_message: str, session_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a user request through the agent"""
        try:
            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=user_message)],
                "user_request": user_message,
                "city": None,
                "location": None,
                "bike_type": None,
                "context": session_context or {}
            }
            
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Extract response
            messages = final_state.get("messages", [])
            last_message = messages[-1] if messages else None
            
            if last_message and hasattr(last_message, 'content'):
                response_text = last_message.content
            else:
                response_text = "I apologize, but I couldn't process your request properly."
            
            return {
                "success": True,
                "response": response_text,
                "messages": [msg.dict() if hasattr(msg, 'dict') else str(msg) for msg in messages],
                "context": final_state.get("context", {})
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "success": False,
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "error": str(e)
            }
    
    def process_request_sync(self, user_message: str, session_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Synchronous version of process_request for FastAPI compatibility"""
        import asyncio
        try:
            return asyncio.run(self.process_request(user_message, session_context))
        except Exception as e:
            logger.error(f"Error in sync processing: {e}")
            return {
                "success": False,
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "error": str(e)
            }

# Create global agent instance
bike_agent = BikeRentalAgent()
