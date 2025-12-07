from pydantic import BaseModel
from typing import List, Optional
from .journey import Journey

class ConnectionsRequest(BaseModel):
    origin: str
    destination: str
    date: Optional[str] = None
    via: Optional[str] = None
    min_transfer_time: Optional[int] = 0
    
class ConnectionsResponse(BaseModel):
    journeys: List[Journey]
