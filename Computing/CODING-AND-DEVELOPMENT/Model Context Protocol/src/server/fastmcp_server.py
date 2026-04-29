#!/usr/bin/env python3
"""
Example MCP Server using FastMCP
FastMCP provides a simpler API for building MCP servers
"""

from fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("demo-server")


@mcp.tool()
def get_system_info(component: str = "os") -> str:
    """
    Get system information
    
    Args:
        component: Which component to query (os, python, platform)
    
    Returns:
        System information as a string
    """
    import sys
    import platform
    
    if component == "os":
        return f"Operating System: {platform.system()} {platform.release()}"
    elif component == "python":
        return f"Python Version: {sys.version}"
    elif component == "platform":
        return f"Platform: {platform.platform()}"
    else:
        return f"Unknown component: {component}"


@mcp.tool()
def text_analysis(text: str, operation: str = "word_count") -> dict:
    """
    Analyze text and return statistics
    
    Args:
        text: Input text to analyze
        operation: Type of analysis (word_count, char_count, line_count)
    
    Returns:
        Dictionary with analysis results
    """
    results = {
        "text_length": len(text),
        "word_count": len(text.split()),
        "line_count": len(text.splitlines()),
        "char_count": len(text),
        "char_count_no_spaces": len(text.replace(" ", ""))
    }
    
    if operation in results:
        return {operation: results[operation]}
    return results


@mcp.resource("config://server")
def get_server_config() -> str:
    """Server configuration resource"""
    return """
    Server Configuration
    ====================
    Name: demo-server
    Version: 1.0.0
    Transport: STDIO/SSE
    Tools: 2
    Resources: 1
    """


if __name__ == "__main__":
    # Run the server
    mcp.run()
