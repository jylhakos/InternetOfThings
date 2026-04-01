"""
Simple Test Agent - Verify Strands Agents Installation

This script tests that Strands Agents is properly installed and configured
with AWS Bedrock access.
"""

from strands import Agent
import sys

def test_basic_agent():
    """Test basic agent functionality."""
    print("=" * 60)
    print("Strands Agents - Installation Test")
    print("=" * 60)
    print()
    
    try:
        # Create a simple agent
        print("1. Creating agent...")
        agent = Agent(
            system_prompt="You are a helpful AI assistant that responds concisely."
        )
        print("   ✅ Agent created successfully")
        print()
        
        # Test the agent with a simple query
        print("2. Testing agent with a simple query...")
        test_query = "Say 'Hello! Strands Agents is working correctly.' and nothing else."
        print(f"   Query: {test_query}")
        print()
        
        print("3. Getting response from agent...")
        response = agent(test_query)
        print()
        print("   Agent Response:")
        print("   " + "-" * 50)
        print(f"   {response}")
        print("   " + "-" * 50)
        print()
        
        # Success message
        print("=" * 60)
        print("✅ SUCCESS! Strands Agents is configured correctly!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  • Try the weather forecaster: python examples/weather_forecaster.py")
        print("  • Read the README.md for more examples")
        print("  • Check QUICK_START.md for VS Code integration")
        print()
        
        return True
        
    except Exception as e:
        # Error handling
        print()
        print("=" * 60)
        print("❌ ERROR: Test failed")
        print("=" * 60)
        print()
        print(f"Error details: {str(e)}")
        print()
        print("Troubleshooting steps:")
        print("  1. Ensure virtual environment is activated: source venv/bin/activate")
        print("  2. Verify AWS credentials: aws sts get-caller-identity")
        print("  3. Check Bedrock model access in AWS Console")
        print("  4. Verify region supports Bedrock (e.g., us-west-2)")
        print("  5. Check that dependencies are installed: pip install -r requirements.txt")
        print()
        
        return False

if __name__ == "__main__":
    success = test_basic_agent()
    sys.exit(0 if success else 1)
