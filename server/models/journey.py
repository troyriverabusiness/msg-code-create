from pydantic import BaseModel
from typing import List, Optional
from .station import Station
from .train import Train
from .stationChange import StationChange

class Journey(BaseModel):
    startStation: Station
    endStation: Station
    
    trains: List[Train]
    # Can be direct trains
    changes: Optional[List[StationChange]]

    totalTime: int
    description: str