# Testing & Verification

This directory contains reports and instructions for verifying the functionality of the backend services.

## Automated Verification Report

See [FEATURE_VERIFICATION_REPORT.md](./FEATURE_VERIFICATION_REPORT.md) for the latest run output verifying:
1. **Intermediate Station Discovery** (Graph Service)
2. **Planned Timetable Retrieval** (DB API integration)

## Running the Verification Script

To run the verification script and generate a new report:

1. Navigate to the `server` directory:
   ```bash
   cd server
   ```

2. Run the script using `uv` (to ensure dependencies are loaded):
   ```bash
   uv run ../scripts/verify_features_report.py
   ```

The script will:
- Initialize the `GraphService` (loading the graph from cache or DB).
- Query `find_intermediate_stations` for a sample route (Frankfurt -> Munich).
- Call the DB API via `plan_service` to get the current hour's planned trains for Frankfurt Hbf.
- Generate/Overwrite `server/TEST_REPORT.md` (which you can move here if needed).

## Frontend Testing

The frontend is integrated with these services. To test manually:
1. Start the backend: `cd server && uv run main.py`
2. Start the frontend: `cd client && npm run dev`
3. Open the browser and use the chat or connection search features.
