import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "arcee-agent:latest")
    
    # API Configuration
    CITYBIKES_API_URL = os.getenv("CITYBIKES_API_URL", "https://api.citybik.es/v2")
    GBFS_BASE_URL = os.getenv("GBFS_BASE_URL", "https://gbfs.org")
    
    # Application Settings
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Supported European Cities
    SUPPORTED_CITIES = {
        "amsterdam": {
            "country": "Netherlands",
            "networks": ["ns-fiets", "ov-fiets"],
            "gbfs_url": "https://gbfs.nextbike.net/maps/gbfs/v1/nextbike_amsterdam/gbfs.json"
        },
        "paris": {
            "country": "France", 
            "networks": ["velib"],
            "gbfs_url": "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/gbfs.json"
        },
        "berlin": {
            "country": "Germany",
            "networks": ["nextbike-berlin", "call-a-bike-berlin"],
            "gbfs_url": "https://gbfs.nextbike.net/maps/gbfs/v1/nextbike_berlin/gbfs.json"
        },
        "london": {
            "country": "United Kingdom",
            "networks": ["santander-cycles"],
            "gbfs_url": "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
        },
        "barcelona": {
            "country": "Spain",
            "networks": ["bicing"],
            "gbfs_url": "https://www.bicing.barcelona/get-stations"
        },
        "madrid": {
            "country": "Spain",
            "networks": ["bicimad"],
            "gbfs_url": "https://opendata.emtmadrid.es/Datos-estaticos/Datos-generales-(1)"
        }
    }
