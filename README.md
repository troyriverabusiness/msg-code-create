# vibe-template
Perfect repo template for you to start vibecoding


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


