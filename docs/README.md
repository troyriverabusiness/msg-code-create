# Smart Travel Assistant Documentation

> Conversational travel planner for the German rail network

## Quick Navigation

| Document | Description | Audience |
|----------|-------------|----------|
| **Architecture** | | |
| [System Overview](./architecture/system-overview.md) | High-level architecture, components, pipeline | All |
| [Graph Traversal Service](./architecture/graph-traversal-service.md) | Deep dive on route discovery algorithm | Developers |
| [Data Flow](./architecture/data-flow.md) | Complete request lifecycle | Developers |
| [Architecture Decisions](./architecture/architecture-decisions.md) | ADRs and rationale | Maintainers |
| **API** | | |
| [API Reference](./api/api-reference.md) | Endpoints and contracts | Frontend, Integration |
| [Data Models](./api/data-models.md) | Pydantic models explained | Developers |
| **Guides** | | |
| [Getting Started](./guides/getting-started.md) | Setup and first run | New developers |
| [Frontend Integration](./guides/frontend-integration.md) | Vue.js integration | Frontend |
| [Deployment](./guides/deployment.md) | Docker and production | DevOps |

---

## System Overview

The Smart Travel Assistant combines:

- **GTFS Data**: Static train schedules (~500K entries)
- **Live API**: Real-time delays from DB Timetables
- **AI Agent**: Conversational planning with AWS Bedrock
- **Graph Algorithm**: NetworkX for route discovery

```
User → Chat → AI understands intent
     → Search → Graph finds routes → DB returns trains → AI adds insights
     → Results displayed
```

**See:** [System Overview](./architecture/system-overview.md) for full architecture

---

## Key Concepts

### The 3-Step Pipeline

1. **Discover** - GraphService finds transfer candidates using Dijkstra
2. **Retrieve** - TravelService queries GTFS for actual trains
3. **Evaluate** - JourneyService validates transfers and adds AI insights

### Chat-First Flow

Users build a "Travel Plan" through conversation before executing search. This allows complex intents like "stop somewhere nice" or "need wheelchair access."

**See:** [Architecture Decisions](./architecture/architecture-decisions.md) for rationale

---

## For Stakeholders

Start with:
1. [System Overview](./architecture/system-overview.md) - What the system does
2. [Data Flow](./architecture/data-flow.md) - How a request works

## For Developers

Start with:
1. [Getting Started](./guides/getting-started.md) - Run locally
2. [Graph Traversal Service](./architecture/graph-traversal-service.md) - Core algorithm
3. [Data Models](./api/data-models.md) - Understand the types

## For Maintainers

Start with:
1. [Architecture Decisions](./architecture/architecture-decisions.md) - Why we built it this way
2. [Deployment](./guides/deployment.md) - Production considerations

---

## Project Structure

```
msg-code-create/
├── server/                 # FastAPI backend
│   ├── service/           # Business logic
│   │   ├── graph_service.py      # Route discovery
│   │   ├── journey_service.py    # Orchestration
│   │   └── travel_service.py     # GTFS queries
│   ├── models/            # Pydantic models
│   ├── routes/            # API endpoints
│   └── data/              # SQLite DB, graph cache
├── client/                # Vue.js frontend
├── docs/                  # This documentation
└── ROADMAP.md            # Future plans
```

---

## Related Links

- [ROADMAP.md](../ROADMAP.md) - Future enhancements
- [Archive](./archive/) - Historical brainstorming notes
