"""
FastAPI: authentication, caching, monitoring, and gRPC integration
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import redis
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# gRPC client import (will be available after running generate_grpc.sh)
try:
    from services.auth_client import AuthServiceClient, auth_client
    GRPC_AVAILABLE = True
    logger.info("gRPC Auth Service client loaded successfully")
except ImportError:
    logger.warning("gRPC client not available. Please run ./generate_grpc.sh first")
    GRPC_AVAILABLE = False

# Configuration
class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/microservices"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "your-super-secret-jwt-key"
    debug: bool = True
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"

settings = Settings()

# Redis client
try:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    redis_client.ping()
    logger.info("Connected to Redis")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    redis_client = None

# OpenTelemetry setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

if not settings.debug:
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

# Pydantic Models
class UserRegistration(BaseModel):
    phone: str
    password: str
    email: str
    full_name: str
    country_code: Optional[str] = "+1"

class UserLogin(BaseModel):
    phone: str
    password: str

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    services: dict

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FastAPI application")
    if redis_client:
        await redis_client.set("app_status", "running")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application")
    if redis_client:
        await redis_client.set("app_status", "shutdown")

# FastAPI app
app = FastAPI(
    title="FastAPI Microservices",
    description="A comprehensive microservices architecture with authentication, caching, and monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom timing middleware
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    
    # Add tracing
    with tracer.start_as_current_span(f"{request.method} {request.url.path}") as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        span.set_attribute("http.status_code", response.status_code)
        span.set_attribute("http.response_time", process_time)
        
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    
    return response

# Initialize monitoring
instrumentator = Instrumentator()
instrumentator.instrument(app)
instrumentator.expose(app)

# Instrument with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return user info using gRPC Auth Service"""
    try:
        token = credentials.credentials
        
        if GRPC_AVAILABLE:
            # Use gRPC Auth Service to validate token
            async with AuthServiceClient() as auth_service:
                result = await auth_service.validate_token(token)
                
                if not result.get("valid", False):
                    raise HTTPException(status_code=401, detail=result.get("message", "Invalid token"))
                
                return result.get("user", {})
        else:
            # Fallback to Redis cache for token validation
            if redis_client:
                cached_user = redis_client.get(f"token:{token}")
                if cached_user:
                    return {"user_id": "cached_user", "token": token}
            
            # Mock user validation
            return {"user_id": "test_user", "token": token}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with service status"""
    services = {
        "redis": "connected" if redis_client else "disconnected",
        "database": "unknown",  # Would check DB connection in real app
        "grpc_auth_service": "available" if GRPC_AVAILABLE else "unavailable"
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        services=services
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "FastAPI Microservices Architecture", "version": "1.0.0"}

@app.post("/auth/register")
async def register_user(user: UserRegistration):
    """User registration endpoint using gRPC Auth Service"""
    try:
        logger.info(f"Registering user with phone: {user.phone}")
        
        if GRPC_AVAILABLE:
            # Use gRPC Auth Service for user registration
            async with AuthServiceClient() as auth_service:
                result = await auth_service.register_user(
                    phone=user.phone,
                    email=user.email,
                    password=user.password,
                    full_name=user.full_name,
                    country_code=user.country_code
                )
                
                if not result.get("success", False):
                    raise HTTPException(status_code=400, detail=result.get("message", "Registration failed"))
                
                return {
                    "message": result.get("message", "User registered successfully"),
                    "user": result.get("user", {}),
                    "service": "gRPC Auth Service"
                }
        else:
            # Fallback to Redis-based registration
            if redis_client:
                user_data = {
                    "phone": user.phone,
                    "email": user.email,
                    "full_name": user.full_name,
                    "created_at": time.time()
                }
                redis_client.setex(f"user:{user.phone}", 3600, str(user_data))
            
            return {
                "message": "User registered successfully (fallback)",
                "phone": user.phone,
                "service": "Redis fallback"
            }
    
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(username: str = Form(...), password: str = Form(...)):
    """User login endpoint using gRPC Auth Service (OAuth2 compatible)"""
    try:
        logger.info(f"Login attempt for phone: {username}")
        
        if GRPC_AVAILABLE:
            # Use gRPC Auth Service for authentication
            async with AuthServiceClient() as auth_service:
                result = await auth_service.authenticate_user(username, password)
                
                if not result.get("success", False):
                    raise HTTPException(
                        status_code=401, 
                        detail=result.get("message", "Invalid credentials")
                    )
                
                return TokenResponse(
                    access_token=result.get("access_token", ""),
                    refresh_token=result.get("refresh_token"),
                    expires_in=result.get("expires_in", 1800)
                )
        else:
            # Fallback authentication
            mock_token = f"jwt_token_{username}_{int(time.time())}"
            
            # Cache the token
            if redis_client:
                redis_client.setex(f"token:{mock_token}", 1800, username)  # 30 min expiry
            
            return TokenResponse(
                access_token=mock_token,
                expires_in=1800
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/users/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile (protected endpoint)"""
    logger.info(f"Fetching profile for user: {current_user.get('user_id', 'unknown')}")
    
    # Return the user data from gRPC or fallback
    return {
        "user_id": current_user.get("user_id", "unknown"),
        "phone": current_user.get("phone", ""),
        "email": current_user.get("email", ""),
        "full_name": current_user.get("full_name", ""),
        "is_active": current_user.get("is_active", True),
        "is_verified": current_user.get("is_verified", False),
        "service": "gRPC Auth Service" if GRPC_AVAILABLE else "Fallback"
    }

@app.post("/auth/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """User logout endpoint"""
    try:
        user_id = current_user.get("user_id")
        token = current_user.get("token", "")
        
        if GRPC_AVAILABLE and user_id:
            # Use gRPC Auth Service for logout
            async with AuthServiceClient() as auth_service:
                result = await auth_service.logout_user(token, user_id)
                
                return {
                    "message": result.get("message", "Logout successful"),
                    "service": "gRPC Auth Service"
                }
        else:
            # Fallback logout - remove from Redis cache
            if redis_client and token:
                redis_client.delete(f"token:{token}")
            
            return {
                "message": "Logout successful",
                "service": "Redis fallback"
            }
    
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str = Form(...)):
    """Refresh access token using refresh token"""
    try:
        if GRPC_AVAILABLE:
            # Use gRPC Auth Service for token refresh
            async with AuthServiceClient() as auth_service:
                result = await auth_service.refresh_token(refresh_token)
                
                if not result.get("success", False):
                    raise HTTPException(status_code=401, detail=result.get("message", "Invalid refresh token"))
                
                return TokenResponse(
                    access_token=result.get("access_token", ""),
                    refresh_token=result.get("refresh_token"),
                    expires_in=result.get("expires_in", 1800)
                )
        else:
            raise HTTPException(status_code=501, detail="Token refresh not available in fallback mode")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=401, detail="Token refresh failed")

@app.get("/debug/{item_id}")
async def debug_endpoint(item_id: int):
    """Debug endpoint to demonstrate debugging techniques"""
    logger.info(f"Debug endpoint called with item_id: {item_id}")
    print(f"Debugging Value: {item_id}")  # Print statement for debugging
    
    # Demonstrate breakpoint (uncomment for debugging)
    # breakpoint()
    
    # Simulate some processing
    result = {"item_id": item_id, "processed": True}
    
    if item_id < 0:
        logger.warning(f"Negative item_id received: {item_id}")
        raise HTTPException(status_code=400, detail="Item ID must be positive")
    
    return result

@app.get("/performance/heavy")
async def heavy_operation():
    """Simulate heavy operation for performance testing"""
    start_time = time.perf_counter()
    
    # Simulate heavy computation
    total = sum(i * i for i in range(10000))
    
    processing_time = time.perf_counter() - start_time
    
    return {
        "result": total,
        "processing_time": processing_time,
        "status": "completed"
    }

@app.get("/cache/test/{key}")
async def test_cache(key: str, value: Optional[str] = None):
    """Test Redis caching functionality"""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    try:
        if value:
            # Set value in cache
            redis_client.setex(key, 300, value)  # 5 minutes expiry
            return {"message": f"Cached {key} = {value}"}
        else:
            # Get value from cache
            cached_value = redis_client.get(key)
            if cached_value:
                return {"key": key, "value": cached_value, "source": "cache"}
            else:
                return {"key": key, "value": None, "source": "not_found"}
    
    except Exception as e:
        logger.error(f"Cache operation failed: {e}")
        raise HTTPException(status_code=500, detail="Cache operation failed")

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug,
        log_level="info"
    )
