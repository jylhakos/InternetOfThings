"""
Load testing script for FastAPI application using Locust
"""

from locust import HttpUser, task, between
import json
import random

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts"""
        # Register and login to get token
        self.register_and_login()
    
    def register_and_login(self):
        """Register a user and login to get auth token"""
        phone = f"+123456789{random.randint(0, 9)}"
        user_data = {
            "phone": phone,
            "password": "testpassword123",
            "email": f"test{random.randint(0, 9999)}@example.com"
        }
        
        # Register user
        response = self.client.post("/auth/register", json=user_data)
        if response.status_code == 200:
            # Login to get token
            login_data = {
                "phone": phone,
                "password": "testpassword123"
            }
            response = self.client.post("/auth/login", json=login_data)
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {token}"}
            else:
                self.headers = {}
        else:
            self.headers = {}
    
    @task(3)
    def test_health_check(self):
        """Test health check endpoint - most frequent"""
        self.client.get("/health")
    
    @task(2)
    def test_heavy_operation(self):
        """Test heavy operation endpoint"""
        self.client.get("/performance/heavy")
    
    @task(1)
    def test_debug_endpoint(self):
        """Test debug endpoint"""
        item_id = random.randint(1, 1000)
        self.client.get(f"/debug/{item_id}")
    
    @task(1)
    def test_cache_operations(self):
        """Test cache operations"""
        key = f"test_key_{random.randint(1, 100)}"
        value = f"test_value_{random.randint(1, 1000)}"
        
        # Set cache
        self.client.get(f"/cache/test/{key}?value={value}")
        
        # Get cache
        self.client.get(f"/cache/test/{key}")
    
    @task(1)
    def test_protected_endpoint(self):
        """Test protected endpoint with authentication"""
        if hasattr(self, 'headers') and self.headers:
            self.client.get("/users/profile", headers=self.headers)
    
    @task(1)
    def test_registration(self):
        """Test user registration"""
        phone = f"+123456789{random.randint(1000, 9999)}"
        user_data = {
            "phone": phone,
            "password": "testpassword123",
            "email": f"test{random.randint(0, 99999)}@example.com"
        }
        self.client.post("/auth/register", json=user_data)
