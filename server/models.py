from pydantic import BaseModel
from typing import List, Optional

class RouteRequest(BaseModel):
    start: str
    end: str
    time: Optional[str] = None # HH:MM:SS

class PlatformInfo(BaseModel):
    name: str
    accessibility: str # "Step-free", "Stairs only", etc.

class RouteOption(BaseModel):
    trip_id: str
    line_name: str # "ICE 690"
    start_station: str
    end_station: str
    scheduled_departure: str
    real_time_departure: str
    arrival: str
    delay_minutes: int
    platform: PlatformInfo
    occupancy: str # "Low", "Medium", "High"

class StationInfo(BaseModel):
    name: str
    facilities: List[str] # "Elevator", "Escalator"
    entrances: List[str]

class RealTimeStatus(BaseModel):
    messages: List[str]
    alternatives: List[str]
