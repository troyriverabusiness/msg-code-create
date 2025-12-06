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

### Other Routes

**GET** `/hello` - Test endpoint


