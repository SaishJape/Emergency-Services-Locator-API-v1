from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.api.routes import router as api_router
from app.db.postgres import init_db
from app.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="An API for locating emergency and general services based on user location and requirements",
    version=settings.API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    await init_db()

# Include API routes
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Emergency Services Locator API",
        "docs": "/docs",
        "version": settings.API_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)