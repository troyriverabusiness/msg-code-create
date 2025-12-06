from pydantic import BaseModel
from typing import Optional


class ConnectionsRequest(BaseModel):
    """Request model for connections endpoint."""
    start: str
    end: str
    trip_plan: str
    date: Optional[str] = None

