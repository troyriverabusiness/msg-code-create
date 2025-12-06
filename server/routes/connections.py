from fastapi import APIRouter
from server.service import connections

router = APIRouter(prefix="/api/v1", tags=["connections"])

@router.get("/connections")
async def get_connections():
    return connections.get_connections()