from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConnectionsRequest(BaseModel):
    """Request model for connections endpoint."""

    start: str
    end: str
    trip_plan: str = ""
    departure_time: Optional[datetime] = Field(
        default=None,
        description="Departure time in ISO format (e.g., '2025-12-07T13:00:00'). Defaults to current time if not provided.",
    )
