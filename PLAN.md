# Project Roadmap & Extensions

This document tracks future enhancements and features that are out of scope for the current MVP but planned for later.

## API Extensions

### Smarter Transfer Matching
- **Goal**: Use live data and historical patterns to validate transfers more intelligently than a fixed buffer.
- **Implementation**:
    - [ ] **Platform Awareness**: Use `TimetableService` to get real-time platform info.
    - [ ] **Dynamic Buffer**: 
        - Same Platform: 2 mins
        - Same Station: 7 mins
        - Cross-City: 10 mins
    - [ ] **Delay Propagation**: If incoming train is delayed, check if the connection is still reachable.

### Historical Data Integration
- **Goal**: Use the downloaded Parquet files (`datachaos/deutsche-bahn-data/`) to predict delays for future dates.
- **Implementation**:
    - [ ] **Ingestion Script**: `server/scripts/ingest_delays.py` to populate `delay_patterns` table.
    - [ ] **SimulationService**: Query this table to provide "Probable Delay" for future trips.

### Advanced Routing
- **Goal**: Replace the static GraphService with a time-dependent routing algorithm.
- **Implementation**:
    - [ ] **CSA (Connection Scan Algorithm)**: Implement CSA on the raw GTFS `stop_times` data.
    - [ ] **Raptor**: Alternative algorithm for multi-criteria optimization (e.g., "Fastest" vs "Fewest Transfers").

## Infrastructure
- [ ] **Dockerization**: Containerize the application for easier deployment.
- [ ] **Caching Strategy**: Move from JSON/GML file cache to Redis or similar for the Graph.
