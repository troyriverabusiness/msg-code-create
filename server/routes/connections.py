from fastapi import APIRouter
from server.service import connections
from server.models.API import ConnectionsRequest, ConnectionsResponse

router = APIRouter(prefix="/api/v1", tags=["connections"])

@router.post("/connections", response_model=ConnectionsResponse)
async def get_connections(request: ConnectionsRequest):
    return connections.get_connections(request)

