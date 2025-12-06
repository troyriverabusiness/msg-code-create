from pydantic import BaseModel


class ConnectionsRequest(BaseModel):
    """Request model for connections endpoint."""
    start: str
    end: str
    trip_plan: str

