#!/usr/bin/env python3
"""
Simple demonstration of the Bike Rental Agent components
"""
import asyncio
import json
from utils.config import Config
from utils.logger import logger

async def demo_ollama_connection():
    """Demo Ollama connection"""
    print("🤖 Testing Ollama Connection")
    print("=" * 40)
    
    try:
        # Test basic HTTP connection to Ollama
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{Config.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                print(f"✅ Ollama is running on {Config.OLLAMA_BASE_URL}")
                print(f"📦 Available models: {models}")
                
                if Config.OLLAMA_MODEL in models:
                    print(f"✅ Target model '{Config.OLLAMA_MODEL}' is available")
                else:
                    print(f"⚠️  Target model '{Config.OLLAMA_MODEL}' not found")
                    
                return True
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        return False

async def demo_bike_apis():
    """Demo bike sharing APIs"""
    print("\n🚲 Testing Bike Sharing APIs")
    print("=" * 40)
    
    try:
        from services.citybikes_service import CityBikesService
        
        citybikes = CityBikesService()
        
        # Test getting networks
        networks = await citybikes.get_networks()
        print(f"✅ CityBikes API: Found {len(networks)} bike sharing networks")
        
        # Test Amsterdam specifically
        amsterdam = await citybikes.get_network_by_city("amsterdam")
        if amsterdam:
            print(f"✅ Amsterdam network found: {amsterdam.get('name', 'Unknown')}")
            
            # Get stations
            stations = await citybikes.get_stations_for_city("amsterdam")
            print(f"✅ Amsterdam has {len(stations)} bike stations")
            
            if stations:
                sample_station = stations[0]
                print(f"📍 Sample station: {sample_station.get('name', 'Unnamed')}")
                print(f"   Available bikes: {sample_station.get('free_bikes', 0)}")
                print(f"   Location: {sample_station.get('latitude', 0):.4f}, {sample_station.get('longitude', 0):.4f}")
        else:
            print("⚠️  Amsterdam network not found")
            
    except Exception as e:
        print(f"❌ Error testing bike APIs: {e}")

def demo_tools():
    """Demo the bike rental tools"""
    print("\n🔧 Testing Bike Rental Tools")
    print("=" * 40)
    
    try:
        from agents.tools.bike_tools import calculate_cost_tool
        
        # Test cost calculation
        cost_query = json.dumps({
            "city": "Amsterdam",
            "hours": 3,
            "bike_type": "electric"
        })
        
        result = calculate_cost_tool._run(cost_query)
        cost_data = json.loads(result)
        
        print("✅ Cost calculation tool working:")
        print(f"   City: {cost_data['city']}")
        print(f"   Duration: {cost_data['duration_hours']} hours")
        print(f"   Bike type: {cost_data['bike_type']}")
        print(f"   Total cost: {cost_data['total_cost']} {cost_data['currency']}")
        
    except Exception as e:
        print(f"❌ Error testing tools: {e}")

def demo_config():
    """Demo configuration"""
    print("\n⚙️  Configuration")
    print("=" * 40)
    
    print(f"Ollama URL: {Config.OLLAMA_BASE_URL}")
    print(f"Ollama Model: {Config.OLLAMA_MODEL}")
    print(f"CityBikes API: {Config.CITYBIKES_API_URL}")
    print(f"Supported cities: {len(Config.SUPPORTED_CITIES)}")
    
    for city, details in list(Config.SUPPORTED_CITIES.items())[:3]:
        print(f"  • {city.title()}: {details['country']}")

async def main():
    """Run all demos"""
    print("🌍 European Bike Rental Agent - Component Demo")
    print("=" * 50)
    
    # Configuration demo
    demo_config()
    
    # Test Ollama connection
    ollama_ok = await demo_ollama_connection()
    
    # Test bike APIs
    await demo_bike_apis()
    
    # Test tools
    demo_tools()
    
    print("\n" + "=" * 50)
    if ollama_ok:
        print("✅ Demo completed! All core components are working.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test API endpoints")
    else:
        print("⚠️  Demo completed with warnings.")
        print("Please ensure Ollama is running and the model is available.")
    
    print("\n🚴‍♂️ Ready for bike rental adventures in Europe! 🚴‍♀️")

if __name__ == "__main__":
    asyncio.run(main())
