from pydantic import BaseModel
from typing import List
from .station import Station


class Train(BaseModel):
    trainNumber: str
    startLocation: Station
    endLocation: Station
    # Pfad 
    path: List[Station]
    platform: int
    # Liste von Auslastung
    wagons: List[int]

