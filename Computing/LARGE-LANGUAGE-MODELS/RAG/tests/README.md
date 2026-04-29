# Tests Directory

This directory contains unit and integration tests for the RAG project.

## Test Files

- `conftest.py` - Pytest configuration and shared fixtures
- `test_example.py` - Simple example tests to verify pytest is working
- `test_rag.py` - Tests for RAG pipeline components
- `test_weather.py` - Tests for weather tool
- `test_agent.py` - Tests for the AI agent

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_example.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_rag.py::TestDocumentLoading -v
```

### Run Specific Test Function

```bash
pytest tests/test_example.py::test_simple_assertion -v
```

### Run Tests with Coverage

```bash
pytest --cov=src tests/
```

### Run Tests with Detailed Output

```bash
pytest tests/ -vv
```

### Run Only Fast Unit Tests

```bash
pytest tests/ -v -m "not integration"
```

## Test Markers

Tests are marked with pytest markers for better organization:

- `@pytest.mark.integration` - Integration tests requiring external services
- `@pytest.mark.slow` - Tests that take more than 1 second
- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.requires_api` - Tests requiring API keys

## Fixtures

Common fixtures are defined in `conftest.py`:

- `data_dir` - Returns the path to test data directory
- `sample_documents` - Loads sample documents for testing
- `mock_openai_api_key` - Sets mock OpenAI API key
- `mock_weather_api_key` - Sets mock weather API key

## Writing New Tests

### Test File Structure

```python
import pytest

class TestMyFeature:
    """Test description."""
    
    def test_something(self):
        """Test that something works."""
        assert True
```

### Using Fixtures

```python
def test_with_fixture(data_dir):
    """Test using a fixture."""
    assert data_dir == "./data"
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

### Testing Exceptions

```python
def test_raises_exception():
    with pytest.raises(ValueError):
        raise ValueError("Test error")
```

### Mocking External Services

```python
from unittest.mock import Mock, patch

@patch('src.module.requests.get')
def test_with_mock(mock_get):
    mock_get.return_value.json.return_value = {"key": "value"}
    # Your test code here
```

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
2. **Test Independence**: Each test should be independent and not rely on other tests
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification phases
4. **Use Fixtures**: Reuse common setup code with fixtures
5. **Mock External Services**: Mock API calls and external dependencies
6. **Test Edge Cases**: Test both normal and error conditions

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest tests/ --cov=src --cov-report=xml
```

## Troubleshooting

### Tests Not Found

Make sure:
- Test files start with `test_`
- Test classes start with `Test`
- Test functions start with `test_`

### Import Errors

Ensure the virtual environment is activated:
```bash
source venv/bin/activate
```

### Missing Dependencies

Install test dependencies:
```bash
pip install -r requirements.txt
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Parametrization](https://docs.pytest.org/en/stable/parametrize.html)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
