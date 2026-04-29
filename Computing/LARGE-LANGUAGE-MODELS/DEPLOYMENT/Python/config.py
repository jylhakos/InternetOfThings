# Ollama FastAPI Server Configuration

# Ollama server settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_API_VERSION = "v1"

# FastAPI server settings
FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = 8000

# Default model settings
DEFAULT_MODEL = "llama3"
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7

# Available models (update based on your Ollama installation)
AVAILABLE_MODELS = [
    "llama3",
    "llama3:8b",
    "llama3:70b",
    "codellama",
    "mistral",
    "neural-chat",
    "starling-lm"
]
