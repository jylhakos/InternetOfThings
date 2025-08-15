"""
gRPC Client for FastAPI to communicate with Auth Service
"""
import grpc
import logging
from typing import Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import generated protobuf classes
from protos import auth_pb2, auth_pb2_grpc

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """gRPC client for Auth Service"""
    
    def __init__(self, server_url: str = "localhost:50051"):
        self.server_url = server_url
        self.channel = None
        self.stub = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.channel = grpc.aio.insecure_channel(self.server_url)
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.channel:
            await self.channel.close()
    
    async def register_user(self, phone: str, email: str, password: str, 
                          full_name: str, country_code: str = None) -> Dict[str, Any]:
        """Register a new user"""
        try:
            request = auth_pb2.RegisterUserRequest(
                phone=phone,
                email=email,
                password=password,
                full_name=full_name,
                country_code=country_code
            )
            
            response = await self.stub.RegisterUser(request)
            
            result = {
                "success": response.success,
                "message": response.message
            }
            
            if response.success and response.user:
                result["user"] = {
                    "user_id": response.user.user_id,
                    "phone": response.user.phone,
                    "email": response.user.email,
                    "full_name": response.user.full_name,
                    "is_active": response.user.is_active,
                    "is_verified": response.user.is_verified,
                    "country_code": response.user.country_code,
                    "roles": list(response.user.roles)
                }
            
            return result
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error in register_user: {e}")
            return {"success": False, "message": f"Service error: {e.details()}"}
        except Exception as e:
            logger.error(f"Error in register_user: {e}")
            return {"success": False, "message": "Internal error"}
    
    async def authenticate_user(self, phone: str, password: str) -> Dict[str, Any]:
        """Authenticate user and get tokens"""
        try:
            request = auth_pb2.AuthenticateUserRequest(
                phone=phone,
                password=password
            )
            
            response = await self.stub.AuthenticateUser(request)
            
            result = {
                "success": response.success,
                "message": response.message
            }
            
            if response.success:
                result.update({
                    "access_token": response.access_token,
                    "refresh_token": response.refresh_token,
                    "expires_in": response.expires_in
                })
                
                if response.user:
                    result["user"] = {
                        "user_id": response.user.user_id,
                        "phone": response.user.phone,
                        "email": response.user.email,
                        "full_name": response.user.full_name,
                        "is_active": response.user.is_active,
                        "is_verified": response.user.is_verified,
                        "country_code": response.user.country_code,
                        "roles": list(response.user.roles)
                    }
            
            return result
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error in authenticate_user: {e}")
            return {"success": False, "message": f"Service error: {e.details()}"}
        except Exception as e:
            logger.error(f"Error in authenticate_user: {e}")
            return {"success": False, "message": "Internal error"}
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token"""
        try:
            request = auth_pb2.ValidateTokenRequest(token=token)
            response = await self.stub.ValidateToken(request)
            
            result = {
                "valid": response.valid,
                "message": response.message
            }
            
            if response.valid and response.user:
                result["user"] = {
                    "user_id": response.user.user_id,
                    "phone": response.user.phone,
                    "email": response.user.email,
                    "full_name": response.user.full_name,
                    "is_active": response.user.is_active,
                    "is_verified": response.user.is_verified,
                    "country_code": response.user.country_code,
                    "roles": list(response.user.roles)
                }
                result["expires_at"] = response.expires_at
            
            return result
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error in validate_token: {e}")
            return {"valid": False, "message": f"Service error: {e.details()}"}
        except Exception as e:
            logger.error(f"Error in validate_token: {e}")
            return {"valid": False, "message": "Internal error"}
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            request = auth_pb2.RefreshTokenRequest(refresh_token=refresh_token)
            response = await self.stub.RefreshToken(request)
            
            result = {
                "success": response.success,
                "message": response.message
            }
            
            if response.success:
                result.update({
                    "access_token": response.access_token,
                    "refresh_token": response.refresh_token,
                    "expires_in": response.expires_in
                })
            
            return result
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error in refresh_token: {e}")
            return {"success": False, "message": f"Service error: {e.details()}"}
        except Exception as e:
            logger.error(f"Error in refresh_token: {e}")
            return {"success": False, "message": "Internal error"}
    
    async def logout_user(self, token: str, user_id: str) -> Dict[str, Any]:
        """Logout user"""
        try:
            request = auth_pb2.LogoutUserRequest(token=token, user_id=user_id)
            response = await self.stub.LogoutUser(request)
            
            return {
                "success": response.success,
                "message": response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error in logout_user: {e}")
            return {"success": False, "message": f"Service error: {e.details()}"}
        except Exception as e:
            logger.error(f"Error in logout_user: {e}")
            return {"success": False, "message": "Internal error"}


# Synchronous client for non-async usage
class SyncAuthServiceClient:
    """Synchronous gRPC client for Auth Service"""
    
    def __init__(self, server_url: str = "localhost:50051"):
        self.server_url = server_url
    
    def _call_async_method(self, coro):
        """Helper to call async methods from sync context"""
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If we're in an existing event loop, use a thread
            with ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: asyncio.run(coro))
                return future.result()
        else:
            return loop.run_until_complete(coro)
    
    def register_user(self, phone: str, email: str, password: str, 
                     full_name: str, country_code: str = None) -> Dict[str, Any]:
        """Register a new user (sync)"""
        async def _register():
            async with AuthServiceClient(self.server_url) as client:
                return await client.register_user(phone, email, password, full_name, country_code)
        
        return self._call_async_method(_register())
    
    def authenticate_user(self, phone: str, password: str) -> Dict[str, Any]:
        """Authenticate user (sync)"""
        async def _auth():
            async with AuthServiceClient(self.server_url) as client:
                return await client.authenticate_user(phone, password)
        
        return self._call_async_method(_auth())
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate token (sync)"""
        async def _validate():
            async with AuthServiceClient(self.server_url) as client:
                return await client.validate_token(token)
        
        return self._call_async_method(_validate())
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh token (sync)"""
        async def _refresh():
            async with AuthServiceClient(self.server_url) as client:
                return await client.refresh_token(refresh_token)
        
        return self._call_async_method(_refresh())
    
    def logout_user(self, token: str, user_id: str) -> Dict[str, Any]:
        """Logout user (sync)"""
        async def _logout():
            async with AuthServiceClient(self.server_url) as client:
                return await client.logout_user(token, user_id)
        
        return self._call_async_method(_logout())


# Global client instance
auth_client = SyncAuthServiceClient()

# Convenience functions
async def register_user_async(phone: str, email: str, password: str, 
                            full_name: str, country_code: str = None) -> Dict[str, Any]:
    """Async convenience function for user registration"""
    async with AuthServiceClient() as client:
        return await client.register_user(phone, email, password, full_name, country_code)

async def authenticate_user_async(phone: str, password: str) -> Dict[str, Any]:
    """Async convenience function for user authentication"""
    async with AuthServiceClient() as client:
        return await client.authenticate_user(phone, password)

async def validate_token_async(token: str) -> Dict[str, Any]:
    """Async convenience function for token validation"""
    async with AuthServiceClient() as client:
        return await client.validate_token(token)
