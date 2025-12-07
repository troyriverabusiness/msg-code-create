# Getting Started

> Set up and run the Smart Travel Assistant locally.

## Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (optional, for containerized deployment)
- AWS credentials (for AI features)
- DB Timetables API credentials (for live data)

---

## Quick Start

### 1. Clone and Install

```bash
git clone <repository-url>
cd msg-code-create

# Install Python dependencies
uv sync
```

### 2. Configure Environment

Create the environment file:

```bash
cp server/.env.example server/.env
```

Edit `server/.env` with your credentials:

```bash
# DB Timetables API (required for live data)
TROY_API_CLIENT=your_client_id
TROY_API_KEY=your_api_key

# AWS Bedrock (required for AI features)
AWS_ACCESS_KEY=your_access_key
AWS_SECRET=your_secret_key
AWS_REGION=eu-central-1

# Alternative: Short-term bearer token
AWS_SHORT_TERM_KEY=your_bearer_token
```

### 3. Initialize Database

Populate SQLite with GTFS and NeTEx data:

```bash
./scripts/reset_data.sh
```

This creates:
- `server/data/travel.db` - GTFS database
- `server/data/graph_cache.json` - Pre-computed graph
- `server/data/top_stations.json` - Station rankings

### 4. Run the Server

```bash
uv run server/main.py
```

The server starts at:
- **API**: http://localhost:8000/api
- **Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:8000

---

## Verify Installation

### Test the API

```bash
# Health check
curl http://localhost:8000/api/v1/status

# Find connections
curl -X POST http://localhost:8000/api/v1/connections \
  -H "Content-Type: application/json" \
  -d '{
    "start": "Frankfurt",
    "end": "München",
    "departure_time": "2025-12-07T10:00:00"
  }'
```

### Test the Chat

```bash
# Start a conversation
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to travel from Berlin to Munich tomorrow"}'
```

### CLI Chat Interface

For interactive testing:

```bash
uv run -m scripts.chat_cli
```

---

## Docker Deployment

### Build and Run

```bash
docker compose up --build
```

Services:
- **Client** (Vue.js): http://localhost:3000
- **Server** (FastAPI): http://localhost:8000

### Environment

Docker reads from `server/.env` automatically via `env_file` in compose.yaml.

---

## Project Structure

```
msg-code-create/
├── server/
│   ├── main.py           # FastAPI entry point
│   ├── service/          # Business logic
│   │   ├── graph_service.py
│   │   ├── journey_service.py
│   │   └── travel_service.py
│   ├── models/           # Pydantic models
│   ├── routes/           # API endpoints
│   ├── data/             # SQLite DB, caches
│   └── .env              # Environment config
├── client/               # Vue.js frontend
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── compose.yaml          # Docker config
```

---

## Common Issues

### "GTFS data not found"

Run the data ingestion script:
```bash
./scripts/reset_data.sh
```

### "AI service unavailable"

Check AWS credentials in `.env`:
```bash
# Verify AWS config
cat server/.env | grep AWS
```

### "Station not found"

Try different name formats:
- "Frankfurt" → "Frankfurt (Main) Hbf"
- "Berlin" → "Berlin Hbf"

### Port already in use

Change the port:
```bash
PORT=8080 uv run server/main.py
```

---

## Next Steps

- [System Overview](../architecture/system-overview.md) - Understand the architecture
- [API Reference](../api/api-reference.md) - Explore all endpoints
- [Graph Traversal](../architecture/graph-traversal-service.md) - Deep dive into routing
