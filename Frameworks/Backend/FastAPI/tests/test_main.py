"""
Test suite for FastAPI microservices
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app

# Test client
client = TestClient(app)

class TestHealth:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_user_registration(self):
        """Test user registration"""
        user_data = {
            "phone": "+1234567890",
            "password": "testpassword123",
            "email": "test@example.com"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert data["phone"] == user_data["phone"]
    
    def test_user_login(self):
        """Test user login"""
        login_data = {
            "phone": "+1234567890",
            "password": "testpassword123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/users/profile")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth

class TestCache:
    """Test caching functionality"""
    
    def test_cache_set_and_get(self):
        """Test setting and getting cache values"""
        # Set cache value
        response = client.get("/cache/test/testkey?value=testvalue")
        assert response.status_code in [200, 503]  # 503 if Redis not available
        
        if response.status_code == 200:
            data = response.json()
            assert "Cached testkey = testvalue" in data["message"]
            
            # Get cache value
            response = client.get("/cache/test/testkey")
            assert response.status_code == 200
            data = response.json()
            assert data["key"] == "testkey"
            assert data["value"] == "testvalue"

class TestPerformance:
    """Test performance endpoints"""
    
    def test_heavy_operation(self):
        """Test heavy operation endpoint"""
        response = client.get("/performance/heavy")
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "processing_time" in data
        assert data["status"] == "completed"
        assert isinstance(data["processing_time"], (int, float))

class TestDebug:
    """Test debugging endpoints"""
    
    def test_debug_endpoint_positive(self):
        """Test debug endpoint with positive value"""
        response = client.get("/debug/123")
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 123
        assert data["processed"] is True
    
    def test_debug_endpoint_negative(self):
        """Test debug endpoint with negative value"""
        response = client.get("/debug/-1")
        assert response.status_code == 400
        data = response.json()
        assert "Item ID must be positive" in data["detail"]

class TestValidation:
    """Test Pydantic validation"""
    
    def test_invalid_registration_data(self):
        """Test registration with invalid data"""
        invalid_data = {
            "phone": "",  # Empty phone
            "password": "123",  # Too short
            "email": "invalid-email"  # Invalid email format
        }
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_async_client():
    """Test with async client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
