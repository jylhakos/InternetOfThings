"""
Test gRPC Auth Service Integration
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import json

# Test the gRPC integration without requiring actual gRPC services to be running
class TestGRPCAuthIntegration:
    """Test gRPC Auth Service integration with FastAPI"""
    
    @pytest.fixture
    def mock_auth_response(self):
        """Mock auth service response"""
        return {
            "success": True,
            "message": "Authentication successful",
            "access_token": "mock_jwt_token_12345",
            "refresh_token": "mock_refresh_token_12345",
            "expires_in": 1800,
            "user": {
                "user_id": "user_123",
                "phone": "+1234567890",
                "email": "test@example.com",
                "full_name": "Test User",
                "is_active": True,
                "is_verified": False
            }
        }
    
    @pytest.fixture
    def mock_registration_response(self):
        """Mock registration service response"""
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "user_id": "user_456",
                "phone": "+1234567890",
                "email": "test@example.com",
                "full_name": "Test User",
                "is_active": True,
                "is_verified": False
            }
        }
    
    @pytest.mark.asyncio
    async def test_user_registration_with_grpc(self, mock_registration_response):
        """Test user registration via gRPC"""
        with patch('services.auth_client.AuthServiceClient') as mock_client:
            # Setup mock
            mock_instance = AsyncMock()
            mock_instance.register_user.return_value = mock_registration_response
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Import after patching
            from services.auth_client import register_user_async
            
            result = await register_user_async(
                phone="+1234567890",
                email="test@example.com",
                password="securepass123",
                full_name="Test User"
            )
            
            assert result["success"] is True
            assert result["user"]["phone"] == "+1234567890"
            assert result["user"]["email"] == "test@example.com"
            
            # Verify gRPC call was made
            mock_instance.register_user.assert_called_once_with(
                "+1234567890",
                "test@example.com", 
                "securepass123",
                "Test User",
                None
            )
    
    @pytest.mark.asyncio
    async def test_user_authentication_with_grpc(self, mock_auth_response):
        """Test user authentication via gRPC"""
        with patch('services.auth_client.AuthServiceClient') as mock_client:
            # Setup mock
            mock_instance = AsyncMock()
            mock_instance.authenticate_user.return_value = mock_auth_response
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Import after patching
            from services.auth_client import authenticate_user_async
            
            result = await authenticate_user_async(
                phone="+1234567890",
                password="securepass123"
            )
            
            assert result["success"] is True
            assert result["access_token"] == "mock_jwt_token_12345"
            assert result["user"]["user_id"] == "user_123"
            
            # Verify gRPC call was made
            mock_instance.authenticate_user.assert_called_once_with(
                "+1234567890",
                "securepass123"
            )
    
    @pytest.mark.asyncio
    async def test_token_validation_with_grpc(self):
        """Test token validation via gRPC"""
        mock_validation_response = {
            "valid": True,
            "message": "Token is valid",
            "user": {
                "user_id": "user_123",
                "phone": "+1234567890",
                "email": "test@example.com"
            },
            "expires_at": 1234567890
        }
        
        with patch('services.auth_client.AuthServiceClient') as mock_client:
            # Setup mock
            mock_instance = AsyncMock()
            mock_instance.validate_token.return_value = mock_validation_response
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Import after patching
            from services.auth_client import validate_token_async
            
            result = await validate_token_async("mock_jwt_token_12345")
            
            assert result["valid"] is True
            assert result["user"]["user_id"] == "user_123"
            
            # Verify gRPC call was made
            mock_instance.validate_token.assert_called_once_with("mock_jwt_token_12345")
    
    @pytest.mark.asyncio
    async def test_grpc_service_error_handling(self):
        """Test gRPC service error handling"""
        with patch('services.auth_client.AuthServiceClient') as mock_client:
            # Setup mock to raise exception
            mock_instance = AsyncMock()
            mock_instance.authenticate_user.side_effect = Exception("gRPC connection failed")
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Import after patching
            from services.auth_client import authenticate_user_async
            
            result = await authenticate_user_async("+1234567890", "password")
            
            # Should return error response
            assert result["success"] is False
            assert "error" in result["message"].lower()


class TestProtocolBuffers:
    """Test Protocol Buffer message generation and serialization"""
    
    def test_proto_file_structure(self):
        """Test that proto files exist and have correct structure"""
        import os
        
        proto_files = [
            "protos/auth.proto",
            "protos/user.proto", 
            "protos/common.proto"
        ]
        
        for proto_file in proto_files:
            assert os.path.exists(proto_file), f"{proto_file} should exist"
            
            with open(proto_file, 'r') as f:
                content = f.read()
                assert 'syntax = "proto3";' in content
                assert 'service' in content or 'message' in content
    
    def test_generated_pb2_files_exist(self):
        """Test that generated Python files exist after running generate_grpc.sh"""
        import os
        
        # Note: These files are generated by running ./generate_grpc.sh
        generated_files = [
            "protos/auth_pb2.py",
            "protos/auth_pb2_grpc.py",
            "protos/user_pb2.py", 
            "protos/user_pb2_grpc.py",
            "protos/common_pb2.py",
            "protos/common_pb2_grpc.py"
        ]
        
        for gen_file in generated_files:
            if os.path.exists(gen_file):
                # File exists, check it has content
                with open(gen_file, 'r') as f:
                    content = f.read()
                    assert len(content) > 0, f"{gen_file} should not be empty"
                    assert "# Generated by the protocol buffer compiler" in content
            else:
                # File doesn't exist - user needs to run generate_grpc.sh
                pytest.skip(f"{gen_file} not found. Please run ./generate_grpc.sh first")


class TestGRPCServiceStartup:
    """Test gRPC service startup and configuration"""
    
    def test_auth_service_configuration(self):
        """Test Auth service configuration"""
        # This would test the actual service startup
        # For now, just verify the service file exists and imports correctly
        import os
        
        assert os.path.exists("services/auth_service.py")
        
        # Try to import (will fail if syntax errors)
        try:
            import services.auth_service
            assert hasattr(services.auth_service, 'AuthServicer')
            assert hasattr(services.auth_service, 'serve')
        except ImportError as e:
            pytest.skip(f"Cannot import auth_service: {e}")
    
    def test_auth_client_configuration(self):
        """Test Auth client configuration"""
        import os
        
        assert os.path.exists("services/auth_client.py")
        
        # Try to import client
        try:
            import services.auth_client
            assert hasattr(services.auth_client, 'AuthServiceClient')
            assert hasattr(services.auth_client, 'SyncAuthServiceClient')
        except ImportError as e:
            pytest.skip(f"Cannot import auth_client: {e}")


# Integration test fixtures
@pytest.fixture
def test_user_data():
    """Test user data for registration"""
    return {
        "phone": "+1234567890",
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User",
        "country_code": "+1"
    }


@pytest.fixture
def test_login_data():
    """Test login data"""
    return {
        "phone": "+1234567890", 
        "password": "SecurePassword123!"
    }


# Performance tests
class TestGRPCPerformance:
    """Test gRPC performance characteristics"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_auth_requests(self):
        """Test concurrent authentication requests"""
        mock_response = {
            "success": True,
            "access_token": "token_123",
            "expires_in": 1800
        }
        
        with patch('services.auth_client.AuthServiceClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.authenticate_user.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            from services.auth_client import authenticate_user_async
            
            # Run 10 concurrent authentication requests
            tasks = []
            for i in range(10):
                task = authenticate_user_async(f"+123456789{i}", "password")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 10
            for result in results:
                assert result["success"] is True
            
            # Verify all calls were made
            assert mock_instance.authenticate_user.call_count == 10


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
