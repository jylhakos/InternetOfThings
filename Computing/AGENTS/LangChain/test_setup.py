#!/usr/bin/env python3
"""
Test script to verify the LangChain agent setup is correct.
This script checks imports and basic structure without requiring API keys.
Supports both Ollama (local) and OpenAI (cloud) providers.
"""

import sys
import os

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")

    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        return False

    try:
        from langchain_core.tools import tool
        print("✓ langchain_core.tools")
    except ImportError as e:
        print(f"✗ langchain_core.tools: {e}")
        return False

    try:
        from langgraph.prebuilt import create_react_agent
        print("✓ langgraph.prebuilt (create_react_agent)")
    except ImportError as e:
        print(f"✗ langgraph.prebuilt: {e}")
        return False

    try:
        from langchain_ollama import ChatOllama
        print("✓ langchain_ollama (local inference)")
    except ImportError as e:
        print(f"✗ langchain_ollama: {e}")
        return False

    try:
        from langchain_openai import ChatOpenAI
        print("✓ langchain_openai (cloud inference)")
    except ImportError as e:
        print(f"✗ langchain_openai: {e}")
        return False

    try:
        from fastapi import FastAPI
        print("✓ fastapi")
    except ImportError as e:
        print(f"✗ fastapi: {e}")
        return False

    try:
        import uvicorn
        print("✓ uvicorn")
    except ImportError as e:
        print(f"✗ uvicorn: {e}")
        return False

    return True


def test_agent_structure():
    """Test that the agent can be structured without API calls."""
    print("\nTesting agent structure...")

    try:
        from langchain_core.tools import tool
        from langgraph.prebuilt import create_react_agent

        @tool
        def test_tool(input_str: str) -> str:
            """A simple test tool."""
            return f"Test: {input_str}"

        print("✓ @tool decorator works")
        print("✓ create_react_agent imported successfully")

        return True

    except Exception as e:
        print(f"✗ Agent structure test failed: {e}")
        return False


def check_ollama_connectivity():
    """Check if Ollama server is reachable."""
    print("\nChecking Ollama connectivity...")

    from dotenv import load_dotenv
    load_dotenv()

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")

    try:
        import requests
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            available_models = [m["name"] for m in data.get("models", [])]
            print(f"✓ Ollama server reachable at {base_url}")
            if available_models:
                print(f"  Available models: {', '.join(available_models)}")
                if any(model in m for m in available_models):
                    print(f"✓ Model '{model}' is available")
                else:
                    print(f"⚠ Model '{model}' not found locally.")
                    print(f"  Pull it with: docker exec -it ollama ollama pull {model}")
            else:
                print(f"⚠ No models downloaded yet.")
                print(f"  Pull one with: docker exec -it ollama ollama pull {model}")
            return True
        else:
            print(f"⚠ Ollama responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠ Ollama not reachable at {base_url}: {e}")
        print("  Start Ollama with: docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama")
        return False


def check_environment():
    """Check environment configuration."""
    print("\nChecking environment...")

    if os.path.exists(".env"):
        print("✓ .env file exists")
    else:
        print("⚠ .env file not found (copy from .env.example)")

    if os.path.exists(".env.example"):
        print("✓ .env.example exists")
    else:
        print("⚠ .env.example not found")

    from dotenv import load_dotenv
    load_dotenv()

    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    print(f"✓ LLM_PROVIDER = {provider}")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key not in ("your-api-key-here", "sk-your-api-key-here"):
            print("✓ OPENAI_API_KEY is configured")
        else:
            print("⚠ OPENAI_API_KEY not configured (add to .env file)")
    else:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        print(f"✓ OLLAMA_BASE_URL = {ollama_url}")
        print(f"✓ OLLAMA_MODEL = {ollama_model}")

    return True


def main():
    print("=" * 60)
    print("LangChain Setup Verification")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Agent Structure", test_agent_structure()))
    results.append(("Environment", check_environment()))

    from dotenv import load_dotenv
    load_dotenv()
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "ollama":
        # Ollama check is informational - don't block overall pass/fail
        check_ollama_connectivity()

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All checks passed! Setup is correct.")
        print("\nNext steps:")
        if provider == "ollama":
            print("1. Start Ollama: docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama")
            print("2. Pull a model: docker exec -it ollama ollama pull llama3.2")
            print("3. Run agent:    python agent.py")
            print("4. Run server:   python server.py")
        else:
            print("1. Configure OPENAI_API_KEY in .env file")
            print("2. Run agent:    python agent.py")
            print("3. Run server:   python server.py")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

