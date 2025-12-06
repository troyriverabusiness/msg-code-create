from pydantic import BaseModel
from typing import Optional
from .platform_info import PlatformInfo

class RouteOption(BaseModel):
    trip_id: str
    line_name: str
    start_station: str
    end_station: str
    scheduled_departure: str
    real_time_departure: str
    arrival: str
    delay_minutes: int
    platform: PlatformInfo
    occupancy: str
