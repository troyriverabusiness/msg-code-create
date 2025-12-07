from pydantic import BaseModel
from typing import Optional
from .station import Station

class Stop(BaseModel):
    station: Station
    arrivalTime: Optional[str] = None
    departureTime: Optional[str] = None
    platform: Optional[str] = None
