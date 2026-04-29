"""
FastAPI server implementation for the AI Agent.

The Python script provides OpenAI-compatible RESTful API endpoints.
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import AIAgent, AgentManager

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.1:8b-instruct-q4_0")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Global agent manager
agent_manager = AgentManager()


# Pydantic models for request/response validation
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")


class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="List of messages in the conversation")
    model: Optional[str] = Field("ai-agent-no-framework", description="Model to use for completion")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(512, ge=1, le=2048, description="Maximum tokens in response")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]
    session_id: str
    agent_info: Dict[str, Any]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting AI Agent Server...")
    
    # Create default agent
    agent_id = agent_manager.create_agent(
        ollama_base_url=OLLAMA_BASE_URL,
        ollama_model=MODEL_NAME
    )
    print(f"✅ Created default agent: {agent_id}")
    
    # Test connectivity
    agent = agent_manager.get_agent()
    if agent:
        health = await agent.health_check()
        print(f"🔍 Health check: {health['status']}")
        print(f"🔧 LLM Status: {health['services']['llm']}")
        print(f"🌤️  Weather API Status: {health['services']['weather_api']}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Agent Server...")


# Create FastAPI app
app = FastAPI(
    title="AI Agent - No Framework",
    description="AI Agent implementation without frameworks, providing OpenAI-compatible API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Agent - No Framework API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat_completions": "/v1/chat/completions",
            "models": "/v1/models"
        },
        "documentation": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    agent = agent_manager.get_agent()
    if not agent:
        raise HTTPException(status_code=503, detail="No agent available")
    
    health = await agent.health_check()
    return health


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.
    Processes user messages and returns AI responses.
    """
    try:
        agent = agent_manager.get_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="No agent available")
        
        # Convert Pydantic models to dict
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Process the completion
        if request.stream:
            # Future: implement streaming
            response = await agent.process_streaming_completion(
                messages=messages,
                temperature=request.temperature
            )
        else:
            response = await agent.process_chat_completion(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    agent = agent_manager.get_agent()
    if not agent:
        models = ["ai-agent-no-framework"]
    else:
        models = agent.get_supported_models()
    
    return {
        "object": "list",
        "data": [
            {
                "id": model,
                "object": "model",
                "created": 1677610602,
                "owned_by": "ai-agent-no-framework",
                "permission": [],
                "root": model,
                "parent": None
            }
            for model in models
        ]
    }


@app.get("/v1/agents")
async def list_agents():
    """List all agent instances."""
    return {
        "agents": agent_manager.list_agents(),
        "total": len(agent_manager.agents)
    }


@app.post("/v1/agents")
async def create_agent(ollama_base_url: Optional[str] = None, ollama_model: Optional[str] = None):
    """Create a new agent instance."""
    kwargs = {}
    if ollama_base_url:
        kwargs["ollama_base_url"] = ollama_base_url
    if ollama_model:
        kwargs["ollama_model"] = ollama_model
    
    agent_id = agent_manager.create_agent(**kwargs)
    return {
        "agent_id": agent_id,
        "status": "created",
        "message": "New agent instance created successfully"
    }


@app.delete("/v1/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent instance."""
    if agent_manager.remove_agent(agent_id):
        return {
            "agent_id": agent_id,
            "status": "deleted",
            "message": "Agent instance deleted successfully"
        }
    else:
        raise HTTPException(status_code=404, detail="Agent not found")


@app.get("/v1/agents/{agent_id}/history")
async def get_agent_history(agent_id: str, limit: int = 10):
    """Get conversation history for a specific agent."""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    history = await agent.get_conversation_history(limit)
    return {
        "agent_id": agent_id,
        "history": history,
        "count": len(history)
    }


@app.delete("/v1/agents/{agent_id}/history")
async def clear_agent_history(agent_id: str):
    """Clear conversation history for a specific agent."""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    result = await agent.clear_conversation_history()
    return {
        "agent_id": agent_id,
        **result
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": f"Internal server error: {str(exc)}",
                "type": "internal_error",
                "timestamp": str(asyncio.get_event_loop().time())
            }
        }
    )


# Custom endpoint for weather queries (convenience)
@app.post("/v1/weather")
async def get_weather(city: str):
    """Convenience endpoint for weather queries."""
    agent = agent_manager.get_agent()
    if not agent:
        raise HTTPException(status_code=503, detail="No agent available")
    
    messages = [{"role": "user", "content": f"What's the temperature in {city}?"}]
    response = await agent.process_chat_completion(messages)
    
    return {
        "city": city,
        "response": response["choices"][0]["message"]["content"],
        "metadata": response.get("metadata", {})
    }


# Development and testing endpoints
@app.get("/dev/test")
async def dev_test():
    """Development testing endpoint."""
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(status_code=404, detail="Endpoint not available")
    
    agent = agent_manager.get_agent()
    if not agent:
        return {"error": "No agent available"}
    
    test_results = {}
    
    # Test greeting
    greeting_response = await agent.process_chat_completion([
        {"role": "user", "content": "Hello!"}
    ])
    test_results["greeting"] = greeting_response["choices"][0]["message"]["content"]
    
    # Test weather (if working)
    try:
        weather_response = await agent.process_chat_completion([
            {"role": "user", "content": "What's the temperature in London?"}
        ])
        test_results["weather"] = weather_response["choices"][0]["message"]["content"]
    except Exception as e:
        test_results["weather_error"] = str(e)
    
    # Test general query
    general_response = await agent.process_chat_completion([
        {"role": "user", "content": "What is Python?"}
    ])
    test_results["general"] = general_response["choices"][0]["message"]["content"]
    
    return test_results


def main():
    """Main function to run the server."""
    print(f"🌟 AI Agent - No Framework Server")
    print(f"📍 Server: {SERVER_HOST}:{SERVER_PORT}")
    print(f"🤖 Ollama: {OLLAMA_BASE_URL}")
    print(f"🧠 Model: {MODEL_NAME}")
    print(f"📚 Docs: http://{SERVER_HOST}:{SERVER_PORT}/docs")
    print("-" * 50)
    
    uvicorn.run(
        "index:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
