"""
Shared Pydantic domain models for the server application.

Import models from here for use across routes and services.
Note: Request/Response models belong in their respective route files.
"""
from .platform_info import PlatformInfo
from .route_option import RouteOption
from .station_info import StationInfo
from .real_time_status import RealTimeStatus
from .station_change import StationChange
from .train import Train

__all__ = [
    "PlatformInfo",
    "RouteOption",
    "StationInfo",
    "RealTimeStatus",
    "StationChange",
    "Train",
]

