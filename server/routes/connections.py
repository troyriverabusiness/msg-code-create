from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from server.service import connections
from server.models.journey import Journey

router = APIRouter(prefix="/api/v1", tags=["connections"])


# Request/Response Models
class ConnectionsRequest(BaseModel):
    """Request model for connections endpoint."""
    start: str
    end: str
    trip_plan: str


class ConnectionsResponse(BaseModel):
    """Response model for connections endpoint."""
    journeys: List[Journey]


@router.post("/connections", response_model=ConnectionsResponse)
async def get_connections(request: ConnectionsRequest):
    return connections.get_connections_example(request)

