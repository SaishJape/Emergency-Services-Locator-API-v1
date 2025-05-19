# from pydantic import BaseModel, BaseSettings
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Database credentials
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "emergency_services")
    
    # Constructed database URL
    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection string from credentials"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # API settings
    API_VERSION: str = "v1"
    APP_NAME: str = "Emergency Services Locator API"
    
    # Geocoding settings
    NOMINATIM_USER_AGENT: str = os.getenv("NOMINATIM_USER_AGENT", "EmergencyLocator/1.0")
    
    # Service search settings
    DEFAULT_SEARCH_RADIUS_KM: int = 10
    DEFAULT_SEARCH_LIMIT: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings object
settings = Settings()