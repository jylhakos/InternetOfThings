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
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
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
    api_key_configured: bool


# ===== Agent Tools =====

def get_weather(city: str) -> str:
    """Get weather information for a city"""
    weather_data = {
        "San Francisco": "It's foggy and cool, 15°C",
        "New York": "Sunny and warm, 22°C",
        "London": "Rainy and cold, 10°C",
        "Tokyo": "Clear skies, 18°C",
        "Paris": "Partly cloudy, 17°C",
        "Sydney": "Beautiful sunny day, 24°C"
    }
    return weather_data.get(city, f"Weather data not available for {city}. It's probably nice though!")


def calculate(expression: str) -> str:
    """Perform mathematical calculations"""
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


# Define tools
tools = [
    Tool(
        name="GetWeather",
        func=get_weather,
        description="Use this tool to get the weather for a specific city. Input should be a city name."
    ),
    Tool(
        name="Calculator",
        func=calculate,
        description="Use this tool to perform mathematical calculations. Input should be a mathematical expression."
    )
]


# ===== Initialize Agent =====

def create_agent(verbose: bool = False):
    """
    Create and return a LangChain agent instance.
    
    Args:
        verbose: Whether to enable verbose output
        
    Returns:
        Initialized LangChain agent
    """
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0
    )
    
    # Create agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=5  # Prevent infinite loops
    )
    
    return agent


# ===== API Endpoints =====

@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    return HealthResponse(
        status="healthy" if api_key_configured else "warning",
        message="LangChain AI Agent API is running" if api_key_configured 
                else "API is running but OPENAI_API_KEY is not configured",
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
        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured. Please set it in your .env file."
            )
        
        # Create agent executor
        agent_executor = create_agent(verbose=request.verbose)
        
        # Invoke the agent with the question
        response = agent_executor.invoke({"input": request.question})
        answer = response['output']
        
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
    
    Returns:
        List of tool names and descriptions
    """
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in tools
        ]
    }


# ===== Main Execution =====

if __name__ == "__main__":
    # Check for API key before starting server
    if not os.getenv("OPENAI_API_KEY"):
        print("\n" + "=" * 60)
        print("WARNING: OPENAI_API_KEY not found!")
        print("=" * 60)
        print("\nThe server will start, but agent queries will fail.")
        print("\nTo fix this:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key to .env")
        print("3. Restart the server\n")
    
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
