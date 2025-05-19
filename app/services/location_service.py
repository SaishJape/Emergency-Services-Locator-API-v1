import requests
from typing import Dict, Optional, Any
from app.config import settings

async def geocode_location(location_query: str) -> Optional[Dict[str, Any]]:
    """
    Geocode a location string to coordinates using OpenStreetMap's Nominatim
    
    Args:
        location_query: Location string to geocode
        
    Returns:
        Dictionary with lat, lon and display name if found, None otherwise
        
    Raises:
        Exception: If the geocoding request fails
    """
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": location_query, 
                "format": "json", 
                "limit": 1
            },
            headers={"User-Agent": settings.NOMINATIM_USER_AGENT},
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            return {
                "latitude": float(data[0]["lat"]),
                "longitude": float(data[0]["lon"]),
                "display_name": data[0].get("display_name", location_query)
            }
        return None
        
    except Exception as e:
        # Log error here if needed
        raise Exception(f"Geocoding failed: {str(e)}")