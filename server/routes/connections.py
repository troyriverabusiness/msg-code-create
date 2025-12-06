from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query
from server.service import connections
from server.models.API import ConnectionsRequest, ConnectionsResponse

router = APIRouter(prefix="/api/v1", tags=["connections"])


@router.post("/connections", response_model=ConnectionsResponse)
async def get_connections(request: ConnectionsRequest):
    """
    Get train connections between two stations.

    This endpoint finds possible journeys from the start station to the end station,
    including direct trains and journeys that require changing trains.

    The request body should contain:
    - start: Name of the departure station (e.g., "Frankfurt", "München Hbf")
    - end: Name of the destination station (e.g., "Berlin", "Hamburg Hbf")
    - trip_plan: Additional trip planning preferences (optional context)

    Returns a list of possible journeys sorted by total travel time.
    """
    return connections.get_connections(request)


@router.post("/connections/example", response_model=ConnectionsResponse)
async def get_connections_example(request: ConnectionsRequest):
    """
    Get example connections (mock data for testing).

    This endpoint returns pre-defined example journeys for testing purposes.
    """
    return connections.get_connections_example(request)


@router.get("/connections", response_model=ConnectionsResponse)
async def get_connections_get(
    start: str = Query(..., description="Name of the departure station"),
    end: str = Query(..., description="Name of the destination station"),
    departure_time: Optional[str] = Query(
        None, description="Departure time in ISO format (YYYY-MM-DDTHH:MM:SS)"
    ),
):
    """
    Get train connections between two stations (GET endpoint).

    Alternative GET endpoint for fetching connections.

    Query parameters:
    - start: Name of the departure station
    - end: Name of the destination station
    - departure_time: Optional departure time in ISO format
    """
    # Parse departure time if provided
    dt = None
    if departure_time:
        try:
            dt = datetime.fromisoformat(departure_time)
        except ValueError:
            pass

    request = ConnectionsRequest(start=start, end=end, trip_plan="")
    return connections.get_connections(request, departure_time=dt)
