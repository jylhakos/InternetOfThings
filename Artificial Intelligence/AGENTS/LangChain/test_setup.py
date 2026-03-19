#!/usr/bin/env python3
"""
Test script to verify the LangChain agent setup is correct.
This script checks imports and basic structure without requiring API keys.
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
        from langchain.agents import initialize_agent, AgentType
        print("✓ langchain.agents")
    except ImportError as e:
        print(f"✗ langchain.agents: {e}")
        return False
    
    try:
        from langchain_core.tools import Tool
        print("✓ langchain_core.tools")
    except ImportError as e:
        print(f"✗ langchain_core.tools: {e}")
        return False
    
    try:
        from langchain_openai import ChatOpenAI
        print("✓ langchain_openai")
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
        from langchain_core.tools import Tool
        from langchain.agents import AgentType
        
        # Test tool creation
        def test_tool(input_str: str) -> str:
            return f"Test: {input_str}"
        
        tool = Tool(
            name="TestTool",
            func=test_tool,
            description="A test tool"
        )
        print("✓ Tool creation works")
        
        # Test AgentType enum
        agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION
        print(f"✓ AgentType.ZERO_SHOT_REACT_DESCRIPTION = {agent_type}")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent structure test failed: {e}")
        return False


def check_environment():
    """Check environment configuration."""
    print("\nChecking environment...")
    
    # Check for .env file
    if os.path.exists(".env"):
        print("✓ .env file exists")
    else:
        print("⚠ .env file not found (copy from .env.example)")
    
    # Check for .env.example
    if os.path.exists(".env.example"):
        print("✓ .env.example exists")
    else:
        print("⚠ .env.example not found")
    
    # Check for API key (without showing it)
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-api-key-here":
        print("✓ OPENAI_API_KEY is configured")
    else:
        print("⚠ OPENAI_API_KEY not configured (add to .env file)")
    
    return True


def main():
    print("=" * 60)
    print("LangChain Setup Verification")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test agent structure
    results.append(("Agent Structure", test_agent_structure()))
    
    # Check environment
    results.append(("Environment", check_environment()))
    
    # Summary
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
        print("1. Configure your API key in .env file")
        print("2. Run: python agent.py")
        print("3. Or run: python server.py")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
