#!/usr/bin/env python3
"""
Open WebUI Integration Test Script
Tests Docker setup, API compatibility, and generates proper configuration commands.
"""

import requests
import json
import subprocess
import time
import sys
import os

class OpenWebUITester:
    def __init__(self):
        self.fastapi_url = "http://localhost:8000"
        self.openwebui_url = "http://localhost:3001"
        self.api_key = "dummy-key"
    
    def check_fastapi_server(self):
        """Check if FastAPI server is running and responsive."""
        print("🔍 Checking FastAPI Server...")
        try:
            response = requests.get(f"{self.fastapi_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FastAPI server is running")
                print(f"   Status: {data.get('status')}")
                print(f"   Redis: {data.get('redis')}")
                return True
            else:
                print(f"❌ FastAPI server responded with HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ FastAPI server is not accessible: {e}")
            return False
    
    def test_openai_endpoints(self):
        """Test OpenAI-compatible endpoints required by Open WebUI."""
        print("\n🤖 Testing OpenAI Compatibility...")
        
        # Test /v1/models endpoint
        try:
            response = requests.get(
                f"{self.fastapi_url}/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                print(f"✅ /v1/models endpoint working ({len(models)} models)")
                for model in models[:3]:
                    print(f"   - {model.get('id', 'unknown')}")
            else:
                print(f"❌ /v1/models failed with HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ /v1/models error: {e}")
            return False
        
        # Test /v1/chat/completions endpoint
        try:
            test_request = {
                "model": "llama3.2:1b",
                "messages": [
                    {"role": "user", "content": "Hello, this is a test message."}
                ],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.fastapi_url}/v1/chat/completions",
                json=test_request,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                choices = data.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '')
                    print(f"✅ /v1/chat/completions working")
                    print(f"   Response: {content[:50]}...")
                else:
                    print("❌ /v1/chat/completions returned no choices")
                    return False
            else:
                print(f"❌ /v1/chat/completions failed with HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"❌ /v1/chat/completions error: {e}")
            return False
        
        return True
    
    def check_docker_availability(self):
        """Check if Docker is available and running."""
        print("\n🐳 Checking Docker Availability...")
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker is available: {result.stdout.strip()}")
                
                # Check if Docker daemon is running
                result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Docker daemon is running")
                    return True
                else:
                    print("❌ Docker daemon is not running")
                    return False
            else:
                print("❌ Docker is not installed")
                return False
        except FileNotFoundError:
            print("❌ Docker command not found")
            return False
    
    def check_existing_containers(self):
        """Check for existing Open WebUI containers."""
        print("\n📦 Checking Existing Containers...")
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', 'name=open-webui', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output and 'open-webui' in output:
                    print("📋 Existing Open WebUI containers:")
                    print(output)
                    return True
                else:
                    print("ℹ️ No existing Open WebUI containers found")
                    return False
            else:
                print("❌ Failed to check containers")
                return False
        except Exception as e:
            print(f"❌ Error checking containers: {e}")
            return False
    
    def generate_docker_commands(self):
        """Generate proper Docker commands for Open WebUI setup."""
        print("\n🛠️ Docker Setup Commands for Open WebUI")
        print("=" * 50)
        
        # Stop existing containers
        print("### Stop any existing Open WebUI containers:")
        print("```bash")
        print("docker stop open-webui 2>/dev/null || true")
        print("docker rm open-webui 2>/dev/null || true")
        print("```")
        
        # Basic Docker run command
        print("\n### Start Open WebUI with FastAPI backend:")
        print("```bash")
        docker_cmd = f"""docker run -d \\
  --name open-webui \\
  -p 3001:8080 \\
  -e OPENAI_API_BASE_URL="http://host.docker.internal:8000/v1" \\
  -e OPENAI_API_KEY="{self.api_key}" \\
  -v open-webui:/app/backend/data \\
  --add-host=host.docker.internal:host-gateway \\
  --restart unless-stopped \\
  ghcr.io/open-webui/open-webui:main"""
        print(docker_cmd)
        print("```")
        
        # Alternative for Linux
        print("\n### Alternative for Linux (if host.docker.internal doesn't work):")
        print("```bash")
        docker_cmd_linux = f"""docker run -d \\
  --name open-webui \\
  -p 3001:8080 \\
  -e OPENAI_API_BASE_URL="http://172.17.0.1:8000/v1" \\
  -e OPENAI_API_KEY="{self.api_key}" \\
  -v open-webui:/app/backend/data \\
  --restart unless-stopped \\
  ghcr.io/open-webui/open-webui:main"""
        print(docker_cmd_linux)
        print("```")
        
        # Docker Compose version
        print("\n### Docker Compose Configuration:")
        print("```yaml")
        compose_config = f"""version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: redis-queue-open-webui
    ports:
      - "3001:8080"
    environment:
      - OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1
      - OPENAI_API_KEY={self.api_key}
      - WEBUI_SECRET_KEY=your-secret-key-here
    volumes:
      - open-webui:/app/backend/data
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped
    depends_on:
      - fastapi

  fastapi:
    # Your existing FastAPI service configuration
    build: .
    ports:
      - "8000:8000"
    # ... other FastAPI configurations

volumes:
  open-webui:"""
        print(compose_config)
        print("```")
    
    def test_connection_to_openwebui(self):
        """Test connection to Open WebUI if it's running."""
        print("\n🌐 Testing Open WebUI Connection...")
        try:
            response = requests.get(f"{self.openwebui_url}", timeout=5)
            if response.status_code == 200:
                print("✅ Open WebUI is accessible")
                print(f"   URL: {self.openwebui_url}")
                return True
            else:
                print(f"❌ Open WebUI responded with HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"ℹ️ Open WebUI is not running: {e}")
            return False
    
    def generate_curl_tests(self):
        """Generate cURL commands to test the API."""
        print("\n📝 cURL Test Commands")
        print("=" * 50)
        
        curl_tests = [
            {
                "name": "Health Check",
                "curl": f'curl -s "{self.fastapi_url}/health" | jq .'
            },
            {
                "name": "List Models (OpenAI format)",
                "curl": f'curl -s -H "Authorization: Bearer {self.api_key}" "{self.fastapi_url}/v1/models" | jq .'
            },
            {
                "name": "Chat Completion Test",
                "curl": f'''curl -X POST "{self.fastapi_url}/v1/chat/completions" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer {self.api_key}" \\
  -d '{{
    "model": "llama3.2:1b",
    "messages": [
      {{"role": "user", "content": "Hello! Can you help me test this API?"}}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }}' | jq .'''
            },
            {
                "name": "Async Chat Request",
                "curl": f'''curl -X POST "{self.fastapi_url}/chat" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "prompt": "What is machine learning?",
    "model": "llama3.2:1b",
    "temperature": 0.7,
    "max_tokens": 150
  }}' | jq .'''
            }
        ]
        
        for test in curl_tests:
            print(f"\n### {test['name']}")
            print("```bash")
            print(test['curl'])
            print("```")
    
    def generate_open_webui_setup_guide(self):
        """Generate complete setup guide for Open WebUI."""
        print("\n📚 Complete Open WebUI Setup Guide")
        print("=" * 60)
        
        guide = f"""
## Prerequisites
1. FastAPI server running on port 8000
2. Docker installed and running
3. Redis Queue system operational

## Step 1: Verify FastAPI is ready
```bash
curl {self.fastapi_url}/health
curl -H "Authorization: Bearer {self.api_key}" {self.fastapi_url}/v1/models
```

## Step 2: Start Open WebUI
```bash
# Remove any existing container
docker stop open-webui 2>/dev/null || true
docker rm open-webui 2>/dev/null || true

# Start Open WebUI
docker run -d \\
  --name open-webui \\
  -p 3001:8080 \\
  -e OPENAI_API_BASE_URL="http://host.docker.internal:8000/v1" \\
  -e OPENAI_API_KEY="{self.api_key}" \\
  -v open-webui:/app/backend/data \\
  --add-host=host.docker.internal:host-gateway \\
  --restart unless-stopped \\
  ghcr.io/open-webui/open-webui:main

# Check if it's running
docker ps | grep open-webui
```

## Step 3: Access Open WebUI
1. Open browser to: http://localhost:3001
2. Create an account (first user becomes admin)
3. Go to Settings → Models
4. Verify that models from your FastAPI server are available

## Step 4: Configure Custom Models (if needed)
1. Settings → Models → Add Model
2. Model ID: llama3.2:1b
3. Base URL: http://host.docker.internal:8000/v1
4. API Key: {self.api_key}

## Troubleshooting
- If "host.docker.internal" doesn't work, try "172.17.0.1" instead
- Check logs: `docker logs open-webui`
- Test API directly: `curl http://localhost:3001`
- Verify network connectivity: `docker exec open-webui ping host.docker.internal`
"""
        print(guide)
    
    def run_complete_test(self):
        """Run complete Open WebUI integration test."""
        print("🚀 Open WebUI Integration Test Suite")
        print("=" * 60)
        
        # Check prerequisites
        fastapi_ok = self.check_fastapi_server()
        if not fastapi_ok:
            print("\n❌ FastAPI server is not ready. Please start it first:")
            print("   python main.py")
            return False
        
        openai_ok = self.test_openai_endpoints()
        if not openai_ok:
            print("\n❌ OpenAI endpoints are not working properly")
            return False
        
        docker_ok = self.check_docker_availability()
        self.check_existing_containers()
        
        # Generate setup instructions
        self.generate_docker_commands()
        self.generate_curl_tests()
        
        # Test Open WebUI if running
        webui_running = self.test_connection_to_openwebui()
        
        # Generate complete guide
        self.generate_open_webui_setup_guide()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"✅ FastAPI Server: {'Ready' if fastapi_ok else 'Not Ready'}")
        print(f"✅ OpenAI Endpoints: {'Working' if openai_ok else 'Failed'}")
        print(f"✅ Docker: {'Available' if docker_ok else 'Not Available'}")
        print(f"✅ Open WebUI: {'Running' if webui_running else 'Not Running'}")
        
        if fastapi_ok and openai_ok:
            print("\n🎉 Your API is ready for Open WebUI integration!")
            print(f"   FastAPI Base URL: {self.fastapi_url}/v1")
            print(f"   API Key: {self.api_key}")
            print(f"   Open WebUI URL: {self.openwebui_url}")
        else:
            print("\n⚠️ Please fix the issues above before proceeding with Open WebUI setup")
        
        return fastapi_ok and openai_ok

def main():
    """Main execution function."""
    if len(sys.argv) > 1:
        tester = OpenWebUITester()
        
        if sys.argv[1] == "quick":
            tester.check_fastapi_server()
            tester.test_openai_endpoints()
        elif sys.argv[1] == "docker":
            tester.generate_docker_commands()
        elif sys.argv[1] == "curl":
            tester.generate_curl_tests()
        elif sys.argv[1] == "guide":
            tester.generate_open_webui_setup_guide()
        else:
            print("Usage: python test_openwebui_integration.py [quick|docker|curl|guide]")
    else:
        tester = OpenWebUITester()
        tester.run_complete_test()

if __name__ == "__main__":
    main()
