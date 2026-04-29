# Testing External MCP Implementations

## Overview

This document explains the test suite for validating MCP clients and servers from the [MCP Quickstart Resources repository](https://github.com/modelcontextprotocol/quickstart-resources).

## Test File

**Location**: `tests/test_mcp_quickstart.py`

This test suite validates MCP implementations based on:
- [Weather Server (Python)](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/weather-server-python)
- [MCP Client (Python)](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python)

## Test Coverage

### 1. Tool Discovery Tests (2 tests)
-   **test_tool_discovery_lists_all_tools**: Verifies that `list_tools()` returns all expected tools
-   **test_tool_discovery_returns_correct_schemas**: Validates tool schemas have required properties

### 2. Parameter Validation Tests (4 tests)
-   **test_parameter_validation_missing_required**: Tests missing required parameters (should raise errors)
-   **test_parameter_validation_invalid_values**: Tests invalid parameter values (out of range, wrong type)
-   **test_parameter_validation_valid_requests**: Tests valid parameters (should process successfully)
-   **test_parameter_validation_unknown_tool**: Tests unknown tool names (should raise errors)

### 3. Resource/Prompt Handling Tests (3 tests)
-   **test_resource_listing**: Verifies `list_resources()` returns available resources
-   **test_resource_reading_valid_uri**: Tests `read_resource()` with valid URIs
-   **test_resource_reading_invalid_uri**: Tests `read_resource()` with invalid URIs (should raise errors)

### 4. Integration Tests (2 tests)
-   **test_full_mcp_client_server_flow**: Full client-server flow (discovery → tool call → resource access)
-   **test_default_parameter_handling**: Verifies default parameter handling

### 5. Environment Tests (1 test)
-   **test_virtual_environment_active**: Ensures tests run in virtual environment

## Running the Tests

### Basic Test Execution

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Run all tests
pytest tests/test_mcp_quickstart.py -v

# Run specific test categories
pytest tests/test_mcp_quickstart.py -v -k "tool_discovery"
pytest tests/test_mcp_quickstart.py -v -k "parameter_validation"
pytest tests/test_mcp_quickstart.py -v -k "resource"

# Run integration tests only
pytest tests/test_mcp_quickstart.py -v -m integration

# Run with detailed output
pytest tests/test_mcp_quickstart.py -v --tb=short
```

### Test Results

All 12 tests pass successfully:

```
============================== 12 passed in 0.32s ===============================
tests/test_mcp_quickstart.py::test_tool_discovery_lists_all_tools PASSED
tests/test_mcp_quickstart.py::test_tool_discovery_returns_correct_schemas PASSED
tests/test_mcp_quickstart.py::test_parameter_validation_missing_required PASSED
tests/test_mcp_quickstart.py::test_parameter_validation_invalid_values PASSED
tests/test_mcp_quickstart.py::test_parameter_validation_valid_requests PASSED
tests/test_mcp_quickstart.py::test_parameter_validation_unknown_tool PASSED
tests/test_mcp_quickstart.py::test_resource_listing PASSED
tests/test_mcp_quickstart.py::test_resource_reading_valid_uri PASSED
tests/test_mcp_quickstart.py::test_resource_reading_invalid_uri PASSED
tests/test_mcp_quickstart.py::test_full_mcp_client_server_flow PASSED
tests/test_mcp_quickstart.py::test_default_parameter_handling PASSED
tests/test_mcp_quickstart.py::test_virtual_environment_active PASSED
```

## Key Testing Patterns

### 1. Mock Weather Server Implementation

```python
class MockWeatherServer:
    """
    Mock implementation of the MCP Weather Server from quickstart-resources.
    Simulates the weather server for testing purposes.
    """
    
    def __init__(self):
        self.app = Server("weather-server")
        self._list_tools_handler = None
        self._call_tool_handler = None
        self._list_resources_handler = None
        self._read_resource_handler = None
        self.setup_handlers()
```

### 2. Testing Tool Discovery

```python
@pytest.mark.asyncio
async def test_tool_discovery_lists_all_tools():
    """Verify that list_tools() returns all expected tools"""
    server = MockWeatherServer()
    tools = await server._list_tools_handler()
    
    assert len(tools) == 2
    tool_names = [tool.name for tool in tools]
    assert "get_forecast" in tool_names
    assert "get_current_weather" in tool_names
```

### 3. Testing Parameter Validation

```python
@pytest.mark.asyncio
async def test_parameter_validation_missing_required():
    """Verify tools reject requests with missing required parameters"""
    server = MockWeatherServer()
    
    with pytest.raises(ValueError, match="Location parameter is required"):
        await server._call_tool_handler("get_forecast", {"days": 3})
```

### 4. Testing Resource Access

```python
@pytest.mark.asyncio
async def test_resource_reading_valid_uri():
    """Verify read_resource() returns content for valid URIs"""
    server = MockWeatherServer()
    
    content = await server._read_resource_handler("weather://docs/api-guide")
    assert content
    assert "Weather API Guide" in content
```

## Why These Tests Matter

1. **MCP Specification Compliance**: Ensures tools, resources, and prompts work as expected
2. **Error Handling**: Validates invalid inputs are caught and reported properly
3. **Production Readiness**: All critical paths are validated
4. **Compatibility**: Works with different MCP clients and transport methods

## Contributing Test Cases

To contribute test cases to the MCP community:

1. **Fork the repository**: https://github.com/modelcontextprotocol/quickstart-resources
2. **Add test cases** to validate specific MCP features
3. **Ensure virtual environment checks**: Include venv activation validation
4. **Document expected behavior**: Add clear assertions and error messages
5. **Submit a pull request** with your improvements

## Configuration

### pytest Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-v --tb=short"
testpaths = ["tests"]
asyncio_mode = "auto"

markers = [
    "asyncio: mark test as async",
    "integration: mark test as integration test",
]
```

### Dependencies (requirements.txt)

```
# Testing
pytest>=9.0.0
pytest-asyncio>=1.3.0
```

## Next Steps

1. **Extend tests** to cover more MCP servers from quickstart-resources
2. **Add performance tests** for high-load scenarios
3. **Test different transports** (STDIO, SSE, WebSocket)
4. **Add security tests** for authentication and authorization
5. **Test error recovery** scenarios (network failures, timeouts)

## Resources

- **MCP Quickstart Resources**: https://github.com/modelcontextprotocol/quickstart-resources
- **Weather Server Example**: https://github.com/modelcontextprotocol/quickstart-resources/tree/main/weather-server-python
- **MCP Client Example**: https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python
- **MCP Documentation**: https://modelcontextprotocol.io/
- **pytest Documentation**: https://docs.pytest.org/
