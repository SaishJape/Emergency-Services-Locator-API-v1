import requests
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Body
from geopy.distance import geodesic
from typing import Dict, Any, Optional, List
from rapidfuzz import process, fuzz

from app.db.postgres import insert_services, search_nearby, get_all_services, get_service_types
from app.utils.common import parse_csv, extract_location_and_service
from app.db.models import Service, UserQuery
from app.config import settings
from app.services.location_service import geocode_location

router = APIRouter()

@router.post("/add_service/")
async def add_service(service: Service):
    """
    Add a single service to the database
    """
    await insert_services([service])
    return {"message": "Service added successfully."}

@router.post("/upload_services/")
async def upload(file: UploadFile = File(...)):
    """
    Upload and process a CSV file of services
    """
    services = parse_csv(file)
    await insert_services(services)
    return {"message": f"{len(services)} services uploaded successfully."}

@router.get("/services/")
async def list_all_services(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    type: Optional[str] = Query(None, description="Filter services by type")
):
    """
    Get all services from the database with pagination and optional type filtering
    """
    services, total_count = await get_all_services(skip=skip, limit=limit, service_type=type)
    
    return {
        "pagination": {
            "total": total_count,
            "offset": skip,
            "limit": limit,
            "has_more": (skip + limit) < total_count
        },
        "services": services
    }

@router.get("/service-types/")
async def list_service_types():
    """
    Get all unique service types from the database
    """
    types = await get_service_types()
    return {"service_types": types}

@router.post("/get_help/")
async def get_help(user_query: UserQuery = Body(...)):
    """
    Find nearby services based on user query and location
    """
    query = user_query.query
    user_lat = user_query.latitude
    user_lon = user_query.longitude

    if not query:
        raise HTTPException(status_code=400, detail="Query text is required")
    
    if user_lat is None or user_lon is None:
        raise HTTPException(status_code=400, detail="Location coordinates are required")

    # If service type not provided, extract from query
    if not user_query.service_type:
        mentioned_location, inferred_type = extract_location_and_service(query)
        best_type = await get_best_matching_service_type(inferred_type or query)
        user_query.service_type = best_type or "unknown"
        user_query.location_mentioned = mentioned_location

    analysis = {
        'service_type': user_query.service_type or 'unknown',
        'location_mentioned': user_query.location_mentioned,
        'urgency': user_query.urgency or 'Medium'
    }

    service_type = analysis.get("service_type", "unknown")
    mentioned_location = analysis.get("location_mentioned")
    urgency = analysis.get("urgency", "Medium")
    
    target_lat, target_lon = user_lat, user_lon
    location_name = "your current location"
    
    # If a location is mentioned, try to geocode it
    if mentioned_location:
        try:
            location_data = await geocode_location(mentioned_location)
            if location_data:
                target_lat = location_data["latitude"]
                target_lon = location_data["longitude"]
                location_name = location_data["display_name"]
        except Exception as e:
            print(f"Geocoding error: {e}")
    
    # Get nearby services
    results = await search_nearby(target_lat, target_lon, top_k=100)

    print("User Service Type:", user_query.service_type)
    # for r in results:
    #     print("Result Type:", r.get('type', ''))
    
    type_filtered = [
        r for r in results 
        if r.get('type', '').strip().lower() == user_query.service_type.strip().lower()
    ]

    # from rapidfuzz import fuzz

    # type_filtered = [
    #     r for r in results 
    #     if fuzz.partial_ratio(user_query.service_type.lower(), r.get('type', '').lower()) > 80
    # ]

    # Set radius based on urgency
    radius_km = settings.DEFAULT_SEARCH_RADIUS_KM
    if urgency == "High":
        radius_km = 15
    elif urgency == "Low":
        radius_km = 5
    
    # Filter by distance
    filtered_by_radius = [
        r for r in type_filtered
        if geodesic((target_lat, target_lon), (r['latitude'], r['longitude'])).km <= radius_km
    ]
    
    filtered = filtered_by_radius
    
    # Handle no results scenario
    if len(filtered) == 0:
        return {
            "original_query": query,
            "understood_service": service_type,
            "target_location": location_name,
            "target_coordinates": [target_lat, target_lon],
            "user_coordinates": [user_lat, user_lon],
            "urgency": urgency,
            "radius_km": radius_km,
            "nearby_services": [],
            "message": f"No {service_type} services found within {radius_km}km of the target location. Try increasing the search radius or selecting a different service type."
        }
    
    # Calculate distances for results
    for result in filtered:
        result['distance_km'] = round(
            geodesic((target_lat, target_lon), (result['latitude'], result['longitude']))
            .km, 2
        )
    
    # Sort by distance
    filtered.sort(key=lambda x: x['distance_km'])
    
    return {
        "original_query": query,
        "understood_service": service_type,
        "target_location": location_name,
        "target_coordinates": [target_lat, target_lon],
        "user_coordinates": [user_lat, user_lon],
        "urgency": urgency,
        "radius_km": radius_km,
        "nearby_services": filtered
    }

async def get_best_matching_service_type(user_input: str) -> Optional[str]:
    all_service_types = await get_service_types()
    if not all_service_types:
        return None
    best_match, score, _ = process.extractOne(
        query=user_input.lower(),
        choices=[stype.lower() for stype in all_service_types],
        scorer=fuzz.token_sort_ratio
    )
    return best_match if score > 60 else None  # adjust threshold if needed