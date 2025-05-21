from pydantic import BaseModel
from typing import List, Optional

class Service(BaseModel):
    """
    Schema for service data
    """
    name: str
    type: str
    latitude: float
    longitude: float
    location: Optional[str] = None
    address: Optional[str] = None
    mobile_no: Optional[str] = None
    timings: Optional[str] = None
    cost: Optional[str] = None
    available: Optional[bool] = True
    contact: Optional[str] = None

class UserQuery(BaseModel):
    """
    Schema for user queries requesting help
    """
    query: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    service_type: Optional[List[str]] = None
    location_mentioned: Optional[str] = None
    urgency: Optional[str] = "Medium"