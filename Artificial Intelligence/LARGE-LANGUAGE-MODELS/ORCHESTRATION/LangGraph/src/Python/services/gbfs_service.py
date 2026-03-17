import httpx
import json
from typing import Dict, List, Any, Optional
from utils.config import Config
from utils.logger import logger

class GBFSService:
    """Service for interacting with GBFS (General Bikeshare Feed Specification) APIs"""
    
    def __init__(self):
        self.base_url = Config.GBFS_BASE_URL
    
    async def get_gbfs_feed(self, gbfs_url: str) -> Optional[Dict[str, Any]]:
        """Fetch GBFS feed from a given URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(gbfs_url)
                if response.status_code == 200:
                    return response.json()
                logger.error(f"GBFS API error: {response.status_code} for {gbfs_url}")
                return None
        except Exception as e:
            logger.error(f"Error fetching GBFS feed: {e}")
            return None
    
    async def get_station_information(self, gbfs_url: str) -> List[Dict[str, Any]]:
        """Get station information from GBFS feed"""
        gbfs_data = await self.get_gbfs_feed(gbfs_url)
        if not gbfs_data:
            return []
        
        # Extract station information URL from GBFS discovery
        feeds = gbfs_data.get("data", {}).get("feeds", [])
        station_info_url = None
        
        for feed in feeds:
            if feed.get("name") == "station_information":
                station_info_url = feed.get("url")
                break
        
        if not station_info_url:
            logger.error("Station information URL not found in GBFS feed")
            return []
        
        # Fetch station information
        station_data = await self.get_gbfs_feed(station_info_url)
        if station_data:
            return station_data.get("data", {}).get("stations", [])
        return []
    
    async def get_station_status(self, gbfs_url: str) -> List[Dict[str, Any]]:
        """Get real-time station status from GBFS feed"""
        gbfs_data = await self.get_gbfs_feed(gbfs_url)
        if not gbfs_data:
            return []
        
        # Extract station status URL from GBFS discovery
        feeds = gbfs_data.get("data", {}).get("feeds", [])
        station_status_url = None
        
        for feed in feeds:
            if feed.get("name") == "station_status":
                station_status_url = feed.get("url")
                break
        
        if not station_status_url:
            logger.error("Station status URL not found in GBFS feed")
            return []
        
        # Fetch station status
        status_data = await self.get_gbfs_feed(station_status_url)
        if status_data:
            return status_data.get("data", {}).get("stations", [])
        return []
    
    async def get_combined_station_data(self, gbfs_url: str) -> List[Dict[str, Any]]:
        """Get combined station information and status"""
        station_info = await self.get_station_information(gbfs_url)
        station_status = await self.get_station_status(gbfs_url)
        
        # Create lookup dictionary for status
        status_lookup = {
            status.get("station_id"): status 
            for status in station_status
        }
        
        # Combine information and status
        combined_data = []
        for station in station_info:
            station_id = station.get("station_id")
            status = status_lookup.get(station_id, {})
            
            combined_station = {
                **station,
                "available_bikes": status.get("num_bikes_available", 0),
                "available_docks": status.get("num_docks_available", 0),
                "is_installed": status.get("is_installed", True),
                "is_renting": status.get("is_renting", True),
                "is_returning": status.get("is_returning", True),
                "last_reported": status.get("last_reported", 0)
            }
            combined_data.append(combined_station)
        
        return combined_data
    
    async def get_system_information(self, gbfs_url: str) -> Optional[Dict[str, Any]]:
        """Get system information from GBFS feed"""
        gbfs_data = await self.get_gbfs_feed(gbfs_url)
        if not gbfs_data:
            return None
        
        # Extract system information URL from GBFS discovery
        feeds = gbfs_data.get("data", {}).get("feeds", [])
        system_info_url = None
        
        for feed in feeds:
            if feed.get("name") == "system_information":
                system_info_url = feed.get("url")
                break
        
        if not system_info_url:
            logger.error("System information URL not found in GBFS feed")
            return None
        
        # Fetch system information
        system_data = await self.get_gbfs_feed(system_info_url)
        if system_data:
            return system_data.get("data", {})
        return None
