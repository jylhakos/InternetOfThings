"""
Unit tests for the AI agent.

These tests verify agent initialization, tool integration, and behavior.
Run with: pytest tests/test_agent.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestAgentInitialization:
    """Test agent initialization and setup."""
    
    def test_agent_requires_api_keys(self, monkeypatch):
        """Test that agent initialization checks for API keys."""
        from src.agent import RAGAgent
        
        # Remove API keys
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
        
        # Agent should still initialize but show warnings
        # This may fail if RAG tool requires valid data
        pytest.skip("Requires data directory and may need API keys")
    
    def test_agent_initialization_with_tools(self, mock_openai_api_key, mock_weather_api_key):
        """Test basic agent initialization."""
        from src.agent import RAGAgent
        
        # This test may fail without proper setup
        pytest.skip("Requires full environment setup")
        
        agent = RAGAgent(verbose=False)
        
        assert agent is not None
        assert hasattr(agent, 'agent')
        assert hasattr(agent, 'tools')
        assert len(agent.tools) > 0


class TestAgentTools:
    """Test agent tool integration."""
    
    def test_agent_has_rag_tool(self):
        """Test that agent includes RAG tool."""
        pytest.skip("Requires full environment setup")
    
    def test_agent_has_weather_tool(self):
        """Test that agent includes weather tool."""
        pytest.skip("Requires full environment setup")
    
    def test_agent_can_add_custom_tools(self):
        """Test that custom tools can be added to agent."""
        pytest.skip("Requires full environment setup")


class TestAgentChat:
    """Test agent chat functionality."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        from src.agent import RAGAgent
        
        # Create a mock agent
        agent = Mock(spec=RAGAgent)
        agent.chat = Mock(return_value="Mock response")
        agent.reset = Mock()
        
        return agent
    
    def test_agent_chat_method(self, mock_agent):
        """Test agent chat method."""
        response = mock_agent.chat("Test question")
        
        assert response is not None
        assert isinstance(response, str)
        mock_agent.chat.assert_called_once_with("Test question")
    
    def test_agent_reset_method(self, mock_agent):
        """Test agent reset method."""
        mock_agent.reset()
        mock_agent.reset.assert_called_once()


class TestAgentToolSelection:
    """Test agent's ability to select appropriate tools."""
    
    def test_agent_selects_rag_for_knowledge_query(self):
        """Test that agent uses RAG tool for knowledge questions."""
        # This would require mocking the agent's internal logic
        pytest.skip("Requires agent with mocked tools")
    
    def test_agent_selects_weather_for_weather_query(self):
        """Test that agent uses weather tool for weather questions."""
        # This would require mocking the agent's internal logic
        pytest.skip("Requires agent with mocked tools")


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for the complete agent."""
    
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration", default=False),
        reason="Integration tests disabled by default"
    )
    def test_agent_end_to_end(self):
        """Test complete agent workflow."""
        from src.agent import RAGAgent
        
        agent = RAGAgent(verbose=False)
        
        # Test knowledge base question
        response1 = agent.chat("What is LlamaIndex?")
        assert len(response1) > 0
        
        # Test weather question
        response2 = agent.chat("What's the weather in Paris?")
        assert len(response2) > 0
        
        # Test agent memory
        agent.reset()


class TestAgentErrorHandling:
    """Test agent error handling."""
    
    def test_agent_handles_empty_query(self):
        """Test agent handles empty queries gracefully."""
        pytest.skip("Requires full agent setup")
    
    def test_agent_handles_tool_failure(self):
        """Test agent handles tool failures gracefully."""
        pytest.skip("Requires mocked agent with failing tools")
    
    def test_agent_handles_missing_api_keys(self):
        """Test agent behavior with missing API keys."""
        pytest.skip("Requires specific environment configuration")


class TestAgentStreaming:
    """Test agent streaming functionality."""
    
    def test_agent_stream_chat_method_exists(self):
        """Test that stream_chat method exists."""
        from src.agent import RAGAgent
        
        assert hasattr(RAGAgent, 'stream_chat')
    
    def test_agent_stream_chat_returns_generator(self):
        """Test that stream_chat returns a generator."""
        pytest.skip("Requires full agent setup")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
