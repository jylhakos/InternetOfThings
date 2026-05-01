"""
FastAPI Server for LangChain AI Agent
======================================
This module provides a REST API server for the LangChain AI agent,
allowing it to be accessed via HTTP endpoints.

Endpoints:
- GET /: Health check
- POST /query: Send a question to the agent
- GET /docs: Interactive API documentation (Swagger UI)

Usage:
    uvicorn server:app --reload --host 0.0.0.0 --port 8000

Or simply:
    python server.py
"""

import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LangChain AI Agent API",
    description="REST API for interacting with a LangChain-powered AI agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Request/Response Models =====

class QueryRequest(BaseModel):
    """Request model for agent queries"""
    question: str = Field(
        ...,
        description="The question or task for the agent to process",
        min_length=1,
        max_length=1000,
        example="What's the weather like in San Francisco?"
    )
    verbose: Optional[bool] = Field(
        default=False,
        description="Whether to return detailed reasoning steps"
    )


class QueryResponse(BaseModel):
    """Response model for agent queries"""
    question: str = Field(description="The original question")
    answer: str = Field(description="The agent's response")
    success: bool = Field(description="Whether the query was successful")
    error: Optional[str] = Field(default=None, description="Error message if any")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str
    llm_provider: str
    api_key_configured: bool


def create_llm(verbose_mode: bool = False):
    """
    Create the LLM based on the LLM_PROVIDER environment variable.
    Supports "ollama" (default, local) and "openai" (cloud).
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        return ChatOpenAI(model_name=model, temperature=0)
    else:
        from langchain_ollama import ChatOllama
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model, base_url=base_url, temperature=0)


# ===== Agent Tools =====

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city name."""
    weather_data = {
        "San Francisco": "It's foggy and cool, 15°C",
        "New York": "Sunny and warm, 22°C",
        "London": "Rainy and cold, 10°C",
        "Tokyo": "Clear skies, 18°C",
        "Paris": "Partly cloudy, 17°C",
        "Sydney": "Beautiful sunny day, 24°C",
    }
    return weather_data.get(city, f"Weather data not available for {city}. It's probably nice though!")


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression such as '2+2' or '10*5-3'."""
    try:
        result = eval(expression)  # noqa: S307
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


tools = [get_weather, calculator]


# ===== Initialize Agent =====

def create_agent(verbose: bool = False):
    """
    Create and return a LangGraph ReAct agent.

    Args:
        verbose: Unused (kept for API compatibility); LangGraph uses streaming for verbosity.

    Returns:
        Compiled LangGraph agent graph.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        raise ValueError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set")

    llm = create_llm(verbose_mode=verbose)
    return create_react_agent(llm, tools)


# ===== API Endpoints =====

@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    api_key_configured = provider != "openai" or bool(os.getenv("OPENAI_API_KEY"))

    return HealthResponse(
        status="healthy" if api_key_configured else "warning",
        message="LangChain AI Agent API is running" if api_key_configured
                else "API is running but OPENAI_API_KEY is not configured",
        llm_provider=provider,
        api_key_configured=api_key_configured
    )


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Send a question to the AI agent and get a response.
    
    Args:
        request: QueryRequest containing the question and options
        
    Returns:
        QueryResponse with the agent's answer
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        # Check provider-specific requirements
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="LLM_PROVIDER=openai but OPENAI_API_KEY is not configured."
            )
        
        # Create agent executor
        agent_executor = create_agent(verbose=request.verbose)

        # Invoke the agent with the question
        result = agent_executor.invoke({"messages": [("human", request.question)]})
        answer = result["messages"][-1].content
        
        return QueryResponse(
            question=request.question,
            answer=answer,
            success=True
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        return QueryResponse(
            question=request.question,
            answer="",
            success=False,
            error=f"Error processing query: {str(e)}"
        )


@app.get("/tools")
async def list_tools():
    """
    List available tools the agent can use.
    """
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description
            }
            for t in tools
        ]
    }


# ===== Main Execution =====

if __name__ == "__main__":
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("\n" + "=" * 60)
        print("WARNING: LLM_PROVIDER=openai but OPENAI_API_KEY not found!")
        print("=" * 60)
        print("\nThe server will start, but agent queries will fail.")
        print("\nTo fix this:")
        print("1. Copy .env.example to .env")
        print("2. Set OPENAI_API_KEY in .env")
        print("3. Restart the server\n")
    elif provider == "ollama":
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        print(f"\nUsing Ollama at {ollama_url} with model: {ollama_model}")
        print("Ensure Ollama is running (see README for Docker instructions)\n")
    
    # Start the server
    print("\n" + "=" * 60)
    print("Starting LangChain AI Agent API Server")
    print("=" * 60)
    print("\nAccess the API at:")
    print("  - API Documentation: http://localhost:8000/docs")
    print("  - Health Check: http://localhost:8000/")
    print("  - Query Endpoint: http://localhost:8000/query")
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
