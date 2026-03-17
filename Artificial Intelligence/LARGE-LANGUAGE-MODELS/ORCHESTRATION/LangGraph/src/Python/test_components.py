import asyncio
import json
from services.ollama_service import OllamaService
from services.citybikes_service import CityBikesService
from utils.logger import logger

async def test_ollama():
    """Test Ollama service connection"""
    print("🤖 Testing Ollama connection...")
    
    ollama_service = OllamaService()
    
    # Check connection
    connected = await ollama_service.check_connection()
    print(f"Connection status: {'✅ Connected' if connected else '❌ Not connected'}")
    
    if connected:
        # List models
        models = await ollama_service.list_models()
        print(f"Available models: {models}")
        
        # Test generation
        if models:
            response = await ollama_service.generate_response(
                "Hello! Can you help me rent a bike?",
                system_prompt="You are a helpful bike rental assistant."
            )
            print(f"Test response: {response[:100]}...")

async def test_citybikes():
    """Test CityBikes API"""
    print("\n🚲 Testing CityBikes API...")
    
    citybikes_service = CityBikesService()
    
    # Test getting networks
    networks = await citybikes_service.get_networks()
    print(f"Total networks found: {len(networks)}")
    
    # Test finding Amsterdam network
    amsterdam_network = await citybikes_service.get_network_by_city("Amsterdam")
    if amsterdam_network:
        print(f"Amsterdam network: {amsterdam_network.get('name', 'Unknown')}")
        
        # Get stations
        stations = await citybikes_service.get_stations_for_city("Amsterdam")
        print(f"Amsterdam stations: {len(stations)}")
        
        if stations:
            first_station = stations[0]
            print(f"First station: {first_station.get('name', 'Unknown')} - {first_station.get('free_bikes', 0)} bikes available")

async def test_tools():
    """Test individual tools"""
    print("\n🔧 Testing tools...")
    
    # Test the bike tools
    from agents.tools.bike_tools import find_stations_tool, calculate_cost_tool
    
    # Test find stations
    station_query = json.dumps({
        "city": "Amsterdam",
        "max_distance_km": 5.0
    })
    
    try:
        station_result = find_stations_tool._run(station_query)
        print("Station search result:", station_result[:200] + "...")
    except Exception as e:
        print(f"Station search error: {e}")
    
    # Test cost calculation
    cost_query = json.dumps({
        "city": "Amsterdam",
        "hours": 3,
        "bike_type": "electric"
    })
    
    try:
        cost_result = calculate_cost_tool._run(cost_query)
        print("Cost calculation result:", cost_result)
    except Exception as e:
        print(f"Cost calculation error: {e}")

async def main():
    """Run all tests"""
    print("🧪 Starting component tests...\n")
    
    try:
        await test_ollama()
        await test_citybikes()
        await test_tools()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
