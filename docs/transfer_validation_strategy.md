# Transfer Validation Strategy

## Goal
Ensure that the connections stitched together by `ConnectionsService` are physically possible and realistic for a human to make.

## The Challenge
We currently pick the "next available train" departing after the previous train arrives. This fails if:
1.  **Gap is too small**: Arrive 14:00, Depart 14:01 (1 min gap).
2.  **Platform distance**: Arrive Track 1, Depart Track 24 (needs 10+ mins).
3.  **Delays**: Incoming train is delayed by 5 mins, eating up the buffer.

## Proposed Solution: Hybrid Validation

We will implement a `validate_transfer(arrival_trip, departure_trip)` function that uses a hierarchy of checks.

### 1. The "Golden Rule" (Base Check)
*   **Minimum Buffer**: 5 minutes (default).
*   **Logic**: `DepartureTime - ArrivalTime >= 5 mins`.

### 2. Platform-Aware Check (Smarter Matching)
*   **Data Source**: 
    *   **Live**: `TimetableService` (DB API) gives real-time platforms.
    *   **Static**: `LinkerService` (GTFS) gives planned platforms.
*   **Logic**:
    *   **Same Platform** (Track 4 -> Track 4): Min 2 mins.
    *   **Same Station, Different Track**: Min 7 mins.
    *   **Cross-City** (Hbf -> Tief): Min 10 mins.

### 3. Real-Time / Simulation Adjustment
*   **Live (Today)**: 
    *   Fetch *Real-Time* Arrival of Train A.
    *   Fetch *Real-Time* Departure of Train B.
    *   Recalculate gap.
*   **Simulation (Future)**:
    *   Query `delay_patterns` (from the downloaded Parquet files).
    *   Apply "Probable Delay" to Train A.
    *   Check if connection still holds.

## Implementation Plan

### Step 1: Basic Validation (MVP)
- [ ] Update `ConnectionsService` to enforce a hard 5-minute minimum.

### Step 2: Platform Logic
- [ ] Update `LinkerService` to return platform info (already started).
- [ ] Implement `get_min_transfer_time(station, platform_a, platform_b)`.

### Step 3: Historical Data Ingestion
- [ ] Create script `server/scripts/ingest_delays.py`.
- [ ] Read Parquet files (`datachaos/deutsche-bahn-data/`).
- [ ] Aggregate average delays by `train_number` and `station`.
- [ ] Store in `delay_patterns` table.

### Step 4: Smart Matching
- [ ] In `ConnectionsService`, before finalizing a connection:
    - Check if `date == today`.
    - If yes, call `TimetableService` to get live delays.
    - If `RealArrival + MinBuffer > RealDeparture`, discard and find next train.
