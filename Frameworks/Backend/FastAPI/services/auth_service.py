"""
gRPC Auth Service Implementation
"""
import grpc
import bcrypt
import jwt
from datetime import datetime, timedelta
from concurrent import futures
import logging
import asyncio
from typing import Optional
import redis
import json

# Import generated protobuf classes
from protos import auth_pb2, auth_pb2_grpc, common_pb2
from google.protobuf.timestamp_pb2 import Timestamp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    """gRPC Auth Service Implementation"""
    
    def __init__(self, redis_client: redis.Redis, jwt_secret: str, jwt_algorithm: str = "HS256"):
        self.redis_client = redis_client
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def RegisterUser(self, request: auth_pb2.RegisterUserRequest, context: grpc.ServicerContext) -> auth_pb2.RegisterUserResponse:
        """Register a new user"""
        try:
            logger.info(f"Registration request for phone: {request.phone}")
            
            # Check if user already exists
            if self._user_exists(request.phone):
                return auth_pb2.RegisterUserResponse(
                    success=False,
                    message="User with this phone number already exists"
                )
            
            # Validate request
            validation_error = self._validate_registration_request(request)
            if validation_error:
                return auth_pb2.RegisterUserResponse(
                    success=False,
                    message=validation_error
                )
            
            # Hash password
            password_hash = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user data
            user_id = self._generate_user_id()
            user_data = {
                "user_id": user_id,
                "phone": request.phone,
                "email": request.email,
                "full_name": request.full_name,
                "password_hash": password_hash.decode('utf-8'),
                "country_code": request.country_code or "+1",
                "is_active": True,
                "is_verified": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "roles": ["user"]
            }
            
            # Store user in Redis (in production, use a database)
            self.redis_client.setex(
                f"user:{request.phone}",
                86400 * 30,  # 30 days expiration
                json.dumps(user_data)
            )
            
            # Create user data for response
            user_response = auth_pb2.UserData(
                user_id=user_id,
                phone=request.phone,
                email=request.email,
                full_name=request.full_name,
                is_active=True,
                is_verified=False,
                created_at=int(datetime.utcnow().timestamp()),
                updated_at=int(datetime.utcnow().timestamp()),
                country_code=request.country_code or "+1",
                roles=["user"]
            )
            
            logger.info(f"User registered successfully: {user_id}")
            return auth_pb2.RegisterUserResponse(
                success=True,
                message="User registered successfully",
                user_id=user_id,
                user=user_response
            )
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return auth_pb2.RegisterUserResponse(
                success=False,
                message="Internal server error"
            )
    
    def AuthenticateUser(self, request: auth_pb2.AuthenticateUserRequest, context: grpc.ServicerContext) -> auth_pb2.AuthenticateUserResponse:
        """Authenticate user and return tokens"""
        try:
            logger.info(f"Authentication request for phone: {request.phone}")
            
            # Get user data
            user_data = self._get_user_by_phone(request.phone)
            if not user_data:
                return auth_pb2.AuthenticateUserResponse(
                    success=False,
                    message="Invalid credentials"
                )
            
            # Verify password
            if not bcrypt.checkpw(request.password.encode('utf-8'), user_data["password_hash"].encode('utf-8')):
                return auth_pb2.AuthenticateUserResponse(
                    success=False,
                    message="Invalid credentials"
                )
            
            # Check if user is active
            if not user_data.get("is_active", False):
                return auth_pb2.AuthenticateUserResponse(
                    success=False,
                    message="Account is deactivated"
                )
            
            # Generate tokens
            access_token = self._create_access_token(user_data["user_id"])
            refresh_token = self._create_refresh_token(user_data["user_id"])
            
            # Store refresh token
            self.redis_client.setex(
                f"refresh_token:{user_data['user_id']}",
                86400 * self.refresh_token_expire_days,
                refresh_token
            )
            
            # Create user data for response
            user_response = auth_pb2.UserData(
                user_id=user_data["user_id"],
                phone=user_data["phone"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                is_active=user_data["is_active"],
                is_verified=user_data["is_verified"],
                created_at=int(datetime.fromisoformat(user_data["created_at"]).timestamp()),
                updated_at=int(datetime.fromisoformat(user_data["updated_at"]).timestamp()),
                country_code=user_data.get("country_code", "+1"),
                roles=user_data.get("roles", ["user"])
            )
            
            logger.info(f"User authenticated successfully: {user_data['user_id']}")
            return auth_pb2.AuthenticateUserResponse(
                success=True,
                message="Authentication successful",
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.access_token_expire_minutes * 60,
                user=user_response
            )
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return auth_pb2.AuthenticateUserResponse(
                success=False,
                message="Internal server error"
            )
    
    def ValidateToken(self, request: auth_pb2.ValidateTokenRequest, context: grpc.ServicerContext) -> auth_pb2.ValidateTokenResponse:
        """Validate JWT token"""
        try:
            # Decode token
            payload = jwt.decode(request.token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            
            if not user_id:
                return auth_pb2.ValidateTokenResponse(
                    valid=False,
                    message="Invalid token payload"
                )
            
            # Get user data
            user_data = self._get_user_by_id(user_id)
            if not user_data:
                return auth_pb2.ValidateTokenResponse(
                    valid=False,
                    message="User not found"
                )
            
            # Check if user is still active
            if not user_data.get("is_active", False):
                return auth_pb2.ValidateTokenResponse(
                    valid=False,
                    message="User account is deactivated"
                )
            
            # Create user data for response
            user_response = auth_pb2.UserData(
                user_id=user_data["user_id"],
                phone=user_data["phone"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                is_active=user_data["is_active"],
                is_verified=user_data["is_verified"],
                created_at=int(datetime.fromisoformat(user_data["created_at"]).timestamp()),
                updated_at=int(datetime.fromisoformat(user_data["updated_at"]).timestamp()),
                country_code=user_data.get("country_code", "+1"),
                roles=user_data.get("roles", ["user"])
            )
            
            return auth_pb2.ValidateTokenResponse(
                valid=True,
                message="Token is valid",
                user_id=user_id,
                user=user_response,
                expires_at=payload.get("exp", 0)
            )
            
        except jwt.ExpiredSignatureError:
            return auth_pb2.ValidateTokenResponse(
                valid=False,
                message="Token has expired"
            )
        except jwt.InvalidTokenError:
            return auth_pb2.ValidateTokenResponse(
                valid=False,
                message="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return auth_pb2.ValidateTokenResponse(
                valid=False,
                message="Internal server error"
            )
    
    def RefreshToken(self, request: auth_pb2.RefreshTokenRequest, context: grpc.ServicerContext) -> auth_pb2.RefreshTokenResponse:
        """Refresh access token using refresh token"""
        try:
            # Decode refresh token
            payload = jwt.decode(request.refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            
            if not user_id or payload.get("type") != "refresh":
                return auth_pb2.RefreshTokenResponse(
                    success=False,
                    message="Invalid refresh token"
                )
            
            # Check if refresh token exists in Redis
            stored_token = self.redis_client.get(f"refresh_token:{user_id}")
            if not stored_token or stored_token.decode('utf-8') != request.refresh_token:
                return auth_pb2.RefreshTokenResponse(
                    success=False,
                    message="Refresh token not found or invalid"
                )
            
            # Generate new tokens
            new_access_token = self._create_access_token(user_id)
            new_refresh_token = self._create_refresh_token(user_id)
            
            # Update refresh token in Redis
            self.redis_client.setex(
                f"refresh_token:{user_id}",
                86400 * self.refresh_token_expire_days,
                new_refresh_token
            )
            
            return auth_pb2.RefreshTokenResponse(
                success=True,
                message="Token refreshed successfully",
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_in=self.access_token_expire_minutes * 60
            )
            
        except jwt.ExpiredSignatureError:
            return auth_pb2.RefreshTokenResponse(
                success=False,
                message="Refresh token has expired"
            )
        except jwt.InvalidTokenError:
            return auth_pb2.RefreshTokenResponse(
                success=False,
                message="Invalid refresh token"
            )
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return auth_pb2.RefreshTokenResponse(
                success=False,
                message="Internal server error"
            )
    
    def LogoutUser(self, request: auth_pb2.LogoutUserRequest, context: grpc.ServicerContext) -> auth_pb2.LogoutUserResponse:
        """Logout user and invalidate refresh token"""
        try:
            # Remove refresh token from Redis
            self.redis_client.delete(f"refresh_token:{request.user_id}")
            
            # Add token to blacklist (optional - implement based on requirements)
            self.redis_client.setex(
                f"blacklist_token:{request.token}",
                3600,  # 1 hour (should match token expiry)
                "true"
            )
            
            logger.info(f"User logged out successfully: {request.user_id}")
            return auth_pb2.LogoutUserResponse(
                success=True,
                message="Logout successful"
            )
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return auth_pb2.LogoutUserResponse(
                success=False,
                message="Internal server error"
            )
    
    def ResetPassword(self, request: auth_pb2.ResetPasswordRequest, context: grpc.ServicerContext) -> auth_pb2.ResetPasswordResponse:
        """Reset user password"""
        try:
            # In a real implementation, you would verify the reset code
            # For now, we'll implement a basic version
            
            # Get user data
            user_data = self._get_user_by_phone(request.phone)
            if not user_data:
                return auth_pb2.ResetPasswordResponse(
                    success=False,
                    message="User not found"
                )
            
            # Hash new password
            new_password_hash = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt())
            
            # Update user data
            user_data["password_hash"] = new_password_hash.decode('utf-8')
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Store updated user data
            self.redis_client.setex(
                f"user:{request.phone}",
                86400 * 30,
                json.dumps(user_data)
            )
            
            # Invalidate all refresh tokens for this user
            self.redis_client.delete(f"refresh_token:{user_data['user_id']}")
            
            logger.info(f"Password reset successfully for user: {user_data['user_id']}")
            return auth_pb2.ResetPasswordResponse(
                success=True,
                message="Password reset successful"
            )
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return auth_pb2.ResetPasswordResponse(
                success=False,
                message="Internal server error"
            )
    
    # Helper methods
    
    def _user_exists(self, phone: str) -> bool:
        """Check if user exists"""
        return self.redis_client.exists(f"user:{phone}")
    
    def _get_user_by_phone(self, phone: str) -> Optional[dict]:
        """Get user data by phone"""
        user_data = self.redis_client.get(f"user:{phone}")
        if user_data:
            return json.loads(user_data.decode('utf-8'))
        return None
    
    def _get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user data by user ID"""
        # In a real implementation, you would have a proper database query
        # For now, we'll search through Redis keys (not efficient for production)
        for key in self.redis_client.scan_iter(match="user:*"):
            user_data = json.loads(self.redis_client.get(key).decode('utf-8'))
            if user_data.get("user_id") == user_id:
                return user_data
        return None
    
    def _validate_registration_request(self, request: auth_pb2.RegisterUserRequest) -> Optional[str]:
        """Validate registration request"""
        if not request.phone or len(request.phone) < 10:
            return "Invalid phone number"
        
        if not request.email or "@" not in request.email:
            return "Invalid email address"
        
        if not request.password or len(request.password) < 8:
            return "Password must be at least 8 characters"
        
        if not request.full_name or len(request.full_name.strip()) < 2:
            return "Full name is required"
        
        return None
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _create_access_token(self, user_id: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)


async def serve():
    """Start the gRPC Auth Service"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Initialize Redis client
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    # Add Auth Service
    auth_servicer = AuthServicer(
        redis_client=redis_client,
        jwt_secret="your-super-secret-jwt-key-here"
    )
    auth_pb2_grpc.add_AuthServiceServicer_to_server(auth_servicer, server)
    
    # Configure server
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting Auth Service gRPC server on {listen_addr}")
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down Auth Service...")
        await server.stop(5)


if __name__ == '__main__':
    import asyncio
    asyncio.run(serve())
