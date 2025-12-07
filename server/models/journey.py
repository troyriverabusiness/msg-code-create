from pydantic import BaseModel
from typing import List, Optional
from .station import Station
from .train import Train
from .station_change import StationChange
from .leg import Leg

class Journey(BaseModel):
    id: str
    startStation: Station
    endStation: Station
    
    legs: List[Leg]
    transfers: int

    totalTime: int
    description: str