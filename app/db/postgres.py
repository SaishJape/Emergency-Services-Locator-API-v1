import uuid
from typing import List, Tuple

from sqlalchemy import Column, String, Float, Boolean, Text, select, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from geoalchemy2 import Geography, WKTElement
from geoalchemy2.functions import ST_DWithin, ST_Distance

from app.config import settings
from app.db.models import Service  # your Pydantic model for input

Base = declarative_base()

class ServiceDB(Base):
    """
    Database model for services with geospatial support
    """
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    type = Column(String)
    location = Column(String)
    address = Column(Text)
    mobile_no = Column(String)
    timings = Column(String)
    cost = Column(String)
    available = Column(Boolean)
    contact = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geography(geometry_type='POINT', srid=4326))


# Initialize DB engine and session
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def insert_services(services: List[Service]):
    """
    Insert multiple services into the database
    
    Args:
        services: List of Service objects to insert
    """
    async with AsyncSessionLocal() as session:
        db_services = [
            ServiceDB(
                name=s.name,
                type=s.type,
                location=s.location,
                address=s.address,
                mobile_no=s.mobile_no,
                timings=s.timings,
                cost=s.cost,
                available=s.available,
                contact=s.contact,
                latitude=s.latitude,
                longitude=s.longitude,
                geom=WKTElement(f'POINT({s.longitude} {s.latitude})', srid=4326)
            )
            for s in services
        ]
        session.add_all(db_services)
        await session.commit()


async def search_nearby(lat: float, lon: float, top_k: int = 100, radius_km: int = 20):
    """
    Search for services near a geographical point
    
    Args:
        lat: Latitude of search center
        lon: Longitude of search center
        top_k: Maximum number of results to return
        radius_km: Search radius in kilometers
        
    Returns:
        List of service dictionaries sorted by distance
    """
    async with AsyncSessionLocal() as session:
        point = WKTElement(f'POINT({lon} {lat})', srid=4326)

        stmt = (
            select(ServiceDB)
            .where(ST_DWithin(ServiceDB.geom, point, radius_km * 1000))  # radius in meters
            .order_by(ST_Distance(ServiceDB.geom, point))
            .limit(top_k)
        )

        results = (await session.execute(stmt)).scalars().all()

        services = [
            {
                "name": r.name,
                "type": r.type,
                "location": r.location,
                "address": r.address,
                "mobile_no": r.mobile_no,
                "timings": r.timings,
                "cost": r.cost,
                "available": r.available,
                "contact": r.contact,
                "latitude": r.latitude,
                "longitude": r.longitude,
            }
            for r in results
        ]

        return services


async def get_all_services(skip: int = 0, limit: int = 100, service_type: str = None):
    """
    Retrieve all services from the database with pagination and optional type filtering
    
    Args:
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        service_type: Optional filter by service type
    
    Returns:
        Tuple containing list of service objects and total count
    """
    async with AsyncSessionLocal() as session:
        # Base query
        query = select(ServiceDB)
        count_query = select(func.count()).select_from(ServiceDB)
        
        # Apply type filter if provided
        if service_type:
            query = query.where(ServiceDB.type == service_type)
            count_query = count_query.where(ServiceDB.type == service_type)
        
        # Get total count with applied filters
        total_count = await session.execute(count_query)
        total_count = total_count.scalar()
        
        # Get paginated results with applied filters
        query = query.order_by(ServiceDB.name).offset(skip).limit(limit)
        results = (await session.execute(query)).scalars().all()
        
        services = [
            {
                "id": str(r.id),
                "name": r.name,
                "type": r.type,
                "location": r.location,
                "address": r.address,
                "mobile_no": r.mobile_no,
                "timings": r.timings,
                "cost": r.cost,
                "available": r.available,
                "contact": r.contact,
                "latitude": r.latitude,
                "longitude": r.longitude,
            }
            for r in results
        ]
        
        return services, total_count


async def get_service_types():
    """
    Retrieve all unique service types from the database
    
    Returns:
        List of distinct service type strings
    """
    async with AsyncSessionLocal() as session:
        from sqlalchemy import distinct
        stmt = select(distinct(ServiceDB.type)).order_by(ServiceDB.type)
        results = (await session.execute(stmt)).scalars().all()
        
        # Convert results to a list of strings
        service_types = list(results)
        
        return service_types


async def init_db():
    """
    Initialize database tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)