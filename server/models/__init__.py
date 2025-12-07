"""
Shared Pydantic domain models for the server application.

Import models from here for use across routes and services.
"""
from .journey import Journey
from .leg import Leg
from .stop import Stop
from .station import Station
from .station_change import StationChange
from .train import Train
from .connection_schema import ConnectionsRequest, ConnectionsResponse
from .route_option import RouteOption
from .platform_info import PlatformInfo
from .station_info import StationInfo
from .real_time_status import RealTimeStatus

__all__ = [
    "Journey",
    "Leg",
    "Station",
    "StationChange",
    "Train",
    "ConnectionsRequest",
    "ConnectionsResponse",
    "RouteOption",
    "PlatformInfo",
    "StationInfo",
    "RealTimeStatus",
]

