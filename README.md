project-root/
│
├── app/                          # Main app code
│   ├── main.py                   # FastAPI app entrypoint
│   ├── config.py                 # Centralized config & .env loader (Pydantic)
│
│   ├── api/                      # FastAPI endpoints (grouped by feature)
│   │   ├── routes.py             # All routes defined here
│   │   └── __init__.py
│
│   ├── db/                       # Database layer
│   │   ├── postgres.py           # PostgreSQL connector & queries
│   │   ├── models.py             # Pydantic models
│   │   └── __init__.py
│
│   ├── services/                 # Business logic / integrations
│   │   ├── location_service.py   # Handles geocoding and location processing
│   │   └── __init__.py
│
│   └── utils/                    # Utility functions
│       ├── common.py             # Reusable logic/helpers
│       └── __init__.py
│
├── .env                          # All secret keys (NEVER push to GitHub)
├── .gitignore                    # Git ignore file
├── requirements.txt              # Dependencies
└── README.md                     # Project documentation


# Emergency Services Locator API

A FastAPI application that helps users find nearby emergency and general services based on their location and service type requirements.

## Features

- Find nearby services based on user location
- Upload service data via CSV
- Filter services by type, location, and urgency
- Geographic radius-based search
- Support for different service types (ambulance, hospital, police, etc.)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your PostgreSQL database credentials:
   ```
   # Database credentials
   DB_USER=username
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=emergency_services
   ```
5. Make sure PostgreSQL is installed and running with PostGIS extension enabled

## Running the API

Start the development server:

```
uvicorn app.main:app --reload
```
OR
```
python run.py
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, access the auto-generated API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Setup

This application requires PostgreSQL with the PostGIS extension. To set up:

1. Install PostgreSQL and PostGIS
2. Create a database for the application
3. Enable the PostGIS extension:
   ```sql
   CREATE EXTENSION postgis;
   ```

## API Endpoints

- `POST /add_service/`: Add a single service
- `POST /upload_services/`: Upload multiple services via CSV
- `GET /services/`: List all services with filtering and pagination
- `GET /service-types/`: Get all unique service types
- `POST /get_help/`: Find nearby services based on user query and location

## Data Format

Services should include:
- name
- type
- location (optional)
- address (optional)
- mobile_no (optional)
- timings (optional)
- cost (optional)
- available (optional)
- contact (optional)
- latitude
- longitude