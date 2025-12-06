"""Travel and timetable routes"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from server.service.timetable_service import TimetableService
from server.service.simulation import SimulationService

router = APIRouter(prefix="/api/v1", tags=["travel"])

# Service instances
timetable_service = TimetableService()
simulation_service = SimulationService()

# Hardcoded EVA mapping for MVP
STATION_EVA_MAP = {
    "München Hbf": "8000261",
    "Berlin Hbf": "8011160",
    "Hamburg Hbf": "8002549",
    "Frankfurt (Main) Hbf": "8000105",
    "Lindau-Reutin": "8003693",
    "Köln Hbf": "8000207",
    "Stuttgart Hbf": "8000096",
    "Leipzig Hbf": "8010205",
    "Dresden Hbf": "8010085",
    "Hannover Hbf": "8000152",
    "Nürnberg Hbf": "8000284"
}


@router.get("/status")
async def get_status():
    return {"status": "ok", "services": ["travel", "simulation", "timetable"]}


@router.get("/status/ticker")
async def get_ticker():
    """Returns real-time ticker messages from the simulation service."""
    messages = simulation_service.get_messages()
    return {"messages": messages}


@router.get("/live/{station_name}")
async def get_live_station_data(station_name: str):
    """
    Returns real-time departure/arrival data for a station.
    Uses Timetables API if EVA is known, otherwise returns 404.
    """
    # Try exact match
    eva_no = STATION_EVA_MAP.get(station_name)

    # Fuzzy match if exact match fails
    if not eva_no:
        for name, eva in STATION_EVA_MAP.items():
            if station_name.lower() in name.lower():
                eva_no = eva
                station_name = name  # Use canonical name
                break

    if not eva_no:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_name}' not found. Available: {', '.join(STATION_EVA_MAP.keys())}"
        )

    # Fetch merged station board
    now = datetime.now()
    board = timetable_service.get_station_board(eva_no, now)

    return {
        "station": station_name,
        "eva": eva_no,
        "departures": board
    }


@router.get("/stations")
async def list_stations():
    """Returns list of available stations."""
    return {"stations": list(STATION_EVA_MAP.keys())}
