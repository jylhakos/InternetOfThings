from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import socketio
import asyncio
from datetime import datetime, timedelta
import uvicorn
import os
from dotenv import load_dotenv

from auth import authenticate_user, create_access_token, get_current_user, create_user
from database import init_db, get_db
from weather_service import WeatherService
from models import UserCreate, UserLogin, User

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Weather Streaming API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:5173", "http://localhost:3000"]
)

# Wrap FastAPI app with Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Security
security = HTTPBearer()

# Initialize weather service
weather_service = WeatherService()

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class WeatherData(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: int
    weather_condition: str
    location: str
    timestamp: datetime

# Store connected clients
connected_clients = set()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Weather Streaming API", "status": "running"}

@app.post("/auth/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = hash_password(user_data.password)
        user_dict = user_data.dict()
        user_dict['password'] = hashed_password
        
        user = await create_user(User(**user_dict))
        
        return {
            "message": "User registered successfully",
            "user_id": user.id
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login user and return JWT token"""
    try:
        # Get user by email
        user = await get_user_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = verify_token(credentials.credentials)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = await get_user_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.get("/user/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone
    }

@app.get("/weather/current")
async def get_current_weather(current_user: User = Depends(get_current_user)):
    """Get current weather data for Schiphol Airport"""
    try:
        weather_data = await weather_service.get_schiphol_weather()
        return weather_data
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch weather data"
        )

# Socket.IO event handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"Client {sid} connected")
    connected_clients.add(sid)
    
    # Send initial weather data
    try:
        weather_data = await weather_service.get_schiphol_weather()
        await sio.emit('weather_update', weather_data, room=sid)
    except Exception as e:
        logger.error(f"Error sending initial weather data: {e}")

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client {sid} disconnected")
    connected_clients.discard(sid)

@sio.event
async def refresh_weather(sid):
    """Handle weather refresh request"""
    logger.info(f"Weather refresh requested by {sid}")
    try:
        weather_data = await weather_service.get_schiphol_weather()
        await sio.emit('weather_update', weather_data, room=sid)
    except Exception as e:
        logger.error(f"Error refreshing weather data: {e}")
        await sio.emit('error', {'message': 'Failed to fetch weather data'}, room=sid)

async def weather_broadcaster():
    """Background task to broadcast weather updates every hour"""
    while True:
        try:
            await asyncio.sleep(3600)  # Wait 1 hour
            if connected_clients:
                logger.info("Broadcasting hourly weather update")
                weather_data = await weather_service.get_schiphol_weather()
                await sio.emit('weather_update', weather_data)
        except Exception as e:
            logger.error(f"Error in weather broadcaster: {e}")

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(weather_broadcaster())
    logger.info("Weather streaming service started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )