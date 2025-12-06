# Matching Algorithm Design

## Goal
Enable the agent to discover routes, intermediate stations, and calculate complex journeys (including stopovers) using a graph-based approach. This moves beyond simple point-to-point lookups to true network traversal.

## 1. Graph Representation
We will model the transport network as a directed graph.

*   **Nodes**: Stations (identified by `stop_id` or `parent_station`).
*   **Edges**: Direct connections between stations.
    *   **Definition**: An edge exists from Station A to Station B if there is at least one trip that goes directly from A to B (consecutive stops).
    *   **Attributes**:
        *   `weight`: Average travel time (minutes).
        *   `lines`: List of lines serving this edge (e.g., ["ICE 690", "RE 5"]).
        *   `frequency`: Trips per day/hour.

### Storage Strategy
Since querying raw GTFS `stop_times` for graph traversal is slow, we will build a lightweight **Network Graph** abstraction.
*   **Option A (In-Memory)**: Load the graph into `networkx` on startup. Good for small-medium networks.
*   **Option B (Database)**: Create a `connections` table in SQLite.
    ```sql
    CREATE TABLE connections (
        from_stop_id TEXT,
        to_stop_id TEXT,
        min_duration INTEGER,
        lines TEXT, -- JSON array
        PRIMARY KEY (from_stop_id, to_stop_id)
    );
    ```

## 2. Algorithms

### A. Discovery (Intermediate Stations)
**User Intent**: "I want to go from Frankfurt to Munich via somewhere nice."

**Logic**:
1.  **Pathfinding**: Find K-shortest paths (or all reasonable paths) from Origin to Destination in the abstract graph.
2.  **Node Extraction**: Identify all unique nodes (stations) that appear on these paths.
3.  **Filtering**:
    *   Filter out small stations (using `location_type` or heuristic like "number of connections").
    *   Rank by "detour cost" (how much time does stopping here add?).
4.  **Output**: A list of candidate stopover cities.

### B. Journey Calculation (Multi-Leg Routing)
**User Intent**: "Frankfurt -> Fulda (2h stop) -> Munich"

**Logic**:
1.  **Decomposition**: Break the request into segments.
    *   Segment 1: Frankfurt -> Fulda (Depart: User Time)
    *   Segment 2: Fulda -> Munich (Depart: Arrival at Fulda + 2h)
2.  **Segment Solving**:
    *   For each segment, use the `TravelService.find_routes` (or improved version) to find concrete trains.
3.  **Chaining**:
    *   Select the best connection for Segment 1.
    *   Use its arrival time to constrain the search for Segment 2.
    *   Combine into a single `Journey` object.

### C. Route Finding (The Core)
**User Intent**: "Get me from A to B" (implies finding the best transfer points if no direct train exists).

**Algorithm**:
*   **Direct**: Check `connections` table.
*   **1-Transfer**: Find common neighbors in the graph. `Neighbors(A) INTERSECT Neighbors(B)`.
*   **General**: Dijkstra's Algorithm on the weighted graph to find the sequence of stations, then find trips for each edge.

## 3. Agent Tools
We will expose these capabilities as tools for the AI Agent:

### 1. `find_intermediate_stations`
*   **Input**: `origin: str`, `destination: str`
*   **Output**: `List[str]` (Station names)
*   **Description**: "Finds major stations located between origin and destination that are suitable for a stopover."

### 2. `get_possible_routes`
*   **Input**: `origin: str`, `destination: str`
*   **Output**: `List[List[str]]` (List of station sequences, e.g., `[["Frankfurt", "Fulda", "Munich"], ["Frankfurt", "Stuttgart", "Munich"]]`)
*   **Description**: "Returns abstract routes (sequences of transfer points) without specific times. Use this to explore options."

### 3. `plan_multi_leg_journey`
*   **Input**: `segments: List[{origin, destination, min_stopover}]`, `start_time`
*   **Output**: `Journey` (Detailed itinerary with trains and times)
*   **Description**: "Calculates a concrete itinerary for a multi-stop journey."

## 4. Implementation Steps
1.  **Graph Builder**: Create a script to populate the `connections` table from existing `stop_times`.
2.  **Routing Service**: Implement `RoutingService` class to handle graph queries.
3.  **Tool Integration**: Wrap `RoutingService` methods for the Agent.
