from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
from .station import Station


class Train(BaseModel):
    """
    Represents a train service with its route and timing information.

    Attributes:
        trainNumber: The train identifier (e.g., "ICE 920", "RE 50")
        trainId: The unique stop ID from the API (for deduplication)
        trainCategory: The category of train (ICE, IC, RE, RB, S)
        startLocation: The origin station of this train segment
        endLocation: The destination station of this train segment
        departureTime: Scheduled departure time
        arrivalTime: Scheduled arrival time at destination
        actualDepartureTime: Real-time departure time (if available)
        actualArrivalTime: Real-time arrival time (if available)
        path: List of stations the train passes through
        platform: Departure platform number
        wagons: Occupancy data per wagon (if available)
        delayMinutes: Delay in minutes (if any)
    """

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
    path: List[Station] = []
    platform: Optional[int] = None
    wagons: List[int] = []
    delayMinutes: int = 0
