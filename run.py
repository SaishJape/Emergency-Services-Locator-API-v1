import uvicorn
# import asyncio
import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_app():
    """Run the FastAPI application using Uvicorn server"""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_app()