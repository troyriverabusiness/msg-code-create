"""Example routes"""

from fastapi import APIRouter
from service import example_service

router = APIRouter(prefix="/api", tags=["example"])


@router.get("/hello")
async def hello(name: str = "World"):
    """
    Simple hello endpoint that calls the service layer.

    Args:
        name: Optional name parameter (defaults to "World")

    Returns:
        Greeting response from the service
    """
    return example_service.get_greeting(name)
