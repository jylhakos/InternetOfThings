#!/usr/bin/env python3
"""
Simple runner script for the Llama 4 Scout AI Agent.
This script starts the AI Agent without Docker for development and testing.
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def check_requirements():
    """Check if basic requirements are met."""
    try:
        import httpx
        import fastapi
        import pydantic
        print("✅ Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

async def check_ollama():
    """Check if Ollama is running and has a compatible model."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                print(f"✅ Ollama is running with {len(models)} models")
                
                # Check for Llama 4 models first
                llama4_models = [m for m in models if 'llama4' in m.lower()]
                if llama4_models:
                    print(f"🌟 Found Llama 4 models: {llama4_models}")
                    return llama4_models[0]
                
                # Fall back to Llama 3.x
                llama3_models = [m for m in models if 'llama3' in m.lower()]
                if llama3_models:
                    print(f"📝 Found Llama 3.x models: {llama3_models}")
                    return llama3_models[0]
                
                print("⚠️  No compatible models found")
                return None
            else:
                print("❌ Ollama API not responding")
                return None
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Please make sure Ollama is installed and running:")
        print("  curl -fsSL https://ollama.com/install.sh | sh")
        print("  ollama serve")
        return None

def main():
    """Main entry point."""
    print("🚀 Starting Llama 4 Scout AI Agent...")
    print("-" * 50)
    
    # Check Python requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check Ollama
    model = asyncio.run(check_ollama())
    if not model:
        print("\n💡 To install a model:")
        print("  ollama pull llama4:scout          # Preferred")
        print("  ollama pull llama3.1:8b-instruct-q4_0  # Fallback")
        sys.exit(1)
    
    # Set environment variables
    os.environ['MODEL_NAME'] = model
    os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
    os.environ['SERVER_HOST'] = '0.0.0.0'
    os.environ['SERVER_PORT'] = '8000'
    
    print(f"🤖 Using model: {model}")
    print(f"🌐 Starting server on http://localhost:8000")
    print("-" * 50)
    
    try:
        # Import and run the FastAPI app
        from index import app
        
        # Configure uvicorn
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False  # Set to True for development
        )
        
        server = uvicorn.Server(config)
        
        print("🎉 AI Agent is starting!")
        print("\nEndpoints:")
        print("  Health Check: http://localhost:8000/health")
        print("  Chat API: http://localhost:8000/v1/chat/completions")
        print("  Documentation: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop")
        print("-" * 50)
        
        # Run the server
        asyncio.run(server.serve())
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AI Agent...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
