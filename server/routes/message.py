from fastapi import APIRouter
# TODO: Service import missing

router = APIRouter(prefix="/api", tags=["message"])

@router.get("/message")
async def get_message():
    return {"message": "Hello, World!"}