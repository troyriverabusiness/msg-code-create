from pydantic import BaseModel

class PlatformInfo(BaseModel):
    name: str
    accessibility: str
