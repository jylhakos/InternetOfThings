from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
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

# Weather service instance
weather_service = WeatherService()

# In-memory store for active connections (in production, use Redis)
active_connections = {}

@app.on_event("startup")
async def startup_event():
    """Initialize database and start weather streaming"""
    await init_db()
    # Start weather streaming task
    asyncio.create_task(weather_streaming_task())

@app.post("/api/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    try:
        user = await create_user(db, user_data)
        access_token_expires = timedelta(days=1)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/login")
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user"""
    user = await authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=1)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone
        }
    }

@app.get("/api/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone
    }

@app.get("/api/weather")
async def get_weather():
    """Get current weather data for Schiphol Airport"""
    try:
        weather_data = await weather_service.get_schiphol_weather()
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    print(f"Client {sid} connected")
    active_connections[sid] = datetime.now()
    # Send initial weather data
    try:
        weather_data = await weather_service.get_schiphol_weather()
        await sio.emit('weather_update', weather_data, room=sid)
    except Exception as e:
        print(f"Error sending initial weather data: {e}")

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client {sid} disconnected")
    if sid in active_connections:
        del active_connections[sid]

@sio.event
async def request_weather(sid):
    """Handle manual weather data request"""
    try:
        weather_data = await weather_service.get_schiphol_weather()
        await sio.emit('weather_update', weather_data, room=sid)
    except Exception as e:
        await sio.emit('weather_error', {'error': str(e)}, room=sid)

async def weather_streaming_task():
    """Background task to stream weather data every hour"""
    while True:
        try:
            # Wait for 1 hour (3600 seconds) - for testing, use 60 seconds
            await asyncio.sleep(60)  # Change to 3600 for production
            
            if active_connections:
                weather_data = await weather_service.get_schiphol_weather()
                # Broadcast to all connected clients
                await sio.emit('weather_update', weather_data)
                print(f"Weather data broadcasted to {len(active_connections)} clients")
        except Exception as e:
            print(f"Error in weather streaming task: {e}")
            await asyncio.sleep(30)  # Wait 30 seconds before retrying

@app.get("/")
async def root():
    return {"message": "Weather Streaming API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )