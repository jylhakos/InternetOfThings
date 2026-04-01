"""
Unit tests for n8n and Ollama workflow components.
Run with: pytest tests/test_workflow.py -v
"""

import pytest
import requests
import json
from typing import Dict, Any


class TestOllamaConnection:
    """Test suite for Ollama server connectivity"""

    @pytest.fixture
    def ollama_base_url(self) -> str:
        """Ollama server base URL"""
        return 'http://localhost:11434'

    def test_ollama_server_running(self, ollama_base_url: str):
        """Test if Ollama server is accessible"""
        try:
            response = requests.get(f'{ollama_base_url}/api/version', timeout=5)
            assert response.status_code == 200, "Ollama server is not responding"
            data = response.json()
            assert 'version' in data, "Invalid response from Ollama server"
            print(f"✓ Ollama version: {data['version']}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama server is not running. Start with: ollama serve")

    def test_ollama_models_available(self, ollama_base_url: str):
        """Test if required models are installed"""
        try:
            response = requests.get(f'{ollama_base_url}/api/tags', timeout=5)
            assert response.status_code == 200
            data = response.json()
            
            models = [model['name'] for model in data.get('models', [])]
            assert len(models) > 0, "No models installed. Run: ollama pull llama2"
            
            # Check for llama2 model family
            has_llama2 = any('llama2' in model.lower() for model in models)
            if not has_llama2:
                pytest.skip("llama2 model not found. Install with: ollama pull llama2")
            
            print(f"✓ Available models: {', '.join(models)}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama server is not running")

    def test_ollama_generate_request(self, ollama_base_url: str):
        """Test basic text generation with Ollama"""
        try:
            payload = {
                "model": "llama2",
                "prompt": "Hello",
                "stream": False
            }
            
            response = requests.post(
                f'{ollama_base_url}/api/generate',
                json=payload,
                timeout=30
            )
            
            assert response.status_code == 200, "Failed to generate response"
            data = response.json()
            assert 'response' in data, "No response field in Ollama output"
            assert len(data['response']) > 0, "Empty response from Ollama"
            print(f"✓ Ollama generated response successfully")
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama server is not running")
        except requests.exceptions.Timeout:
            pytest.skip("Ollama response timeout - model may not be loaded")


class TestN8nServer:
    """Test suite for n8n server"""

    @pytest.fixture
    def n8n_base_url(self) -> str:
        """n8n server base URL"""
        return 'http://localhost:5678'

    def test_n8n_health_check(self, n8n_base_url: str):
        """Test if n8n server is healthy"""
        try:
            response = requests.get(f'{n8n_base_url}/healthz', timeout=5)
            assert response.status_code == 200, "n8n health check failed"
            print("✓ n8n server is healthy")
        except requests.exceptions.ConnectionError:
            pytest.skip("n8n server is not running. Start with: n8n")

    def test_n8n_accessible(self, n8n_base_url: str):
        """Test if n8n web interface is accessible"""
        try:
            response = requests.get(n8n_base_url, timeout=5, allow_redirects=True)
            assert response.status_code in [200, 301, 302], "n8n interface not accessible"
            print("✓ n8n web interface is accessible")
        except requests.exceptions.ConnectionError:
            pytest.skip("n8n server is not running")


class TestWorkflowValidation:
    """Test suite for workflow JSON validation"""

    @pytest.fixture
    def workflow_path(self) -> str:
        """Path to workflow JSON file"""
        return 'workflows/chat_with_local_llms_ollama.json'

    def test_workflow_json_valid(self, workflow_path: str):
        """Test if workflow JSON is valid"""
        try:
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)
            
            assert isinstance(workflow, dict), "Workflow must be a JSON object"
            print("✓ Workflow JSON is valid")
        except FileNotFoundError:
            pytest.fail(f"Workflow file not found: {workflow_path}")
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in workflow file: {e}")

    def test_workflow_has_required_fields(self, workflow_path: str):
        """Test if workflow has all required fields"""
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        required_fields = ['name', 'nodes', 'connections']
        for field in required_fields:
            assert field in workflow, f"Missing required field: {field}"
        
        print("✓ Workflow has all required fields")

    def test_workflow_nodes_configuration(self, workflow_path: str):
        """Test workflow nodes configuration"""
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        nodes = workflow.get('nodes', [])
        assert len(nodes) > 0, "Workflow has no nodes"
        
        # Check for required node types
        node_types = [node.get('type') for node in nodes]
        
        # Should have at least: Chat Trigger, LLM Chain, Ollama Chat Model
        expected_nodes = [
            '@n8n/n8n-nodes-langchain.chatTrigger',
            '@n8n/n8n-nodes-langchain.chainLlm',
            '@n8n/n8n-nodes-langchain.lmChatOllama'
        ]
        
        for expected in expected_nodes:
            assert expected in node_types, f"Missing required node type: {expected}"
        
        print(f"✓ Workflow has {len(nodes)} nodes with correct types")

    def test_workflow_connections(self, workflow_path: str):
        """Test if workflow nodes are properly connected"""
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        connections = workflow.get('connections', {})
        assert len(connections) > 0, "Workflow has no connections between nodes"
        print("✓ Workflow nodes are connected")


@pytest.mark.integration
class TestEnvironmentSetup:
    """Test suite for environment setup validation"""

    def test_python_version(self):
        """Test if Python version is 3.8 or higher"""
        import sys
        version = sys.version_info
        assert version.major == 3 and version.minor >= 8, \
            f"Python 3.8+ required, found {version.major}.{version.minor}"
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")

    def test_required_packages_installed(self):
        """Test if required Python packages are installed"""
        required_packages = ['pytest', 'requests']
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✓ Package '{package}' is installed")
            except ImportError:
                pytest.fail(f"Required package not installed: {package}")

    def test_virtual_environment_active(self):
        """Test if running in a virtual environment"""
        import sys
        
        # Check if in virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if not in_venv:
            pytest.skip("Not running in virtual environment (recommended but not required)")
        else:
            print(f"✓ Virtual environment active: {sys.prefix}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
