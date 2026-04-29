"""
Helper utilities for n8n workflow management and testing.
"""

import requests
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class OllamaClient:
    """Client for interacting with Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')

    def check_health(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_models(self) -> List[str]:
        """List all available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.exceptions.RequestException:
            return []

    def generate(self, model: str, prompt: str, stream: bool = False) -> Optional[str]:
        """Generate text using specified model"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('response')
            return None
        except requests.exceptions.RequestException:
            return None


class N8nClient:
    """Client for interacting with n8n API"""

    def __init__(self, base_url: str = "http://localhost:5678"):
        self.base_url = base_url.rstrip('/')

    def check_health(self) -> bool:
        """Check if n8n server is running"""
        try:
            response = requests.get(f"{self.base_url}/healthz", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def is_accessible(self) -> bool:
        """Check if n8n web interface is accessible"""
        try:
            response = requests.get(self.base_url, timeout=5, allow_redirects=True)
            return response.status_code in [200, 301, 302]
        except requests.exceptions.RequestException:
            return False


class WorkflowValidator:
    """Validator for n8n workflow JSON files"""

    @staticmethod
    def load_workflow(filepath: str) -> Dict[str, Any]:
        """Load and parse workflow JSON file"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {filepath}")

        with path.open('r') as f:
            return json.load(f)

    @staticmethod
    def validate_structure(workflow: Dict[str, Any]) -> bool:
        """Validate basic workflow structure"""
        required_fields = ['name', 'nodes', 'connections']
        return all(field in workflow for field in required_fields)

    @staticmethod
    def get_node_types(workflow: Dict[str, Any]) -> List[str]:
        """Extract all node types from workflow"""
        nodes = workflow.get('nodes', [])
        return [node.get('type') for node in nodes if 'type' in node]

    @staticmethod
    def has_required_nodes(workflow: Dict[str, Any]) -> bool:
        """Check if workflow has all required node types"""
        node_types = WorkflowValidator.get_node_types(workflow)
        required_nodes = [
            '@n8n/n8n-nodes-langchain.chatTrigger',
            '@n8n/n8n-nodes-langchain.chainLlm',
            '@n8n/n8n-nodes-langchain.lmChatOllama'
        ]
        return all(node_type in node_types for node_type in required_nodes)


class EnvironmentChecker:
    """Check if environment is properly configured"""

    @staticmethod
    def check_python_version() -> bool:
        """Check if Python version is 3.8+"""
        import sys
        version = sys.version_info
        return version.major == 3 and version.minor >= 8

    @staticmethod
    def check_virtual_env() -> bool:
        """Check if running in virtual environment"""
        import sys
        return hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

    @staticmethod
    def check_required_packages() -> Dict[str, bool]:
        """Check if required packages are installed"""
        required = ['pytest', 'requests', 'dotenv']
        results = {}

        for package in required:
            try:
                if package == 'dotenv':
                    __import__('dotenv')
                else:
                    __import__(package)
                results[package] = True
            except ImportError:
                results[package] = False

        return results

    @staticmethod
    def full_check() -> Dict[str, Any]:
        """Perform complete environment check"""
        return {
            'python_version_ok': EnvironmentChecker.check_python_version(),
            'virtual_env': EnvironmentChecker.check_virtual_env(),
            'packages': EnvironmentChecker.check_required_packages(),
            'ollama': OllamaClient().check_health(),
            'n8n': N8nClient().check_health()
        }


def print_status_report():
    """Print comprehensive status report"""
    print("=" * 60)
    print("n8n + Ollama Environment Status Report")
    print("=" * 60)

    checker = EnvironmentChecker()
    status = checker.full_check()

    print(f"\n📊 Python Environment:")
    print(f"  Python 3.8+: {'✓' if status['python_version_ok'] else '✗'}")
    print(f"  Virtual Env: {'✓' if status['virtual_env'] else '✗ (recommended)'}")

    print(f"\n📦 Python Packages:")
    for package, installed in status['packages'].items():
        print(f"  {package}: {'✓' if installed else '✗'}")

    print(f"\n🤖 Services:")
    print(f"  Ollama: {'✓ Running' if status['ollama'] else '✗ Not running'}")
    print(f"  n8n: {'✓ Running' if status['n8n'] else '✗ Not running'}")

    if status['ollama']:
        ollama = OllamaClient()
        models = ollama.list_models()
        print(f"\n🗂️  Available Models:")
        if models:
            for model in models:
                print(f"  - {model}")
        else:
            print("  No models installed. Run: ollama pull llama2")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_status_report()
