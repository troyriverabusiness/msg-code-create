from typing import List
from pydantic import BaseModel
from server.models.journey import Journey

class ConnectionsResponse(BaseModel):
    """Response model for connections endpoint."""
    journeys: List[Journey]




