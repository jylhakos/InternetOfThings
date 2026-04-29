"""
LangChain AI Agent Demo
=======================
This demo shows how to create an AI agent using LangChain that can use tools
to accomplish tasks autonomously.

The agent in this example:
- Uses OpenAI's GPT-4 model
- Has access to a custom weather tool
- Can reason about when to use tools
- Provides natural language responses

Setup:
1. Copy .env.example to .env
2. Add your OpenAI API key to .env
3. Activate the virtual environment: source venv/bin/activate
4. Run: python agent.py
"""

import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# LangChain automatically looks for OPENAI_API_KEY in environment variables


# ===== STEP 1: Define Tools =====
# Tools are functions the agent can use to interact with the world
# Each tool has a name, function, and description that helps the agent decide when to use it

def get_weather(city: str) -> str:
    """
    A tool to get the weather for a given city.
    In a real application, this would call a weather API.
    """
    # Mock implementation - replace with actual API call
    weather_data = {
        "San Francisco": "It's foggy and cool, 15°C",
        "New York": "Sunny and warm, 22°C",
        "London": "Rainy and cold, 10°C",
        "Tokyo": "Clear skies, 18°C"
    }
    return weather_data.get(city, f"Weather data not available for {city}. It's always nice somewhere!")


def calculate(expression: str) -> str:
    """
    A tool to perform mathematical calculations.
    Takes a mathematical expression as a string and evaluates it.
    """
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


# Define the tools list with metadata for the agent
tools = [
    Tool(
        name="GetWeather",
        func=get_weather,
        description="Use this tool to get the weather for a specific city. Input should be a city name."
    ),
    Tool(
        name="Calculator",
        func=calculate,
        description="Use this tool to perform mathematical calculations. Input should be a mathematical expression like '2+2' or '10*5'."
    )
]


# ===== STEP 2: Initialize the Language Model =====
# Configure the LLM that will power the agent's reasoning
llm = ChatOpenAI(
    model_name="gpt-4o",  # or "gpt-3.5-turbo" for faster/cheaper responses
    temperature=0  # Temperature 0 makes the output more consistent and deterministic
)


# ===== STEP 3: Create the Agent =====
# Initialize the agent with the LLM and tools
# AgentType.ZERO_SHOT_REACT_DESCRIPTION means the agent will:
#   - Use ReAct (Reasoning + Acting) pattern
#   - Make decisions based on tool descriptions
#   - Work without examples (zero-shot)
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # A common agent type for basic tool use
    verbose=True,  # Set to True to see the agent's reasoning process
    handle_parsing_errors=True  # Gracefully handle any parsing errors
)


# ===== STEP 4: Run the Agent =====
def main():
    """
    Main function to demonstrate the agent's capabilities
    """
    print("=" * 60)
    print("LangChain AI Agent Demo")
    print("=" * 60)
    print("\nThis agent can:")
    print("- Get weather information for cities")
    print("- Perform mathematical calculations")
    print("- Combine tools to answer complex questions\n")
    
    # Example queries that demonstrate different agent capabilities
    queries = [
        "What's the weather like in San Francisco?",
        "Calculate 25 * 4 + 10",
        "What's the weather in Tokyo and what's 15 + 7?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 60}")
        print(f"Query {i}: {query}")
        print('=' * 60)
        
        try:
            # Invoke the agent with the query
            response = agent_executor.invoke({"input": query})
            print(f"\nAgent Response: {response['output']}\n")
        except Exception as e:
            print(f"\nError: {str(e)}\n")
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive Mode - Type 'exit' to quit")
    print("=" * 60)
    
    while True:
        user_input = input("\nYour question: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            # Invoke the agent with user input
            response = agent_executor.invoke({"input": user_input})
            print(f"\nAgent: {response['output']}")
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    # Check if API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key to .env")
        print("3. Run the script again")
    else:
        main()
