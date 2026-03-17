# Python LangChain Implementation (Alternative)

This directory contains an alternative Python implementation using LangChain libraries, as requested for environments that prefer Python-based AI agents.

## LangChain Python vs LangChain.js Implementation

| Feature | LangChain Python | LangChain.js (Primary) |
|---------|------------------|------------------------|
| **Framework** | LangChain Python | LangChain.js |
| **Performance** | Good (sync/async) | Excellent (event-driven) |
| **Memory Usage** | Higher | Lower |
| **Deployment** | pip/conda | npm (simpler) |
| **Container Size** | Larger | Smaller |
| **Startup Time** | Slower | Faster |
| **Production Ready** | ✅ | ✅ (Recommended) |

## When to Use Python LangChain

Choose Python LangChain implementation when:
- Existing Python ML/AI infrastructure
- Team expertise in Python ecosystem  
- Integration with Python-specific libraries (scikit-learn, pandas, etc.)
- Jupyter notebook workflows required
- Custom model fine-tuning pipelines

## Installation

```bash
# Install Python LangChain dependencies
pip install langchain langchain-community langchain-ollama
pip install fastapi uvicorn httpx python-dotenv

# Or using requirements
pip install -r requirements-langchain.txt
```

## Usage

```python
from langchain_agents_python import LangChainPythonAgent

# Initialize agent
agent = LangChainPythonAgent()

# Start server
agent.start_server()
```

## Configuration

The Python LangChain implementation runs on port 8001 to avoid conflicts with the primary JavaScript implementation.

Environment variables:
- `PYTHON_AGENT_PORT=8001`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=llama3.1:8b-instruct-q4_0`

## Note for DevOps Teams

**The JavaScript/LangChain.js implementation remains the PRIMARY recommendation** for production deployments due to:
- Better resource efficiency
- Faster startup times
- Simpler containerization
- More reliable scaling characteristics

Use this Python LangChain implementation only when JavaScript implementation cannot meet specific Python ecosystem requirements.
