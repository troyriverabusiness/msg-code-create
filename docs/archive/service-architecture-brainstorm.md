# Service Architecture

> **Goal**: Chat for intent understanding, deterministic services for data, AI for evaluation.

---

## The Two-Phase Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Intent Understanding (/chat)                                  │
│  ─────────────────────────────────────                                  │
│                                                                         │
│  User: "I want to go to Munich tomorrow, maybe stop somewhere nice"    │
│                        │                                                │
│                        ▼                                                │
│              ┌─────────────────┐                                        │
│              │  LLM (Bedrock)  │  ← Conversational, builds TravelPlan   │
│              └────────┬────────┘                                        │
│                       │                                                 │
│                       ▼                                                 │
│              TravelPlan {                                               │
│                origin: "Frankfurt",                                     │
│                destination: "Munich",                                   │
│                date: "2024-12-07",                                      │
│                via: null,           ← user hasn't decided yet           │
│                preferences: {...}                                       │
│              }                                                          │
│                                                                         │
│  Loop until user says "search" or plan.isReady = true                   │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: Journey Search (/connections)                                 │
│  ──────────────────────────────────────                                 │
│                                                                         │
│  Input: TravelPlan (from Phase 1)                                       │
│                        │                                                │
│    ┌───────────────────┼───────────────────┐                            │
│    │                   │                   │                            │
│    ▼                   ▼                   ▼                            │
│  ┌──────────┐   ┌────────────┐   ┌──────────────┐                       │
│  │ Resolver │   │   Graph    │   │   Travel     │   DETERMINISTIC       │
│  │ ──────── │   │ ────────── │   │ ──────────── │   (no AI)             │
│  │ Name→EVA │   │ Find paths │   │ GTFS lookup  │                       │
│  └──────────┘   └────────────┘   └──────────────┘                       │
│                        │                                                │
│                        ▼                                                │
│              ┌─────────────────┐                                        │
│              │  SmartLinker    │  ← Enrich with platform, delays        │
│              └────────┬────────┘                                        │
│                       │                                                 │
│                       ▼                                                 │
│              ┌─────────────────┐                                        │
│              │  LLM Evaluate   │  ← ONE call: rank + generate insights  │
│              └────────┬────────┘                                        │
│                       │                                                 │
│                       ▼                                                 │
│              Journey[] (sorted, with aiInsight)                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Endpoint | Purpose | AI Usage |
|----------|---------|----------|
| `POST /api/v1/chat` | Build TravelPlan via conversation | LLM understands intent |
| `POST /api/v1/connections` | Execute search, return journeys | LLM evaluates results (1 call) |

### `/chat` - Intent Understanding

```python
# Request
{"message": "I want to go to Munich tomorrow"}

# Response
{
    "session_id": "uuid",
    "message": "Got it! Where are you traveling from?",
    "plan": {
        "origin": null,
        "destination": "Munich",
        "date": "2024-12-07",
        "isReady": false
    }
}
```

The LLM:
- Extracts intent from natural language
- Asks clarifying questions
- Updates the TravelPlan incrementally
- Signals when ready to search

### `/connections` - Journey Search

```python
# Request
{
    "start": "Frankfurt",
    "end": "Munich",
    "trip_plan": "..."  # or structured TravelPlan
}

# Response
{
    "journeys": [Journey, Journey, ...]
}
```

**No LLM tool calls** - direct service pipeline with evaluation at end.

---

## Data Models (Existing)

```python
# Journey (server/models/journey.py)
{
    "startStation": {"name": "Frankfurt (Main) Hbf", "eva": 8000105},
    "endStation": {"name": "München Hbf", "eva": 8000261},
    "totalTime": 195,
    "description": "Direct ICE connection, fastest option.",  # = aiInsight
    "changes": [
        {"station": {...}, "timeMinutes": 30}
    ],
    "trains": [
        {
            "trainNumber": "ICE 690",
            "startLocation": {...},
            "endLocation": {...},
            "platform": 12,
            "path": [...],
            "wagons": [1, 2, 2, 3]  # capacity per wagon
        }
    ]
}
```

**No model changes needed** - existing models match the target.

---

## Service Layer

### Services Overview

| Service | Responsibility | AI? |
|---------|---------------|-----|
| `StationResolver` | "Frankfurt" → EVA 8000105 | No |
| `GraphService` | Find paths, intermediate stations | No |
| `TravelService` | GTFS trip lookup | No |
| `SmartLinker` | Match live → static, add platform/delays | No |
| `JourneyEvaluator` | Rank journeys, generate insights | **Yes (1 call)** |

### JourneyService (Orchestrator)

```python
class JourneyService:
    def search(self, plan: TravelPlan) -> List[Journey]:
        # 1. Resolve station names → EVA codes
        origin = self.resolver.resolve(plan.origin)
        dest = self.resolver.resolve(plan.destination)

        # 2. Find intermediate stations (if user wants stopovers)
        if plan.wants_stopover and not plan.via:
            suggestions = self.graph.find_intermediate_stations(origin, dest)
            # Could return early here for user to pick

        # 3. Get trains from GTFS
        trains = self.travel.get_trains(origin, dest, plan.via, plan.time)

        # 4. Enrich with live data
        enriched = self.linker.enrich(trains)

        # 5. Build journey candidates
        candidates = self._build_journeys(enriched)

        # 6. AI evaluation (single LLM call)
        return self.evaluator.evaluate(candidates, plan.preferences)
```

### JourneyEvaluator

```python
class JourneyEvaluator:
    def evaluate(self, journeys: List[Journey], preferences: dict) -> List[Journey]:
        prompt = f"""
        Rank these {len(journeys)} train journeys for a traveler with preferences: {preferences}

        For each journey, provide:
        - Ranking (1 = best)
        - A brief insight (why this option, any warnings)

        Journeys: {journeys_as_json}

        Respond in JSON format.
        """

        response = self.bedrock.send_message(prompt)
        return self._apply_rankings(journeys, response)
```

---

## Why This Architecture?

### Problems with Agent-Driven Tools

| Issue | Impact |
|-------|--------|
| Agent decides which tool to call | Unpredictable behavior |
| Multiple LLM round-trips | Slow (2-4 calls per request) |
| Tool failures need agent recovery | Complex error handling |
| Hard to debug | "Why did it call that tool?" |

### Benefits of Service-First + AI-Last

| Benefit | How |
|---------|-----|
| **Predictable** | Same service chain every time |
| **Fast** | 1 LLM call instead of 2-4 |
| **Debuggable** | Clear service boundaries |
| **Cheap** | Less AI token usage |
| **Testable** | Services can be unit tested |

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| `GraphService` | ✅ Done | Uses `top_stations.json` (~1000 nodes), pathfinding works |
| `LinkerService` | 🔄 Partial | Structure exists, live enrichment is `pass` |
| `SimulationService` | ✅ Done | Deterministic hash-based delays |
| `connections.py` | 🔄 Partial | Path finding works, uses mock Train data |
| `StationResolver` | ❌ TODO | Currently inline in `_find_node_by_name` |
| `JourneyService` | ❌ TODO | Logic is in `connections.py` but incomplete |

### What's Working
- Graph loads from `top_stations.json` (not just "Hbf" filter)
- `nx.shortest_path()` finds routes between stations
- `LinkerService.find_trip_id()` queries GTFS by train number
- `SimulationService.get_delay()` returns deterministic delays

### What's Missing
1. **Live data enrichment** - `LinkerService.get_trip_details()` has `pass` for today's trains
2. **Real train lookup** - `connections.py` uses mock `ICE 100+i` instead of actual GTFS trips
3. **Segment → Trip mapping** - No logic to find which train covers a path segment

---

## Next Steps

1. **StationResolver** (~50 lines)
   - Fuzzy match station names to EVA codes
   - Use existing EVA map + DB fallback

2. **JourneyService** (~100 lines)
   - Wire together existing services
   - Build Journey objects from train data

3. **JourneyEvaluator** (~50 lines)
   - Single prompt to rank and add insights
   - Parse structured response

4. **Update `/connections` route**
   - Replace stub with JourneyService call

---

## Open Questions

1. **Wagon/capacity data** - Available in GTFS or separate API?
2. **Live delays** - Timetables API integration timing?
3. **Graph deduplication** - By `parent_station` or name grouping?

---

## Architecture Evaluation

> *Honest assessment of whether this approach is correct.*

### Verdict: Yes, this is the right approach.

#### 1. AI is used where it adds value, not where it's overkill

| Task | AI Good? | Why |
|------|----------|-----|
| Understanding "tomorrow morning to Munich" | ✅ Yes | Natural language is fuzzy, AI excels here |
| Finding train ICE 690 in GTFS | ❌ No | Database query is faster, cheaper, deterministic |
| Ranking "which journey is best for wheelchair user" | ✅ Yes | Requires reasoning about trade-offs |

This architecture puts AI at the **boundaries** (user intent, evaluation) and uses code for the **core logic**. That's correct.

#### 2. Avoids the "AI hammering" anti-pattern

Many teams do this:
```
User → AI → Tool → AI → Tool → AI → Tool → AI → Response
```

This architecture does:
```
User → AI (understand) → Services (execute) → AI (evaluate) → Response
```

**2 AI calls vs 4+.** Faster, cheaper, more predictable.

#### 3. The separation matches the problem domain

- **Chat phase**: Ambiguous, conversational, needs clarification → LLM is perfect
- **Search phase**: Structured query, known data → Services are perfect
- **Evaluation**: Subjective ranking, insight generation → LLM is perfect

---

### Potential Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Chat LLM doesn't extract plan correctly** | Strong system prompt + validate plan schema |
| **Evaluator LLM returns unparseable JSON** | Use structured output / JSON mode, have fallback |
| **Services return 0 journeys** | Return helpful error, suggest alternatives |
| **Too many journeys for LLM context** | Pre-filter top 10 before evaluation |

---

### MVP Suggestion: Skip AI Evaluation Initially

The `JourneyEvaluator` is nice-to-have. For MVP, consider:

1. Sort journeys by `totalTime` (fastest first)
2. Use **template-based insights** instead of LLM:

```python
def generate_insight(journey: Journey) -> str:
    if not journey.changes:
        return f"Direct connection in {journey.totalTime} min."

    change = journey.changes[0]
    if change.timeMinutes > 60:
        return f"Via {change.station.name} with {change.timeMinutes} min to explore."

    return f"Connection with {len(journey.changes)} change(s)."
```

This gives a working demo without the evaluation LLM call. Add AI evaluation later when core flow works.

---

### Summary

| Aspect | Verdict |
|--------|---------|
| Architecture pattern | ✅ Correct (services + AI at edges) |
| Complexity | ✅ Appropriate for the problem |
| AI usage | ✅ Strategic, not excessive |
| Implementability | ✅ Clear path with existing services |

**Conclusion**: The architecture is sound. Focus on wiring up the services.

---

*Last updated: December 2024*
