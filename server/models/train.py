from pydantic import BaseModel
from typing import List
from .station import Station


class Train(BaseModel):
    name: str
    trainNumber: str
    startLocation: Station
    endLocation: Station
    departureTime: str
    arrivalTime: str
    # Pfad 
    path: List[Station]
    platform: int
    # Liste von Auslastung
    wagons: List[int]

