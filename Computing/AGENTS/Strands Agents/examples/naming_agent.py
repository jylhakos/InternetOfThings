"""
Naming Agent Example with MCP and GitHub Tools

This example demonstrates building an agent that helps name open source projects
by validating domain names and GitHub organization availability.

Note: You will need:
- A GitHub personal access token (set GITHUB_TOKEN environment variable)
- Bedrock model access for Anthropic Claude 3.7 Sonnet in us-west-2
- AWS credentials configured locally
"""

import os
from strands import Agent
from strands.tools.mcp import MCPClient
from strands_tools import http_request
from mcp import stdio_client, StdioServerParameters

# Define a naming-focused system prompt
NAMING_SYSTEM_PROMPT = """
You are an assistant that helps to name open source projects.

When providing open source project name suggestions, always provide
one or more available domain names and one or more available GitHub
organization names that could be used for the project.

Before providing your suggestions, use your tools to validate
that the domain names are not already registered and that the GitHub
organization names are not already used.
"""

def main():
    """Main function to run the naming agent."""
    
    # Check for GitHub token
    if not os.getenv('GITHUB_TOKEN'):
        print("Warning: GITHUB_TOKEN environment variable not set.")
        print("Please set it to use GitHub organization validation.")
        print("Example: export GITHUB_TOKEN=your_token_here\n")
    
    # Load an MCP server that can determine if a domain name is available
    domain_name_tools = MCPClient(lambda: stdio_client(
        StdioServerParameters(command="uvx", args=["fastdomaincheck-mcp-server"])
    ))
    
    # Use a pre-built Strands Agents tool that can make requests to GitHub
    # to determine if a GitHub organization name is available
    github_tools = [http_request]
    
    with domain_name_tools:
        # Define the naming agent with tools and a system prompt
        tools = domain_name_tools.list_tools_sync() + github_tools
        naming_agent = Agent(
            system_prompt=NAMING_SYSTEM_PROMPT,
            tools=tools
        )
        
        # Run the naming agent with the end user's prompt
        print("Naming Agent - Open Source Project Name Generator")
        print("=" * 60)
        
        user_prompt = input("Describe your project (or press Enter for default): ")
        
        if not user_prompt.strip():
            user_prompt = "I need to name an open source project for building AI agents."
        
        print(f"\nGenerating names for: {user_prompt}\n")
        print("Processing (this may take a moment)...\n")
        
        response = naming_agent(user_prompt)
        print(response)

if __name__ == "__main__":
    main()
