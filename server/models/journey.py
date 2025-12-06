from pydantic import BaseModel
from typing import List, Optional
from .station import Station
from .train import Train
from .station_change import StationChange

class Journey(BaseModel):
    id: str
    startStation: Station
    endStation: Station
    
    trains: List[Train]
    # Can be direct trains
    changes: Optional[List[StationChange]]

    totalTime: int
    description: str