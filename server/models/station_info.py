from pydantic import BaseModel
from typing import List

class StationInfo(BaseModel):
    name: str
    facilities: List[str]
    entrances: List[str]
