"""
LangChain AI Agent Demo
=======================
This demo shows how to create an AI agent using LangChain that can use tools
to accomplish tasks autonomously.

The agent in this example:
- Supports Ollama (local, free) or OpenAI (cloud) as the LLM backend
- Has access to a custom weather tool and calculator
- Can reason about when to use tools
- Provides natural language responses

Uses the LangGraph create_react_agent API (LangChain 1.x).

Setup:
1. Copy .env.example to .env
2. Set LLM_PROVIDER in .env ("ollama" for local, "openai" for cloud)
3. For Ollama: docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
4. For Ollama: docker exec -it ollama ollama pull llama3.2
5. For OpenAI: set OPENAI_API_KEY in .env
6. Activate the virtual environment: source venv/bin/activate
7. Run: python agent.py
"""

import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Load environment variables from .env file
load_dotenv()


# ===== LLM Factory =====

def create_llm():
    """
    Create the LLM based on the LLM_PROVIDER environment variable.

    Set LLM_PROVIDER=ollama (default) for free local inference via Ollama.
    Set LLM_PROVIDER=openai to use the OpenAI cloud API.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        print(f"Using OpenAI provider: {model}")
        return ChatOpenAI(model_name=model, temperature=0)
    else:
        # Ollama (default) - free local inference, no API key needed
        from langchain_ollama import ChatOllama
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"Using Ollama provider: {model} at {base_url}")
        return ChatOllama(model=model, base_url=base_url, temperature=0)


# ===== STEP 1: Define Tools =====
# Tools are functions the agent can use to interact with the world.
# The @tool decorator auto-generates the name and schema from the docstring.

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city name."""
    # Mock implementation - replace with an actual weather API call
    weather_data = {
        "San Francisco": "It's foggy and cool, 15°C",
        "New York": "Sunny and warm, 22°C",
        "London": "Rainy and cold, 10°C",
        "Tokyo": "Clear skies, 18°C",
    }
    return weather_data.get(city, f"Weather data not available for {city}. It's always nice somewhere!")


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression such as '2+2' or '10*5-3'."""
    try:
        result = eval(expression)  # noqa: S307
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


tools = [get_weather, calculator]


# ===== STEP 2: Initialize the Language Model =====
# LLM_PROVIDER env var selects the backend ("ollama" default or "openai").
llm = create_llm()


# ===== STEP 3: Create the Agent =====
# create_react_agent from LangGraph builds a ReAct agent that:
#   - Uses the Reasoning + Acting (ReAct) pattern
#   - Selects tools based on the query
#   - Loops until it produces a final answer
agent_executor = create_react_agent(llm, tools)


# ===== STEP 4: Run the Agent =====

def run_query(question: str) -> str:
    """Invoke the agent with a single question and return the answer."""
    result = agent_executor.invoke({"messages": [("human", question)]})
    return result["messages"][-1].content


def main():
    """Main function to demonstrate the agent's capabilities."""
    print("=" * 60)
    print("LangChain AI Agent Demo")
    print("=" * 60)
    print("\nThis agent can:")
    print("- Get weather information for cities")
    print("- Perform mathematical calculations")
    print("- Combine tools to answer complex questions\n")

    queries = [
        "What's the weather like in San Francisco?",
        "Calculate 25 * 4 + 10",
        "What's the weather in Tokyo and what is 15 + 7?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 60}")
        print(f"Query {i}: {query}")
        print("=" * 60)
        try:
            answer = run_query(query)
            print(f"\nAgent Response: {answer}\n")
        except Exception as e:
            print(f"\nError: {str(e)}\n")

    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive Mode — Type 'exit' to quit")
    print("=" * 60)

    while True:
        user_input = input("\nYour question: ").strip()
        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue
        try:
            print(f"\nAgent: {run_query(user_input)}")
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("ERROR: LLM_PROVIDER=openai but OPENAI_API_KEY not found.")
        print("Please:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key to .env")
        print("3. Run the script again")
    else:
        main()

