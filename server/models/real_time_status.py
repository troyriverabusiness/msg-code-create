from pydantic import BaseModel

class RealTimeStatus(BaseModel):
    status: str
    delay: int
