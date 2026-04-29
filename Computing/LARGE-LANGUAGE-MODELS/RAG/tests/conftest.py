"""
Test configuration and fixtures for RAG tests.

This module provides pytest fixtures that can be reused across test files.
"""

import os
import pytest
from pathlib import Path


@pytest.fixture
def data_dir():
    """Return the path to the test data directory."""
    return "./data"


@pytest.fixture
def sample_documents(data_dir):
    """Load sample documents for testing."""
    from llama_index.core import SimpleDirectoryReader
    
    if not Path(data_dir).exists():
        pytest.skip(f"Data directory not found: {data_dir}")
    
    documents = SimpleDirectoryReader(data_dir).load_data()
    
    if not documents:
        pytest.skip(f"No documents found in {data_dir}")
    
    return documents


@pytest.fixture
def mock_openai_api_key(monkeypatch):
    """Set a mock OpenAI API key for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-mock-key-12345")


@pytest.fixture
def mock_weather_api_key(monkeypatch):
    """Set a mock weather API key for testing."""
    monkeypatch.setenv("OPENWEATHER_API_KEY", "mock-weather-key-12345")
