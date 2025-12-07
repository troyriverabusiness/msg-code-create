# Server Development

## Architecture Overview

This server follows a **layered architecture** pattern that separates concerns and enables maintainable, scalable development:

```
┌─────────────────────────────────────┐
│         Routing Layer               │
│      (FastAPI Routes)               │
│  /api/v1/connections, /chat, etc.   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Service Layer               │
│   (Business Logic & Orchestration)   │
│  JourneyService, TravelService, etc. │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Data Access Layer              │
│  (Database & External APIs)         │
│  DB Services, AWS Bedrock, etc.    │
└─────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. Routing Layer (`routes/`)
- **Purpose**: Handles HTTP requests and responses
- **Responsibilities**:
  - Request validation using Pydantic models
  - Route registration and API endpoint definitions
  - HTTP status code management
  - Input/output serialization

**Key Files:**
- `routes/connections.py` - Train connection endpoints
- `routes/chat.py` - AI chat endpoints
- `routes/travel.py` - Travel status and simulation endpoints
- `routes/example.py` - Example endpoints

**Example Flow:**
```python
# routes/connections.py
@router.post("/connections")
def get_connections(request: ConnectionsRequest):
    return connections.get_connections(request)  # Delegates to service layer
```

#### 2. Service Layer (`service/`)
- **Purpose**: Contains business logic and orchestrates operations
- **Responsibilities**:
  - Business rule enforcement
  - Data transformation and aggregation
  - Coordinating multiple data access operations
  - Session management
  - AI agent orchestration

**Key Services:**
- `service/connections.py` - Connection finding logic
- `service/journey_service.py` - Journey planning and routing
- `service/travel_service.py` - Travel segment finding
- `service/graph_service.py` - Station connectivity graph
- `service/chat.py` - AI chat orchestration
- `service/simulation.py` - Real-time delay simulation

**Example Flow:**
```python
# service/connections.py
def get_connections(request: ConnectionsRequest):
    journeys = journey_service.find_routes(...)  # Uses data access layer
    return ConnectionsResponse(journeys=journeys)
```

#### 3. Data Access Layer (`data_access/`)
- **Purpose**: Abstracts data persistence and external API interactions
- **Responsibilities**:
  - Database queries and transactions
  - External API calls (Deutsche Bahn, AWS Bedrock)
  - Data mapping and transformation
  - Connection management

**Key Components:**

**Database Services (`data_access/DB/`):**
- `timetable_service.py` - GTFS timetable queries
- `station_service.py` - Station information queries
- `full_changes_service.py` - Full schedule change data
- `recent_changes_service.py` - Recent schedule changes

**External Services (`data_access/AWS/`):**
- `bedrock_service.py` - AWS Bedrock AI integration
- `config.py` - AWS configuration

**Example Flow:**
```python
# data_access/DB/timetable_service.py
class TimetableService:
    def get_timetable(self, eva_id: str, date: str):
        # Direct SQLite queries
        # Returns raw data models
```

## Database

### SQLite Database

The application uses **SQLite** for local data storage, located at:
```
server/data/travel.db
```

### Database Schema

The database follows the **GTFS (General Transit Feed Specification)** format:

**Core Tables:**
- `stations` - Station/stop information (stop_id, stop_name, coordinates)
- `routes` - Train route definitions (route_id, route_short_name, route_type)
- `trips` - Individual trip instances (trip_id, route_id, train_number)
- `stop_times` - Timetable entries (trip_id, stop_id, arrival_time, departure_time)
- `transfers` - Station transfer information
- `pathways` - Station navigation paths
- `platforms` - Platform details

**Schema Definition:**
See `data/schema.sql` for the complete database schema.

**Database Access Pattern:**
```python
# Services connect directly to SQLite
DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
```

**Key Features:**
- Thread-safe connections (`check_same_thread=False`)
- Row factory for dictionary-like access
- Indexed queries for performance
- GTFS-compliant structure

### Data Files

The `data/` directory contains:
- `travel.db` - SQLite database (GTFS data)
- `schema.sql` - Database schema definition
- `graph_cache.json` - Cached station connectivity graph
- `top_stations.json` - Top stations list
- `db_fv_stations.csv` - Station reference data

## Development Flow

### Getting Started

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management and virtual environment handling.

#### Why uv?

uv is **extremely fast** - it's written in Rust and can be 10-100x faster than traditional tools like pip. It handles dependency resolution, virtual environments, and package installation all in one tool.

#### Setup

1. **Install uv** (if you haven't already):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # - AWS_ACCESS_KEY, AWS_SECRET (for Bedrock)
   # - TROY_CLIENT_ID, TROY_API_KEY (for Deutsche Bahn API)
   ```

4. **Run the server**:
   ```bash
   uv run python main.py
   ```

   The server will start on `http://0.0.0.0:8000`

### Adding Dependencies

To add a new dependency:
```bash
uv add <package-name>
```

For example:
```bash
uv add fastapi
uv add requests
```

For development dependencies:
```bash
uv add --dev pytest
```

### Running Commands

Run any Python command within the uv environment:
```bash
uv run python main.py
uv run pytest
uv run python scripts/check_stations.py
```

### Virtual Environment

uv automatically manages a virtual environment. To activate it manually:
```bash
source .venv/bin/activate  # On macOS/Linux
```

Or use `uv run` which automatically uses the correct environment.

### Development Workflow

#### 1. Adding a New Endpoint

1. **Create/Update Route** (`routes/your_route.py`):
   ```python
   from fastapi import APIRouter
   from server.service import your_service
   
   router = APIRouter(prefix="/api/v1", tags=["your-tag"])
   
   @router.post("/your-endpoint")
   def your_endpoint(request: YourRequest):
       return your_service.your_function(request)
   ```

2. **Register Route** (`main.py`):
   ```python
   from server.routes import your_route
   app.include_router(your_route.router)
   ```

3. **Create Service** (`service/your_service.py`):
   ```python
   from server.data_access.DB import your_data_service
   
   def your_function(request: YourRequest):
       data = your_data_service.get_data(...)
       # Business logic here
       return result
   ```

4. **Create Data Access** (`data_access/DB/your_data_service.py`):
   ```python
   import sqlite3
   from pathlib import Path
   
   DB_PATH = Path(__file__).parent.parent.parent / "data" / "travel.db"
   
   class YourDataService:
       def get_data(self, ...):
           conn = sqlite3.connect(DB_PATH)
           # Query database
           return results
   ```

#### 2. Database Operations

**Query Pattern:**
```python
DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row  # For dict-like access

cursor = conn.execute(
    "SELECT * FROM stations WHERE stop_name LIKE ?",
    (f"%{name}%",)
)
results = cursor.fetchall()
```

**Best Practices:**
- Use parameterized queries to prevent SQL injection
- Close connections when done (or use context managers)
- Use `row_factory = sqlite3.Row` for dictionary-like access
- Create indexes for frequently queried columns

#### 3. Testing

Run tests (when available):
```bash
uv run pytest
```

Run specific scripts:
```bash
uv run python scripts/check_stations.py
uv run python scripts/calculate_connectivity.py
```

### Project Structure

```
server/
├── routes/              # Routing layer (FastAPI endpoints)
│   ├── connections.py
│   ├── chat.py
│   └── travel.py
├── service/             # Service layer (business logic)
│   ├── connections.py
│   ├── journey_service.py
│   ├── travel_service.py
│   └── chat.py
├── data_access/         # Data access layer
│   ├── DB/              # Database services
│   │   ├── timetable_service.py
│   │   └── station_service.py
│   └── AWS/             # External API services
│       └── bedrock_service.py
├── models/              # Pydantic models
│   ├── API/             # Request/Response models
│   └── ...              # Domain models
├── data/                # Data files
│   ├── travel.db        # SQLite database
│   └── schema.sql       # Database schema
├── scripts/             # Utility scripts
├── main.py              # FastAPI application entry point
└── pyproject.toml       # Project dependencies
```

### Environment Variables

Required environment variables (see `.env.example`):
- `AWS_ACCESS_KEY` - AWS access key for Bedrock
- `AWS_SECRET` - AWS secret key for Bedrock
- `AWS_REGION` - AWS region (default: us-east-1)
- `TROY_CLIENT_ID` - Deutsche Bahn API client ID
- `TROY_API_KEY` - Deutsche Bahn API key
- `LARS_CLIENT_ID` - Fallback DB API client ID (optional)
- `LARS_API_KEY` - Fallback DB API key (optional)

### API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Common Tasks

**Check database status:**
```bash
uv run python scripts/check_stations.py
```

**Calculate station connectivity:**
```bash
uv run python scripts/calculate_connectivity.py
```

**Ingest delay data:**
```bash
uv run python scripts/ingest_delays.py
```

**Debug issues:**
```bash
uv run python scripts/debug_all.py
```

## Architecture Principles

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **Dependency Direction**: Dependencies flow downward (Routes → Services → Data Access)
3. **Testability**: Each layer can be tested independently
4. **Maintainability**: Changes in one layer don't cascade to others
5. **Scalability**: Easy to add new endpoints, services, or data sources

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [GTFS Specification](https://gtfs.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
