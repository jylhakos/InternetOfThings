from langchain_core.tools import BaseTool
from typing import Dict, Any, Optional, Tuple
import json
import math
import httpx
import asyncio
from utils.logger import logger

class GeocodeLocationTool(BaseTool):
    name = "geocode_location"
    description = """
    Convert address or location name to coordinates (latitude, longitude).
    
    Input should be a JSON string with:
    - address: Full address or landmark name
    - city: City name for context
    
    Returns latitude and longitude coordinates.
    """
    
    def _run(self, query: str) -> str:
        try:
            params = json.loads(query)
            address = params.get("address", "")
            city = params.get("city", "")
            
            # Use Nominatim (OpenStreetMap) for geocoding
            result = asyncio.run(self._geocode_async(address, city))
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _geocode_async(self, address: str, city: str) -> Dict[str, Any]:
        """Async geocoding using Nominatim"""
        try:
            query_string = f"{address}, {city}" if city else address
            url = "https://nominatim.openstreetmap.org/search"
            
            params = {
                "q": query_string,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            
            headers = {
                "User-Agent": "BikeRentalAgent/1.0"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        location = data[0]
                        return {
                            "success": True,
                            "address": address,
                            "city": city,
                            "latitude": float(location.get("lat", 0)),
                            "longitude": float(location.get("lon", 0)),
                            "display_name": location.get("display_name", ""),
                            "formatted_address": location.get("display_name", "")
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Location not found",
                            "address": address,
                            "city": city
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Geocoding API error: {response.status_code}",
                        "address": address,
                        "city": city
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address,
                "city": city
            }


class CalculateDistanceTool(BaseTool):
    name = "calculate_distance"
    description = """
    Calculate distance between two locations using coordinates.
    
    Input should be a JSON string with:
    - lat1, lon1: First location coordinates
    - lat2, lon2: Second location coordinates
    - unit (optional): "km" or "miles" (default: "km")
    
    Returns distance between the two points.
    """
    
    def _run(self, query: str) -> str:
        try:
            params = json.loads(query)
            lat1 = params.get("lat1", 0)
            lon1 = params.get("lon1", 0)
            lat2 = params.get("lat2", 0)
            lon2 = params.get("lon2", 0)
            unit = params.get("unit", "km")
            
            distance_km = self._haversine_distance(lat1, lon1, lat2, lon2)
            
            if unit.lower() == "miles":
                distance = distance_km * 0.621371
                unit_label = "miles"
            else:
                distance = distance_km
                unit_label = "km"
            
            return json.dumps({
                "distance": round(distance, 2),
                "unit": unit_label,
                "coordinates": {
                    "from": {"lat": lat1, "lon": lon1},
                    "to": {"lat": lat2, "lon": lon2}
                }
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


class FindNearbyLocationsTool(BaseTool):
    name = "find_nearby_locations"
    description = """
    Find nearby points of interest around a given location.
    
    Input should be a JSON string with:
    - latitude: Latitude coordinate
    - longitude: Longitude coordinate  
    - radius_km: Search radius in kilometers (default: 1)
    - poi_type: Type of POI ("restaurant", "tourist_attraction", etc.)
    
    Returns list of nearby locations.
    """
    
    def _run(self, query: str) -> str:
        try:
            params = json.loads(query)
            lat = params.get("latitude", 0)
            lon = params.get("longitude", 0)
            radius = params.get("radius_km", 1.0)
            poi_type = params.get("poi_type", "tourist_attraction")
            
            # Use Overpass API to find nearby POIs
            result = asyncio.run(self._find_pois_async(lat, lon, radius, poi_type))
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _find_pois_async(
        self, 
        lat: float, 
        lon: float, 
        radius_km: float, 
        poi_type: str
    ) -> Dict[str, Any]:
        """Find POIs using Overpass API"""
        try:
            radius_m = int(radius_km * 1000)  # Convert to meters
            
            # Overpass query for POIs
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["tourism"="{poi_type}"](around:{radius_m},{lat},{lon});
              way["tourism"="{poi_type}"](around:{radius_m},{lat},{lon});
              relation["tourism"="{poi_type}"](around:{radius_m},{lat},{lon});
            );
            out geom;
            """
            
            url = "https://overpass-api.de/api/interpreter"
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    url,
                    data={"data": overpass_query},
                    headers={"User-Agent": "BikeRentalAgent/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get("elements", [])
                    
                    pois = []
                    for element in elements[:10]:  # Limit results
                        if element.get("type") == "node":
                            pois.append({
                                "name": element.get("tags", {}).get("name", "Unnamed"),
                                "type": poi_type,
                                "latitude": element.get("lat", 0),
                                "longitude": element.get("lon", 0),
                                "distance_km": self._calculate_distance(
                                    lat, lon, 
                                    element.get("lat", 0), 
                                    element.get("lon", 0)
                                )
                            })
                    
                    pois.sort(key=lambda x: x["distance_km"])
                    
                    return {
                        "success": True,
                        "center": {"latitude": lat, "longitude": lon},
                        "radius_km": radius_km,
                        "poi_type": poi_type,
                        "total_found": len(pois),
                        "locations": pois
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Overpass API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error finding POIs: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Helper to calculate distance"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return round(R * c, 2)

# Tool instances
geocode_tool = GeocodeLocationTool()
distance_tool = CalculateDistanceTool()
nearby_locations_tool = FindNearbyLocationsTool()
