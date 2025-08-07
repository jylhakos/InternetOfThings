from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

# Import models
from models.requests import BikeSearchRequest, BikeRentalRequest, ChatRequest, LocationRequest
from models.responses import (
    BikeSearchResponse, BikeRentalResponse, ChatResponse, 
    ErrorResponse, BikeStation, RentalStatus
)

# Import services
from services.ollama_service import OllamaService
from services.citybikes_service import CityBikesService
from services.gbfs_service import GBFSService

# Import agent (will be imported after dependencies are installed)
# from agents.bike_agent import bike_agent

from utils.config import Config
from utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Bike Rental Agent API...")
    
    # Check Ollama connection
    ollama_service = OllamaService()
    if not await ollama_service.check_connection():
        logger.warning("Ollama service is not available. Please ensure Ollama is running.")
    else:
        logger.info("Connected to Ollama service successfully")
        
        # List available models
        models = await ollama_service.list_models()
        logger.info(f"Available Ollama models: {models}")
        
        if Config.OLLAMA_MODEL not in models:
            logger.warning(f"Model {Config.OLLAMA_MODEL} not found. You may need to pull it.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bike Rental Agent API...")

app = FastAPI(
    title="European Bike Rental Agent",
    description="AI-powered bike rental service for European cities using LangGraph and Ollama",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "European Bike Rental Agent API",
        "version": "1.0.0",
        "documentation": "/docs",
        "supported_cities": list(Config.SUPPORTED_CITIES.keys()),
        "ollama_model": Config.OLLAMA_MODEL
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_service = OllamaService()
    ollama_connected = await ollama_service.check_connection()
    
    return {
        "status": "healthy" if ollama_connected else "degraded",
        "ollama_connected": ollama_connected,
        "ollama_url": Config.OLLAMA_BASE_URL,
        "model": Config.OLLAMA_MODEL
    }

@app.post("/api/find-bikes", response_model=BikeSearchResponse)
async def find_bikes(request: BikeSearchRequest):
    """Find available bike stations in a city"""
    try:
        citybikes_service = CityBikesService()
        
        # Get stations for the city
        stations = await citybikes_service.get_stations_for_city(request.city.lower())
        
        # Convert to response format
        bike_stations = []
        for station in stations[:20]:  # Limit results
            bike_station = BikeStation(
                id=str(station.get("id", "unknown")),
                name=station.get("name", "Unnamed Station"),
                latitude=station.get("latitude", 0),
                longitude=station.get("longitude", 0),
                available_bikes=station.get("free_bikes", 0),
                available_docks=station.get("empty_slots", 0),
                total_capacity=station.get("free_bikes", 0) + station.get("empty_slots", 0),
                bike_types=["regular"]
            )
            bike_stations.append(bike_station)
        
        return BikeSearchResponse(
            success=True,
            message=f"Found {len(bike_stations)} bike stations in {request.city}",
            stations=bike_stations,
            total_found=len(bike_stations)
        )
        
    except Exception as e:
        logger.error(f"Error finding bikes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rent-bike", response_model=BikeRentalResponse)
async def rent_bike(request: BikeRentalRequest):
    """Simulate bike rental (demo implementation)"""
    try:
        from datetime import datetime
        import uuid
        
        # Create mock rental
        rental = RentalStatus(
            rental_id=str(uuid.uuid4()),
            status="active",
            start_time=datetime.now(),
            station_start=BikeStation(
                id=request.station_id,
                name="Demo Station",
                latitude=52.3676, longitude=4.9041,  # Amsterdam coordinates
                available_bikes=5, available_docks=3,
                total_capacity=8
            ),
            cost=request.duration_hours * 2.5,
            currency="EUR"
        )
        
        return BikeRentalResponse(
            success=True,
            message=f"Bike rented successfully for {request.duration_hours} hours",
            rental=rental
        )
        
    except Exception as e:
        logger.error(f"Error renting bike: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with the bike rental AI agent"""
    try:
        # For now, provide a mock response until LangGraph dependencies are installed
        # In production, this would use: bike_agent.process_request_sync(request.message, request.context)
        
        # Mock intelligent response based on message content
        message_lower = request.message.lower()
        
        if any(city in message_lower for city in ["amsterdam", "paris", "berlin", "london"]):
            response = "I can help you find bike rental stations! I support bike rentals in Amsterdam, Paris, Berlin, London, and other European cities. Would you like me to find available bikes near a specific location?"
            
        elif "cost" in message_lower or "price" in message_lower:
            response = "Bike rental costs vary by city. Typically, you'll pay around €2-3 for the first hour and €1.5-2 for each additional hour. Electric bikes cost about 50% more. Would you like me to calculate the exact cost for a specific duration and city?"
            
        elif "station" in message_lower or "location" in message_lower:
            response = "I can help you find bike stations! Please tell me which city you're interested in and optionally a specific area or landmark, and I'll show you nearby stations with availability."
            
        else:
            response = f"Hello! I'm your European bike rental assistant. I can help you find bikes, check availability, calculate costs, and provide information about bike sharing in cities like Amsterdam, Paris, Berlin, and more. What would you like to know about bike rental?"
        
        return ChatResponse(
            success=True,
            message="Chat response generated",
            agent_response=response,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cities")
async def get_supported_cities():
    """Get list of supported cities"""
    return {
        "supported_cities": Config.SUPPORTED_CITIES,
        "total_cities": len(Config.SUPPORTED_CITIES)
    }

@app.get("/api/models")
async def get_available_models():
    """Get available Ollama models"""
    try:
        ollama_service = OllamaService()
        models = await ollama_service.list_models()
        return {
            "available_models": models,
            "current_model": Config.OLLAMA_MODEL,
            "total_models": len(models)
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/geocode")
async def geocode_location(request: LocationRequest):
    """Geocode an address or location"""
    try:
        # Mock geocoding response
        # In production, this would use the geocoding tool
        
        # Sample coordinates for major cities
        city_coords = {
            "amsterdam": {"lat": 52.3676, "lon": 4.9041},
            "paris": {"lat": 48.8566, "lon": 2.3522},
            "berlin": {"lat": 52.5200, "lon": 13.4050},
            "london": {"lat": 51.5074, "lon": -0.1278},
        }
        
        city_lower = request.city.lower()
        coords = city_coords.get(city_lower, {"lat": 0, "lon": 0})
        
        return {
            "success": True,
            "city": request.city,
            "address": request.address,
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "formatted_address": f"{request.address or ''}, {request.city}".strip(", ")
        }
        
    except Exception as e:
        logger.error(f"Error geocoding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )
