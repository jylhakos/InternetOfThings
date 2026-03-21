"""
Simple example tests to demonstrate pytest functionality.

These tests don't require external dependencies and can run immediately.
Run with: pytest tests/test_example.py -v
"""

import pytest


class TestBasicPytest:
    """Basic pytest examples to verify test framework is working."""
    
    def test_simple_assertion(self):
        """Test that basic assertions work."""
        assert 1 + 1 == 2
        assert "hello".upper() == "HELLO"
    
    def test_string_operations(self):
        """Test string operations."""
        text = "LlamaIndex RAG"
        
        assert "LlamaIndex" in text
        assert text.startswith("Llama")
        assert text.endswith("RAG")
        assert len(text) > 0
    
    def test_list_operations(self):
        """Test list operations."""
        tools = ["rag_tool", "weather_tool"]
        
        assert len(tools) == 2
        assert "rag_tool" in tools
        assert tools[0] == "rag_tool"
    
    def test_dict_operations(self):
        """Test dictionary operations."""
        config = {
            "llm_model": "gpt-4o",
            "temperature": 0,
            "verbose": True
        }
        
        assert config["llm_model"] == "gpt-4o"
        assert config.get("temperature") == 0
        assert "verbose" in config


class TestPytestFeatures:
    """Demonstrate pytest features."""
    
    def test_with_fixture(self, data_dir):
        """Test using a fixture from conftest.py."""
        assert data_dir == "./data"
    
    def test_parametrize_decorator(self):
        """Demonstrate parametrized tests."""
        
        @pytest.mark.parametrize("city,expected_type", [
            ("Paris", str),
            ("Tokyo", str),
            ("London", str),
        ])
        def check_city_type(city, expected_type):
            assert isinstance(city, expected_type)
        
        # Call the parametrized test
        check_city_type("Paris", str)
    
    def test_exception_handling(self):
        """Test that exceptions are raised correctly."""
        with pytest.raises(ZeroDivisionError):
            result = 1 / 0
        
        with pytest.raises(KeyError):
            d = {}
            value = d["nonexistent_key"]


class TestMathOperations:
    """Simple math tests to verify pytest is working."""
    
    def test_addition(self):
        """Test addition."""
        assert 2 + 3 == 5
        assert -1 + 1 == 0
    
    def test_multiplication(self):
        """Test multiplication."""
        assert 3 * 4 == 12
        assert 0 * 100 == 0
    
    def test_division(self):
        """Test division."""
        assert 10 / 2 == 5
        assert 9 / 3 == 3


@pytest.mark.parametrize("input_value,expected_output", [
    ("llamaindex", "LLAMAINDEX"),
    ("rag", "RAG"),
    ("agent", "AGENT"),
])
def test_uppercase_conversion(input_value, expected_output):
    """Test uppercase conversion with parameterization."""
    assert input_value.upper() == expected_output


def test_environment_setup():
    """Test that we can access environment-related functionality."""
    import os
    import sys
    
    # Test that Python is working
    assert sys.version_info.major >= 3
    assert sys.version_info.minor >= 9
    
    # Test that we can work with paths
    from pathlib import Path
    current_file = Path(__file__)
    assert current_file.exists()
    assert current_file.name == "test_example.py"


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])
