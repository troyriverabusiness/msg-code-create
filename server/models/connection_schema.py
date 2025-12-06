from pydantic import BaseModel
from typing import List, Optional
from .journey import Journey

class ConnectionsRequest(BaseModel):
    origin: str
    destination: str
    date: Optional[str] = None
    
class ConnectionsResponse(BaseModel):
    journeys: List[Journey]
