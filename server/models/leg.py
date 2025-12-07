from pydantic import BaseModel
from .station import Station
from .train import Train

class Leg(BaseModel):
    origin: Station
    destination: Station
    train: Train
    departureTime: str
    arrivalTime: str
    delayInMinutes: int = 0
    departurePlatform: str = "0"
    arrivalPlatform: str = "0"
