import httpx
from typing import Dict, List, Any, Optional
from utils.config import Config
from utils.logger import logger

class CityBikesService:
    def __init__(self):
        self.base_url = Config.CITYBIKES_API_URL
    
    async def get_networks(self) -> List[Dict[str, Any]]:
        """Get all available bike sharing networks"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/networks")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("networks", [])
                return []
        except Exception as e:
            logger.error(f"Error fetching networks: {e}")
            return []
    
    async def get_network_by_city(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Find bike sharing network for a specific city"""
        networks = await self.get_networks()
        city_lower = city_name.lower()
        
        for network in networks:
            network_name = network.get("name", "").lower()
            location = network.get("location", {})
            city = location.get("city", "").lower()
            country = location.get("country", "").lower()
            
            if (city_lower in city or 
                city_lower in network_name or
                any(city_lower in tag.lower() for tag in network.get("tags", []))):
                return network
        
        return None
    
    async def get_network_details(self, network_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific network"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/networks/{network_id}")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("network", {})
                return None
        except Exception as e:
            logger.error(f"Error fetching network details: {e}")
            return None
    
    async def get_stations_for_city(self, city_name: str) -> List[Dict[str, Any]]:
        """Get all bike stations for a specific city"""
        network = await self.get_network_by_city(city_name)
        if not network:
            logger.warning(f"No network found for city: {city_name}")
            return []
        
        network_id = network.get("id")
        network_details = await self.get_network_details(network_id)
        
        if network_details:
            return network_details.get("stations", [])
        return []
    
    async def find_nearby_stations(
        self, 
        city_name: str, 
        target_lat: float, 
        target_lon: float, 
        max_distance_km: float = 5.0
    ) -> List[Dict[str, Any]]:
        """Find bike stations near a specific location"""
        stations = await self.get_stations_for_city(city_name)
        nearby_stations = []
        
        for station in stations:
            station_lat = station.get("latitude", 0)
            station_lon = station.get("longitude", 0)
            
            # Calculate approximate distance (simplified haversine)
            distance_km = self._calculate_distance(
                target_lat, target_lon, 
                station_lat, station_lon
            )
            
            if distance_km <= max_distance_km:
                station["distance_km"] = round(distance_km, 2)
                nearby_stations.append(station)
        
        # Sort by distance
        nearby_stations.sort(key=lambda x: x.get("distance_km", float("inf")))
        return nearby_stations
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        import math
        
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
