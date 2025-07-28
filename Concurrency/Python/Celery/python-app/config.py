import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Ollama Configuration
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
    
    # LangChain Service Configuration
    LANGCHAIN_SERVICE_URL = os.getenv("LANGCHAIN_SERVICE_URL", "http://localhost:3000")
    
    # FastAPI Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # Celery Configuration
    CELERY_WORKER_CONCURRENCY = int(os.getenv("CELERY_WORKER_CONCURRENCY", 4))
    CELERY_TASK_TIMEOUT = int(os.getenv("CELERY_TASK_TIMEOUT", 300))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

settings = Settings()
