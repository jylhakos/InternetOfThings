from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from contextlib import asynccontextmanager

from app.database import database, engine, Base
from app.routers import users

# Create database tables
Base.metadata.create_all(bind=engine)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await database.connect()
    print("Database connected")
    yield
    # Shutdown
    await database.disconnect()
    print("Database disconnected")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="FastAPI PostgreSQL Demo",
    description="A FastAPI application with PostgreSQL and async support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "FastAPI with PostgreSQL",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # For development only
        workers=1,    # For development; increase for production
        loop="asyncio"
    )