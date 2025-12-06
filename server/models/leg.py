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
