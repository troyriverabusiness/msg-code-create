# Project Context & Key Decisions

> **Purpose**: This document captures critical context, architectural decisions, and "tribal knowledge" established during development sessions. Read this to understand the *why* behind the code.

## 1. Architecture: The "Refinement Loop"
We moved away from a traditional search-first approach to a **Chat-First** flow:
*   **Phase 1 (Chat)**: The user talks to the AI to build a structured `TravelPlan`. The frontend sends `POST /chat`, and the AI updates the plan (Origin, Dest, Date, Preferences) until it's ready.
*   **Phase 2 (Search)**: Only when the plan is finalized does the frontend trigger `POST /search`.
*   **Why?**: To allow for complex intent understanding (e.g., "stop in Fulda", "step-free access") before hitting the database.

## 2. The "Smart Linker" Algorithm
We are building a custom matching engine inspired by **HAFAS Reconstruction Match** (found in `datachaos/Algorithm-Inspiration/`):
*   **Problem**: Live API data (Timetables) has no static context (accessibility, full path). GTFS has static context but no live status.
*   **Solution**: We link them using a multi-level strategy:
    1.  **Strict Match**: Train Number + Category + Time (±5m).
    2.  **Fuzzy Match**: Train Number + Time (±60m) (ignores Category typos).
    3.  **Spatial Validation**: Check if the GTFS trip actually stops at the station.
    4.  **AI Resolution**: Use the LLM to resolve ambiguous station names or edge cases.

## 3. API Simplification (MVP Focus)
We drastically reduced the API surface area to just **2 Core Endpoints**:
*   `POST /chat`: Handles all conversation and state management.
*   `POST /search`: Executes the 3-step logic:
    1.  **Discover**: Find intermediate stations (Graph Search).
    2.  **Get Trains**: Fetch GTFS + Live Data.
    3.  **Calculate**: Run the Smart Linker.
*   **Removed**: `/trip/{id}` (all details are now sent in the search result).
*   **Simplified Models**: `Journey` object focuses on `aiInsight`, `totalTime`, and a simple list of `trains`. Real-time platform details were deferred for later.

## 4. AWS Authentication
*   **Primary**: Long-term credentials (`AWS_ACCESS_KEY`, `AWS_SECRET`) using `langchain-aws`.
*   **Fallback**: Custom `BedrockBearerTokenLLM` using a short-term token (`AWS_SHORT_TERM_KEY`).
*   **Status**: Verified working via CLI.

## 5. Current State & Next Steps
*   **Missing Services**: `bedrock_service.py` and `timetable_service.py` were deleted during refactoring and need to be rebuilt to match the new `api_specification.md`.
*   **Data**: GTFS and NeTEx ingestion is working. The database is populated.
*   **Immediate Goal**: Implement the "Discover Intermediate Stations" logic (Step 1 of Search).
