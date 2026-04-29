#!/usr/bin/env python3
"""
Simple FastAPI server to demonstrate the Bike Rental Agent
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="European Bike Rental Agent",
    description="AI-powered bike rental service for European cities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# European cities data
CITIES = {
    "amsterdam": {
        "country": "Netherlands",
        "sample_stations": [
            {"id": "001", "name": "Central Station", "bikes": 12, "docks": 8},
            {"id": "002", "name": "Dam Square", "bikes": 5, "docks": 15},
            {"id": "003", "name": "Vondelpark", "bikes": 8, "docks": 12}
        ]
    },
    "paris": {
        "country": "France",
        "sample_stations": [
            {"id": "101", "name": "Eiffel Tower", "bikes": 15, "docks": 5},
            {"id": "102", "name": "Louvre Museum", "bikes": 7, "docks": 13},
            {"id": "103", "name": "Notre Dame", "bikes": 10, "docks": 10}
        ]
    },
    "berlin": {
        "country": "Germany", 
        "sample_stations": [
            {"id": "201", "name": "Brandenburg Gate", "bikes": 9, "docks": 11},
            {"id": "202", "name": "Alexanderplatz", "bikes": 13, "docks": 7},
            {"id": "203", "name": "Potsdamer Platz", "bikes": 6, "docks": 14}
        ]
    }
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚲 European Bike Rental Agent API",
        "version": "1.0.0",
        "features": [
            "AI-powered bike finding",
            "Real-time availability",
            "Multi-city support",
            "LangGraph agent integration",
            "Ollama local LLM"
        ],
        "supported_cities": list(CITIES.keys()),
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cities_available": len(CITIES),
        "ollama_model": "arcee-agent:latest"
    }

@app.post("/api/chat")
async def chat_with_agent(request: dict):
    """Chat with the bike rental AI agent"""
    message = request.get("message", "").lower()
    
    # Simple rule-based responses to demonstrate functionality
    if any(city in message for city in CITIES.keys()):
        city = next(city for city in CITIES.keys() if city in message)
        stations = CITIES[city]["sample_stations"]
        
        response = f"""I can help you find bikes in {city.title()}! Here are some available stations:

🚲 **Available Bike Stations in {city.title()}:**
"""
        for station in stations:
            response += f"\n• **{station['name']}**: {station['bikes']} bikes, {station['docks']} docks available"
        
        response += f"\n\n💡 Would you like me to help you rent a bike or get directions to any of these stations?"
        
    elif "cost" in message or "price" in message:
        response = """💰 **Bike Rental Pricing:**

• **Regular bikes**: €2.50 first hour, €1.50 each additional hour
• **Electric bikes**: €3.50 first hour, €2.25 each additional hour

**Example costs:**
- 2 hours regular: €4.00
- 2 hours electric: €5.75
- Full day (8 hours): €13.00 regular, €19.25 electric

Would you like me to calculate the exact cost for your rental duration?"""

    elif "help" in message or "how" in message:
        response = """🚴‍♂️ **I can help you with:**

1. **Find bikes** - Search for available bikes in Amsterdam, Paris, or Berlin
2. **Check availability** - Real-time bike and dock availability
3. **Calculate costs** - Get rental pricing for any duration
4. **Get directions** - Find routes to bike stations
5. **Rent bikes** - Complete the rental process

Just tell me what city you're interested in and what you'd like to do!"""

    else:
        response = """Hello! I'm your European bike rental assistant. 🚲

I can help you rent bikes in **Amsterdam**, **Paris**, and **Berlin**!

Try asking me:
- "I want to rent a bike in Amsterdam"
- "Show me bike stations in Paris"
- "How much does it cost to rent a bike for 3 hours?"
- "Find bikes near the Eiffel Tower"

What would you like to know?"""

    return {
        "success": True,
        "message": "Chat response generated",
        "agent_response": response,
        "session_id": request.get("session_id"),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/find-bikes")
async def find_bikes(request: dict):
    """Find bike stations in a city"""
    city = request.get("city", "").lower()
    
    if city not in CITIES:
        return {
            "success": False,
            "message": f"City '{city}' not supported",
            "supported_cities": list(CITIES.keys())
        }
    
    stations = CITIES[city]["sample_stations"]
    
    return {
        "success": True,
        "message": f"Found {len(stations)} bike stations in {city.title()}",
        "city": city.title(),
        "country": CITIES[city]["country"],
        "stations": stations,
        "total_bikes": sum(s["bikes"] for s in stations),
        "total_docks": sum(s["docks"] for s in stations)
    }

@app.post("/api/calculate-cost")
async def calculate_cost(request: dict):
    """Calculate bike rental cost"""
    hours = request.get("hours", 1)
    bike_type = request.get("bike_type", "regular").lower()
    city = request.get("city", "amsterdam").lower()
    
    # Pricing logic
    if bike_type == "electric":
        base_rate = 3.50
        hourly_rate = 2.25
    else:
        base_rate = 2.50
        hourly_rate = 1.50
    
    total_cost = base_rate + (max(0, hours - 1) * hourly_rate)
    
    return {
        "success": True,
        "city": city.title(),
        "duration_hours": hours,
        "bike_type": bike_type,
        "base_cost": base_rate,
        "hourly_rate": hourly_rate,
        "total_cost": round(total_cost, 2),
        "currency": "EUR",
        "breakdown": f"{base_rate}€ first hour + {max(0, hours-1)} × {hourly_rate}€ = {total_cost:.2f}€"
    }

@app.get("/api/cities")
async def get_cities():
    """Get supported cities"""
    return {
        "supported_cities": CITIES,
        "total_cities": len(CITIES)
    }

if __name__ == "__main__":
    print("🚲 Starting European Bike Rental Agent...")
    print("📍 Supported cities: Amsterdam, Paris, Berlin")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("💬 Chat endpoint: http://localhost:8000/api/chat")
    
    uvicorn.run(
        "simple_demo:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
