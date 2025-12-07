from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
from .station import Station
from .stop import Stop

class Train(BaseModel):
    # ... (existing fields)
    trainNumber: str
    name: str = ""
    trainId: Optional[str] = None
    trainCategory: Optional[str] = None
    startLocation: Station
    endLocation: Station
    departureTime: Optional[Union[str, datetime]] = None
    arrivalTime: Optional[Union[str, datetime]] = None
    actualDepartureTime: Optional[Union[str, datetime]] = None
    actualArrivalTime: Optional[Union[str, datetime]] = None
    path: List[Stop] = []
    platform: Optional[int] = None
    wagons: List[int] = []
    delayMinutes: int = 0
