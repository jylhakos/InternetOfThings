"""
The FastAPI application with best practices demonstrates RESTful API design with lifespan management
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uvicorn
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Pydantic Models ---
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: Optional[int] = Field(None, ge=0, le=150)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# --- Mock Database (In production, use real database) ---
class MockDatabase:
    def __init__(self):
        self.users = []
        self.connected = False
        self.next_id = 1
    
    async def connect(self):
        """Simulate database connection"""
        await asyncio.sleep(0.1)  # Simulate connection time
        self.connected = True
        logger.info("Database connected successfully")
    
    async def disconnect(self):
        """Simulate database disconnection"""
        await asyncio.sleep(0.1)  # Simulate disconnection time
        self.connected = False
        logger.info("Database disconnected successfully")
    
    def is_connected(self):
        return self.connected

# Global database instance
db = MockDatabase()

# --- Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup events
    logger.info("🚀 Starting FastAPI application...")
    await db.connect()
    
    # Initialize with sample data
    sample_users = [
        {"name": "John Doe", "email": "john@example.com", "age": 30},
        {"name": "Jane Smith", "email": "jane@example.com", "age": 25}
    ]
    
    for user_data in sample_users:
        user = User(
            id=db.next_id,
            created_at=datetime.now(),
            **user_data
        )
        db.users.append(user)
        db.next_id += 1
    
    logger.info(f"✅ Application startup complete. Loaded {len(db.users)} sample users.")
    
    yield  # Application runs here
    
    # Shutdown events
    logger.info("🛑 Shutting down FastAPI application...")
    await db.disconnect()
    logger.info("✅ Application shutdown complete.")

# --- FastAPI Application ---
app = FastAPI(
    title="FastAPI RESTful API Demo",
    description="A comprehensive example of FastAPI with proper lifespan management",
    version="2.0.0",
    lifespan=lifespan,  # THIS IS ESSENTIAL!
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# --- Dependencies ---
async def get_db():
    """Dependency to get database instance"""
    if not db.is_connected():
        raise HTTPException(
            status_code=503, 
            detail="Database not available"
        )
    return db

# --- API Routes ---

@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information"""
    return APIResponse(
        success=True,
        message="FastAPI RESTful API is running",
        data={
            "version": "2.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    )

@app.get("/health", response_model=APIResponse)
async def health_check(database: MockDatabase = Depends(get_db)):
    """Health check endpoint"""
    return APIResponse(
        success=True,
        message="Service is healthy",
        data={
            "database_connected": database.is_connected(),
            "timestamp": datetime.now().isoformat()
        }
    )

# --- User CRUD Operations ---

@app.get("/users", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    database: MockDatabase = Depends(get_db)
):
    """Get all users with pagination"""
    return database.users[skip:skip + limit]

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, database: MockDatabase = Depends(get_db)):
    """Get user by ID"""
    user = next((u for u in database.users if u.id == user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, database: MockDatabase = Depends(get_db)):
    """Create a new user"""
    # Check if email already exists
    if any(u.email == user_data.email for u in database.users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        id=database.next_id,
        name=user_data.name,
        email=user_data.email,
        age=user_data.age,
        created_at=datetime.now()
    )
    
    database.users.append(new_user)
    database.next_id += 1
    
    logger.info(f"Created new user: {new_user.name} ({new_user.email})")
    return new_user

@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int, 
    user_data: UserBase, 
    database: MockDatabase = Depends(get_db)
):
    """Update an existing user"""
    user = next((u for u in database.users if u.id == user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Update user data
    user.name = user_data.name
    user.email = user_data.email
    user.age = user_data.age
    
    logger.info(f"Updated user: {user.name} ({user.email})")
    return user

@app.delete("/users/{user_id}", response_model=APIResponse)
async def delete_user(user_id: int, database: MockDatabase = Depends(get_db)):
    """Delete a user"""
    user_index = next((i for i, u in enumerate(database.users) if u.id == user_id), None)
    if user_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    deleted_user = database.users.pop(user_index)
    logger.info(f"Deleted user: {deleted_user.name} ({deleted_user.email})")
    
    return APIResponse(
        success=True,
        message=f"User {deleted_user.name} deleted successfully"
    )

# --- Error Handlers ---

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

# --- Application Entry Point ---
if __name__ == "__main__":
    uvicorn.run(
        "example_fastapi_app:app",  # module:app
        host="0.0.0.0",
        port=8001,
        reload=True,
        workers=1,
        log_level="info",
        loop="asyncio"
    )
