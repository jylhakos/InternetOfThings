# LangChain AI Agent

This directory contains a demonstration of building AI agents using LangChain, a framework for developing applications powered by language models.

## Overview

LangChain is an enterprise-grade framework, that provides:
- **Ecosystem**: Extensive integrations with various LLMs, vector stores, and tools
- **Agent Capabilities**: Build autonomous agents that can reason and use tools
- **Chain Composition**: Combine multiple components into sophisticated pipelines
- **Memory Management**: Maintain conversation context and state
- **Observability**: Built-in tracing and monitoring with LangSmith

## What's Included

- **agent.py**: Complete AI agent demo with tools (weather and calculator)
- **server.py**: FastAPI server to deploy the agent as a REST API
- **.env.example**: Template for environment variables
- **requirements.txt**: Python dependencies list

## Prerequisites

- Python 3.9 or later (Python 3.12 recommended)
- OpenAI API key (or other LLM provider)
- VS Code (recommended)

## Setup Instructions

### Step 1: Set Up Virtual Environment

1. **Navigate to this directory**:
   ```bash
   cd "/path/to/AGENTS/LangChain"
   ```

2. **Create a virtual environment**:
   ```bash
   python3.12 -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Linux/Mac**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     venv\Scripts\activate
     ```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- `langchain`: Core LangChain framework
- `langchain-openai`: OpenAI integration for LangChain
- `python-dotenv`: Environment variable management
- `fastapi`: Web framework for API server
- `uvicorn`: ASGI server for FastAPI

### Step 3: Configure API Keys

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key**:
   ```
   OPENAI_API_KEY="sk-your-actual-api-key-here"
   ```

3. **Verify `.env` is in `.gitignore`** (already configured at project root)

### Step 4: Run the Demo

#### Option A: Run the Standalone Agent

```bash
python agent.py
```

This will:
- Run three example queries demonstrating the agent's capabilities
- Enter interactive mode where you can ask your own questions
- Show the agent's reasoning process (verbose mode enabled)

#### Option B: Run the FastAPI Server

```bash
python server.py
```

Then access:
- **API Docs**: http://localhost:8000/docs
- **Query endpoint**: POST to http://localhost:8000/query

Example API request:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather in Tokyo?"}'
```

## Project Structure

```
LangChain/
├── agent.py              # Main agent implementation
├── server.py             # FastAPI server for the agent
├── .env.example          # Environment variables template
├── .env                  # Your actual API keys (gitignored)
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── venv/                # Virtual environment (gitignored)
```

## How It Works

### Agent Architecture

1. **Tools**: The agent has access to functions it can call:
   - `GetWeather`: Retrieves weather information for cities
   - `Calculator`: Performs mathematical calculations

2. **Language Model**: Uses OpenAI's GPT-4 (configurable) for reasoning

3. **Agent Type**: `ZERO_SHOT_REACT_DESCRIPTION`
   
   This is the most common agent type for basic tool use. Let's break down what each part means:
   
   - **ZERO_SHOT**: The agent works without prior examples (zero-shot learning)
     - It doesn't need to be shown examples of how to use tools
     - It figures out tool usage from descriptions alone
     - Makes it flexible and adaptable to new tools
   
   - **REACT**: Stands for "Reasoning and Acting" pattern
     - The agent alternates between thinking (reasoning) and doing (acting)
     - **Thought**: Agent reasons about what to do next
     - **Action**: Agent selects and uses a tool
     - **Observation**: Agent sees the result of the action
     - Repeats this cycle until the task is complete
   
   - **DESCRIPTION**: The agent relies on tool descriptions
     - Each tool has a description explaining when to use it
     - The LLM reads descriptions to decide which tool fits the task
     - Clear, specific descriptions improve agent performance
   
   **Why use this agent type?**
   - ✓ Great for general-purpose tasks
   - ✓ Easy to add new tools (just provide good descriptions)
   - ✓ Transparent reasoning process (especially with `verbose=True`)
   - ✓ No training or examples needed
   - ✓ Works well with GPT-3.5 and GPT-4

4. **Execution Flow**:
   ```
   User Query → Agent Reasoning → Tool Selection → Tool Execution → Response
   ```

### The ReAct Cycle in Action

When you run the agent with `verbose=True`, you'll see the ReAct pattern in action:

```
User: "What's the weather in San Francisco?"

Thought: I need to use the GetWeather tool to find the weather information.
Action: GetWeather
Action Input: "San Francisco"
Observation: It's foggy and cool, 15°C

Thought: I now know the final answer.
Final Answer: The weather in San Francisco is foggy and cool, with a temperature of 15°C.
```

Each cycle includes:
1. **Thought**: The agent's reasoning about what to do
2. **Action**: Which tool to use
3. **Action Input**: What to pass to the tool
4. **Observation**: The result from the tool
5. **Repeat or Finish**: Continue until the agent has enough information

### Other Agent Types in LangChain

While `ZERO_SHOT_REACT_DESCRIPTION` is recommended for most use cases, LangChain offers other agent types:

| Agent Type | Best For | Pros | Cons |
|------------|----------|------|------|
| `ZERO_SHOT_REACT_DESCRIPTION` | General purpose, basic tool use | No examples needed, flexible, transparent | Can be verbose |
| `CONVERSATIONAL_REACT_DESCRIPTION` | Chatbots with memory | Maintains conversation context | Requires memory setup |
| `REACT_DOCSTORE` | Document search and QA | Optimized for document retrieval | Specific to doc search |
| `SELF_ASK_WITH_SEARCH` | Research and fact-finding | Good for complex queries | Requires search tool |
| `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION` | Complex tool inputs | Handles structured data | More complex setup |

For this demo, `ZERO_SHOT_REACT_DESCRIPTION` is ideal because it's:
- Simple to understand and debug
- Doesn't require additional setup
- Works well with multiple tools
- Provides clear reasoning steps

### Key Components

```python
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# 1. Define tools
tools = [Tool(name="...", func=..., description="...")]

# 2. Initialize LLM
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# 3. Create agent executor
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 4. Invoke the agent
response = agent_executor.invoke({"input": "Your question here"})
print(response['output'])
```

## Customization

### Adding New Tools

Add tools to the `tools` list in `agent.py`:

```python
def my_custom_tool(input: str) -> str:
    """Your custom tool logic here"""
    return result

tools.append(
    Tool(
        name="MyTool",
        func=my_custom_tool,
        description="When to use this tool and what it does"
    )
)
```

### Changing the LLM

Modify the `ChatOpenAI` initialization:

```python
# Use GPT-3.5 for faster/cheaper responses
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# Adjust temperature for more creative responses
llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
```

### Using Different LLM Providers

```python
# Anthropic Claude
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-opus-20240229")

# Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-pro")
```

## Deployment with FastAPI

The `server.py` file provides a production-ready REST API:

### Endpoints

- **GET /**: Health check
- **POST /query**: Send questions to the agent
- **GET /docs**: Interactive API documentation

### Run in Production

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t langchain-agent .
docker run -p 8000:8000 --env-file .env langchain-agent
```

## Best Practices

1. **API Key Security**:
   - Never commit `.env` to version control
   - Use environment variables in production
   - Rotate keys regularly

2. **Error Handling**:
   - Set `handle_parsing_errors=True` in agent initialization
   - Implement try-catch blocks for production code

3. **Monitoring**:
   - Enable verbose mode during development
   - Use LangSmith for production observability
   - Log agent interactions for debugging

4. **Performance**:
   - Choose appropriate model (gpt-3.5-turbo vs gpt-4)
   - Set temperature=0 for consistent outputs
   - Cache responses when appropriate

5. **Testing**:
   - Test tools independently before adding to agent
   - Validate tool descriptions are clear
   - Test edge cases and error scenarios

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"
**Solution**: Ensure `.env` file exists and contains your API key.

### Issue: Agent gives unexpected responses
**Solution**: 
- Improve tool descriptions
- Set temperature to 0 for more deterministic outputs
- Enable verbose mode to see reasoning

### Issue: Import errors
**Solution**: Ensure virtual environment is activated and dependencies are installed.

### Issue: API quota exceeded
**Solution**: Check your OpenAI usage limits and billing status.

## Learning Resources

- **LangChain Documentation**: https://python.langchain.com/docs/
- **LangChain Integrations**: https://docs.langchain.com/oss/python/integrations/providers/overview
- **LangChain GitHub**: https://github.com/langchain-ai/langchain
- **LangSmith (Observability)**: https://smith.langchain.com/
- **OpenAI API Reference**: https://platform.openai.com/docs/

## Next Steps

1. **Explore More Agent Types**: Try different agent types like CONVERSATIONAL_REACT_DESCRIPTION
2. **Add Memory**: Implement conversation memory for context retention
3. **Integrate Real APIs**: Replace mock functions with actual API calls
4. **Build Complex Chains**: Combine multiple components into sophisticated workflows
5. **Add Vector Stores**: Integrate document retrieval for RAG applications

## License

See the parent README for more information.

---

*Last Updated: March 2026*
