# Project: European Bike Rental Agent with LangGraph & Ollama

## What We Built?

An AI powered bike rental application for European cities.

- **LangGraph**: An agent workflow with calling a tool
- **Ollama**: Local LLM inference (using Arcee-Agent model)
- **🚲 Bike APIs**: CityBikes API + GBFS integration
- **FastAPI**: RESTful API with OpenAPI docs
- **Python**: An async architecture


**🚴‍♂️ Ready to ride a bike from rentals in European cities**

Start your bike rental adventure with AI assistance.

## 📁 Project Structure

```
European-Bike-Rental-Agent/
├── 📄 README.md              # Comprehensive documentation
├── 🔧 requirements.txt       # Python dependencies
├── ⚙️ .env                   # Configuration
├──  main.py                # Full FastAPI application
├── simple_demo.py         # Simple working demo
├── demo.py                # Component testing
├──
├── 🤖 agents/
│   ├── 🚲 bike_agent.py      # Main LangGraph agent
│   └── tools/
│       ├── bike_tools.py     # Bike rental tools
│       ├── location_tools.py # Geocoding & mapping tools
│       └── python_repl.py    # Enhanced Python REPL
├──
├── 🌐 services/
│   ├── ollama_service.py     # Ollama integration
│   ├── citybikes_service.py  # CityBikes API client
│   └── gbfs_service.py       # GBFS API client
├──
├── models/
│   ├── requests.py           # Pydantic request models
│   └── responses.py          # Pydantic response models
├──
├── ⚡ utils/
│   ├── config.py             # Configuration management
│   └── logger.py             # Logging utilities
├── 
└── 🛠️ Scripts/
    ├── setup.sh              # Complete setup script
    ├── test_api.sh           # API testing script
    ├── test_components.py    # Component tests
    └── quick_start.sh        # Quick start guide
```

## 🌍 Cities

- **Amsterdam**, Netherlands 🇳🇱
- **Paris**, France 🇫🇷  
- **Berlin**, Germany 🇩🇪
- **London**, United Kingdom 🇬🇧
- **Barcelona**, Spain 🇪🇸
- **Madrid**, Spain 🇪🇸
- Copenhagen, Vienna, and more cities

## Quick Start

```bash
# 1. Setup everything
./setup.sh

# 2. Activate environment
source venv/bin/activate

# 3. Start the API (simple demo)
python simple_demo.py

# 4. Start the full AI agent
python main.py

# 5. Test the API
./test_api.sh
```

## 🛠️ Key Features

### 🤖 AI Agent Capabilities
- Natural language bike rental assistance
- Multi-city support across Europe
- Real-time bike availability checking
- Cost calculation and pricing
- Route planning and directions
- Python code execution for complex calculations

### 🔧 Tool Calling Functions
1. **find_bike_stations** - Find available stations by city/location
2. **check_bike_availability** - Real-time availability status
3. **calculate_rental_cost** - Pricing for different durations
4. **geocode_location** - Address to coordinates conversion
5. **calculate_distance** - Haversine distance calculations
6. **find_nearby_locations** - POI discovery around stations
7. **python_repl** - Execute custom Python code

### 🌐 API Endpoints
- `GET /` - API information
- `GET /health` - Health check  
- `POST /api/chat` - Chat with AI agent
- `POST /api/find-bikes` - Search bike stations
- `POST /api/calculate-cost` - Calculate rental costs
- `POST /api/geocode` - Geocode addresses
- `GET /api/cities` - Supported cities
- `GET /docs` - Interactive API documentation

## API Integrations

- **CityBikes API**: Global bike sharing network data
- **GBFS**: General Bikeshare Feed Specification
- **OpenStreetMap**: Geocoding and mapping
- **Overpass API**: Points of interest discovery
- **Ollama**: Local LLM inference

## Usage

### Chat with Agent
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to rent an electric bike in Amsterdam near Central Station for 3 hours"
  }'
```

### Find Bikes
```bash
curl -X POST "http://localhost:8000/api/find-bikes" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Paris", 
    "location": "Eiffel Tower",
    "max_distance_km": 2.0
  }'
```

### Calculate Cost
```bash
curl -X POST "http://localhost:8000/api/calculate-cost" \
  -H "Content-Type: application/json" \
  -d '{
    "hours": 4,
    "bike_type": "electric",
    "city": "Berlin"
  }'
```

## Testing

```bash
# Test individual components
python test_components.py

# Test API endpoints
./test_api.sh

# Run comprehensive demo
python demo.py

# Simple working demo
python simple_demo.py
```

## Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **README.md**: Complete setup and usage guide
- **Inline Comments**: Extensive code documentation


## 🔧 Stack

- **Framework**: FastAPI + LangGraph
- **AI/LLM**: Ollama (Arcee-Agent, Llama-3.x)
- **APIs**: CityBikes, GBFS, OpenStreetMap
- **Language**: Python 3.9+
- **Architecture**: Async, microservices-ready
- **Documentation**: OpenAPI/Swagger

---
