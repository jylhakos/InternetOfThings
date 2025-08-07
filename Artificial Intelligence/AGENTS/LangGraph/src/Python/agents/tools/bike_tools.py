from langchain_core.tools import BaseTool
from typing import Dict, Any, List, Optional
import json
import asyncio
from services.citybikes_service import CityBikesService
from services.gbfs_service import GBFSService
from utils.config import Config
from utils.logger import logger

class FindBikeStationsTool(BaseTool):
    name = "find_bike_stations"
    description = """
    Find available bike stations in a European city.
    
    Input should be a JSON string with:
    - city: City name (e.g., "Amsterdam", "Paris", "Berlin")
    - location (optional): Specific location/landmark
    - max_distance_km (optional): Maximum distance from location (default: 5km)
    
    Returns information about available bike stations including location, 
    available bikes, and distance from requested location.
    """
    
    def __init__(self):
        super().__init__()
        self.citybikes_service = CityBikesService()
        self.gbfs_service = GBFSService()
    
    def _run(self, query: str) -> str:
        """Find bike stations synchronously"""
        try:
            # Parse input
            params = json.loads(query)
            city = params.get("city", "").lower()
            location = params.get("location")
            max_distance = params.get("max_distance_km", 5.0)
            
            # Run async function
            result = asyncio.run(self._find_stations_async(city, location, max_distance))
            return json.dumps(result, indent=2)
            
        except json.JSONDecodeError:
            return json.dumps({
                "error": "Invalid JSON input",
                "expected_format": {
                    "city": "Amsterdam",
                    "location": "Central Station",
                    "max_distance_km": 5.0
                }
            })
        except Exception as e:
            logger.error(f"Error in find_bike_stations: {e}")
            return json.dumps({"error": str(e)})
    
    async def _find_stations_async(
        self, 
        city: str, 
        location: Optional[str], 
        max_distance: float
    ) -> Dict[str, Any]:
        """Async implementation of station finding"""
        
        # Get city configuration
        city_config = Config.SUPPORTED_CITIES.get(city)
        if not city_config:
            return {
                "error": f"City '{city}' not supported",
                "supported_cities": list(Config.SUPPORTED_CITIES.keys())
            }
        
        stations = []
        
        # Try GBFS API first if available
        gbfs_url = city_config.get("gbfs_url")
        if gbfs_url:
            try:
                gbfs_stations = await self.gbfs_service.get_combined_station_data(gbfs_url)
                stations.extend(self._format_gbfs_stations(gbfs_stations))
            except Exception as e:
                logger.warning(f"GBFS failed for {city}: {e}")
        
        # Fallback to CityBikes API
        if not stations:
            try:
                citybike_stations = await self.citybikes_service.get_stations_for_city(city)
                stations.extend(self._format_citybike_stations(citybike_stations))
            except Exception as e:
                logger.warning(f"CityBikes failed for {city}: {e}")
        
        # Filter by location if specified
        if location and stations:
            # For simplicity, filter by name matching
            filtered_stations = []
            location_lower = location.lower()
            
            for station in stations:
                station_name = station.get("name", "").lower()
                if location_lower in station_name:
                    filtered_stations.append(station)
            
            if filtered_stations:
                stations = filtered_stations
        
        return {
            "city": city.title(),
            "location": location,
            "total_stations": len(stations),
            "stations": stations[:10]  # Limit to top 10 results
        }
    
    def _format_gbfs_stations(self, gbfs_stations: List[Dict]) -> List[Dict]:
        """Format GBFS station data"""
        formatted = []
        for station in gbfs_stations:
            formatted.append({
                "id": station.get("station_id", "unknown"),
                "name": station.get("name", "Unnamed Station"),
                "latitude": station.get("lat", 0),
                "longitude": station.get("lon", 0),
                "available_bikes": station.get("available_bikes", 0),
                "available_docks": station.get("available_docks", 0),
                "total_capacity": station.get("capacity", 0),
                "is_active": station.get("is_renting", True),
                "bike_types": ["regular"]  # Default, could be enhanced
            })
        return formatted
    
    def _format_citybike_stations(self, citybike_stations: List[Dict]) -> List[Dict]:
        """Format CityBikes station data"""
        formatted = []
        for station in citybike_stations:
            formatted.append({
                "id": station.get("id", "unknown"),
                "name": station.get("name", "Unnamed Station"),
                "latitude": station.get("latitude", 0),
                "longitude": station.get("longitude", 0),
                "available_bikes": station.get("free_bikes", 0),
                "available_docks": station.get("empty_slots", 0),
                "total_capacity": station.get("free_bikes", 0) + station.get("empty_slots", 0),
                "is_active": True,
                "bike_types": ["regular"]
            })
        return formatted


class CheckBikeAvailabilityTool(BaseTool):
    name = "check_bike_availability"
    description = """
    Check real-time bike availability at specific stations.
    
    Input should be a JSON string with:
    - station_ids: List of station IDs to check
    - city: City name for context
    
    Returns current availability status for each station.
    """
    
    def _run(self, query: str) -> str:
        try:
            params = json.loads(query)
            station_ids = params.get("station_ids", [])
            city = params.get("city", "")
            
            # For demo purposes, return mock availability data
            # In production, this would check real APIs
            availability = []
            for station_id in station_ids:
                availability.append({
                    "station_id": station_id,
                    "available_bikes": 5,
                    "available_docks": 3,
                    "status": "active",
                    "last_updated": "2025-01-07T12:00:00Z"
                })
            
            return json.dumps({
                "city": city,
                "availability": availability,
                "timestamp": "2025-01-07T12:00:00Z"
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


class CalculateRentalCostTool(BaseTool):
    name = "calculate_rental_cost"
    description = """
    Calculate the cost of bike rental based on duration and city.
    
    Input should be a JSON string with:
    - city: City name
    - hours: Rental duration in hours
    - bike_type (optional): Type of bike ("regular" or "electric")
    
    Returns estimated rental cost in local currency.
    """
    
    def _run(self, query: str) -> str:
        try:
            params = json.loads(query)
            city = params.get("city", "").lower()
            hours = params.get("hours", 1)
            bike_type = params.get("bike_type", "regular")
            
            # Pricing structure for European cities (simplified)
            pricing = {
                "amsterdam": {"base": 3.0, "hourly": 2.0, "currency": "EUR"},
                "paris": {"base": 2.5, "hourly": 1.8, "currency": "EUR"},
                "berlin": {"base": 2.0, "hourly": 1.5, "currency": "EUR"},
                "london": {"base": 2.0, "hourly": 2.0, "currency": "GBP"},
                "barcelona": {"base": 2.5, "hourly": 1.5, "currency": "EUR"},
                "madrid": {"base": 2.0, "hourly": 1.2, "currency": "EUR"}
            }
            
            city_pricing = pricing.get(city, {"base": 2.5, "hourly": 1.5, "currency": "EUR"})
            
            # Calculate cost
            base_cost = city_pricing["base"]
            hourly_rate = city_pricing["hourly"]
            
            # Electric bikes cost more
            if bike_type == "electric":
                base_cost *= 1.5
                hourly_rate *= 1.5
            
            total_cost = base_cost + (max(0, hours - 1) * hourly_rate)
            
            return json.dumps({
                "city": city.title(),
                "duration_hours": hours,
                "bike_type": bike_type,
                "base_cost": round(base_cost, 2),
                "hourly_rate": round(hourly_rate, 2),
                "total_cost": round(total_cost, 2),
                "currency": city_pricing["currency"],
                "breakdown": {
                    "first_hour": round(base_cost, 2),
                    "additional_hours": max(0, hours - 1),
                    "additional_cost": round(max(0, hours - 1) * hourly_rate, 2)
                }
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})

# Tool instances
find_stations_tool = FindBikeStationsTool()
check_availability_tool = CheckBikeAvailabilityTool()
calculate_cost_tool = CalculateRentalCostTool()
