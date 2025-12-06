from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from service import chat as chat_service


router = APIRouter(prefix="/api", tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    session_id: str
    message: str


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str


@router.post(
    "/chat", response_model=ChatResponse, responses={500: {"model": ErrorResponse}}
)
async def chat_endpoint(
    request: ChatRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-Id"),
):
    """
    Chat endpoint with AWS Bedrock integration.

    Supports conversation continuity through session management.
    If X-Session-Id header is not provided, a new session will be created.

    Args:
        request: ChatRequest with message field
        x_session_id: Optional session ID from X-Session-Id header

    Returns:
        ChatResponse with session_id and AI response message

    Raises:
        HTTPException: 500 if Bedrock API call fails
    """
    try:
        # Call chat service
        response_message, session_id = chat_service.chat(
            message=request.message, session_id=x_session_id
        )

        return ChatResponse(session_id=session_id, message=response_message)

    except RuntimeError as e:
        # Return error response for API failures
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
