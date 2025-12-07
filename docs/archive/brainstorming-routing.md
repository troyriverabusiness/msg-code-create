# Brainstorming: Multi-Leg Routing & Transfers

## The Problem
You noticed that queries like "Frankfurt to Munich" only return **direct connections** (single ICE/RE trains). 

**Why?**
The current implementation in `TravelService.find_routes` performs a SQL query that joins the `stop_times` table with itself on the `trip_id`.
```sql
-- Pseudo-code of current logic
SELECT * FROM stop_times s1, stop_times s2
WHERE s1.trip_id = s2.trip_id  -- SAME TRAIN
  AND s1.stop_id = Start
  AND s2.stop_id = End
```
This fundamentally restricts results to trains that physically drive the entire distance. It misses:
- Faster connections involving a change (e.g., ICE to Mannheim + ICE to Munich).
- Connections where no direct train exists (e.g., small village to different small village).

## Proposed Solution: Graph-Guided Routing

Building a full "Connection Scan Algorithm" (CSA) or Raptor engine in Python might be overkill and slow. Instead, we can use our existing **GraphService** as a heuristic to guide the search.

### 1. Architectural Change
We need a new hierarchical data model.

**Current:**
`RouteOption` (A single train)

**New:**
`Journey`
  ├── `duration`: int
  ├── `transfers`: int
  └── `legs`: List[`Leg`]
       ├── `Leg 1` (Frankfurt -> Mannheim, ICE 123)
       └── `Leg 2` (Mannheim -> Munich, ICE 555)

### 2. Algorithm: "The Skeleton Approach"

We can implement a `RoutingService` that orchestrates this:

**Step 1: Find Path Candidates (GraphService)**
Ask the Graph for top paths based on static travel time.
*   *Input:* Frankfurt -> Munich
*   *Graph Output:* `[Frankfurt, Mannheim, Stuttgart, Ulm, Munich]` (Weighted Path)

**Step 2: Identify Hubs**
We don't need to change at *every* station. We identify "Hubs" (major stations) in the path.
*   *Segments:* Frankfurt -> Mannheim, Mannheim -> Stuttgart, ...

**Step 3: Recursive Segment Solving (TravelService)**
We try to bridge the gap between Start and Destination.

*   **Attempt 1 (Direct):** specific query for Frankfurt -> Munich.
*   **Attempt 2 (1 Transfer):**
    *   Iterate through nodes in the Graph Path.
    *   Pick a pivot node (e.g., Mannheim).
    *   **Leg A:** Find direct train Frankfurt -> Mannheim (Arrive 10:30).
    *   **Leg B:** Find direct train Mannheim -> Munich (Depart > 10:35).
    *   If both exist, we have a valid connection.

### 3. Implementation Plan

1.  **Update Models:** Create `Journey` and `Leg` pydantic models.
2.  **Update `TravelService`:** Add a `find_connection_legs(start, end, min_time)` method that returns *all* matching trains (not just top 5) for a specific segment.
3.  **New `JourneyService`:**
    *   Takes `origin`, `destination`, `time`.
    *   Tries finding a direct route first.
    *   If limited results, calls `GraphService.find_intermediate_stations` to get candidate transfer points.
    *   Loops through candidates:
        *   Find `Leg 1` (Origin -> Candidate).
        *   For each valid Leg 1, calculate `arrival_time + transfer_buffer`.
        *   Find `Leg 2` (Candidate -> Destination) starting after buffer.
        *   Stitch them together into a `Journey`.

### 4. Visualizing in Frontend
The frontend currently expects a flat list of `RouteOption`. We will need to update the UI to display:
*   Summary Card: "10:00 - 14:00 (4h) | 1 Transfer"
*   Detail View: List of trains involved.

## Immediate Next Steps
1.  Confirm we want to pursue the **"1 Transfer"** logic first (covers 80% of complex cases).
2.  Prototype the `JourneyService` script to test the logic without touching the API yet.
