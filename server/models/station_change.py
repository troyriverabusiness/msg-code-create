from pydantic import BaseModel

from .station import Station


class StationChange(BaseModel):
    station: Station
    timeMinutes: int
    arrivalTime: str
    departureTime: str
    platform: str

