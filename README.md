# Smart Travel Assistant 🚆✨

A hackathon project combining **GTFS** (Static Schedule), **NeTEx** (Accessibility/Platforms), and **DB Timetables API** (Live Data) with an **AI Agent** (LangGraph + Bedrock) to provide intelligent travel assistance.

## 🚀 Quick Start

### 1. Setup Environment
Ensure you have `uv` installed.

```bash
# Install dependencies
uv sync
```

### 2. Configure Credentials
Create a `server/.env` file with your API keys:

```bash
cp server/.env.example server/.env
```

Required keys:
*   `TROY_API_CLIENT` / `TROY_API_KEY`: DB Timetables API (Primary)
*   `LARS_API_CLIENT` / `LARS_API_KEY`: DB Timetables API (Fallback)
*   `AWS_SHORT_TERM_KEY`: AWS Bedrock Bearer Token (expires every 12h)
*   `AWS_REGION`: `eu-central-1`

### 3. Data Ingestion (One-Time)
Populate the SQLite database with GTFS and NeTEx data:

```bash
./scripts/reset_data.sh
```

### 4. Run the System

**Start the API Server:**
```bash
uv run server/main.py
```
> API available at: http://localhost:8000/docs
> Frontend at: http://localhost:8000

**Run the AI Agent CLI:**
```bash
uv run -m scripts.chat_cli
```


## API Endpoints

### Base URL

When deployed locally using docker compose:
```
http://localhost:8000/api
```

### Chat Endpoint

**POST** `/chat`

AI-powered chat endpoint using AWS Bedrock (Claude 3 Sonnet). Supports conversation continuity through session management.

#### Request

**Headers:**
- `Content-Type: application/json`
- `X-Session-Id: <uuid>` (optional) - If not provided, a new session will be created

**Body:**
```json
{
  "message": "Your message here"
}
```

#### Response

**Success (200):**
```json
{
  "session_id": "abc-123-def-456",
  "message": "AI assistant's response"
}
```

**Error (500):**
```json
{
  "detail": "AI service error: <error message>"
}
```

#### Session Management

- Sessions are stored in-memory and expire after 1 hour of inactivity
- Each session maintains up to 10 messages of conversation history
- Multiple users can chat simultaneously without conflicts by using different session IDs
- On first request without `X-Session-Id`, server generates a new session ID
- Include the returned `session_id` in subsequent requests via `X-Session-Id` header for conversation continuity

#### Example Usage

**First message (new session):**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "I'm doing well, thank you for asking! How can I help you today?"
}
```

**Follow-up message (existing session):**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: 550e8400-e29b-41d4-a716-446655440000" \
  -d '{"message": "What did I just ask you?"}'
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "You asked me how I was doing."
}
```

### Connections Endpoint

Find train connections between two stations, including direct trains and journeys requiring changes.

#### POST `/api/v1/connections`

**Request Body:**
```json
{
  "start": "Frankfurt Hbf",
  "end": "Berlin Hbf",
  "trip_plan": "",
  "departure_time": "2025-12-07T14:00:00"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start` | string | Yes | Name of the departure station (e.g., "Frankfurt", "München Hbf") |
| `end` | string | Yes | Name of the destination station (e.g., "Berlin", "Hamburg Hbf") |
| `trip_plan` | string | No | Additional trip planning preferences (optional context) |
| `departure_time` | string | No | ISO 8601 format (e.g., "2025-12-07T14:00:00"). Defaults to current time |

**Response (200):**
```json
{
  "journeys": [
    {
      "startStation": {
        "name": "Frankfurt(Main)Hbf",
        "eva": 8000105
      },
      "endStation": {
        "name": "Berlin Hbf",
        "eva": 8011160
      },
      "trains": [
        {
          "trainNumber": "ICE 920",
          "trainId": "unique-stop-id",
          "trainCategory": "ICE",
          "startLocation": { "name": "Frankfurt(Main)Hbf", "eva": 8000105 },
          "endLocation": { "name": "Berlin Hbf", "eva": 8011160 },
          "departureTime": "2025-12-07T14:30:00",
          "arrivalTime": "2025-12-07T18:45:00",
          "actualDepartureTime": "2025-12-07T14:32:00",
          "actualArrivalTime": "2025-12-07T18:50:00",
          "path": [
            { "name": "Fulda", "eva": 8000115 },
            { "name": "Erfurt Hbf", "eva": 8010101 }
          ],
          "platform": 8,
          "wagons": [],
          "delayMinutes": 5
        }
      ],
      "changes": [
        {
          "station": { "name": "Erfurt Hbf", "eva": 8010101 },
          "timeMinutes": 15
        }
      ],
      "totalTime": 255,
      "description": "Direct ICE connection via Erfurt"
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `journeys` | array | List of possible journeys sorted by total travel time (max 10) |
| `journeys[].startStation` | Station | Departure station with name and EVA code |
| `journeys[].endStation` | Station | Destination station with name and EVA code |
| `journeys[].trains` | array | List of trains in the journey (1 for direct, multiple for changes) |
| `journeys[].trains[].trainNumber` | string | Train identifier (e.g., "ICE 920", "RE 50") |
| `journeys[].trains[].trainCategory` | string | Type of train: ICE, IC, RE, RB, S |
| `journeys[].trains[].departureTime` | string | Scheduled departure (ISO 8601) |
| `journeys[].trains[].arrivalTime` | string | Scheduled arrival (ISO 8601) |
| `journeys[].trains[].actualDepartureTime` | string | Real-time departure if available |
| `journeys[].trains[].actualArrivalTime` | string | Real-time arrival if available |
| `journeys[].trains[].platform` | int | Departure platform number |
| `journeys[].trains[].delayMinutes` | int | Current delay in minutes |
| `journeys[].trains[].path` | array | Intermediate stations the train passes through |
| `journeys[].changes` | array | Station changes with transfer time (null for direct trains) |
| `journeys[].totalTime` | int | Total journey time in minutes |
| `journeys[].description` | string | Human-readable journey description |

#### GET `/api/v1/connections`

Alternative GET endpoint with query parameters.

**Query Parameters:**
- `start` (required): Name of the departure station
- `end` (required): Name of the destination station
- `departure_time` (optional): ISO 8601 format

**Example:**
```bash
curl "http://localhost:8000/api/v1/connections?start=Frankfurt&end=Berlin&departure_time=2025-12-07T14:00:00"
```

#### POST `/api/v1/connections/example`

Returns mock data for testing purposes. Accepts the same request body as the main endpoint.

#### How It Works

1. **Station Resolution**: Matches input station names to actual stations in the rail network
2. **Route Discovery**: Uses the rail network graph to find relevant intermediate stations
3. **Train Data Fetch**: Queries Deutsche Bahn Timetables API for trains at each station (current hour + next hour)
4. **Journey Building**: Constructs possible journeys including direct connections and those requiring changes
5. **Sorting & Limiting**: Returns up to 10 journeys sorted by total travel time

### Other Routes

**GET** `/hello` - Test endpoint


