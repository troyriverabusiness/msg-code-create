from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from server.agent.core import get_agent_executor


router = APIRouter(prefix="/api/v1", tags=["chat"])

# Initialize agent executor (lazy loaded)
agent_executor = None


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
    Chat endpoint with LangGraph agent.

    Uses a ReAct agent with tools for live departures and train details.
    Session management is simplified for MVP.

    Args:
        request: ChatRequest with message field
        x_session_id: Optional session ID (for future conversation continuity)

    Returns:
        ChatResponse with session_id and AI response message

    Raises:
        HTTPException: 500 if agent execution fails
    """
    global agent_executor

    try:
        # Lazy initialize agent
        if agent_executor is None:
            agent_executor = get_agent_executor()

        # Invoke the LangGraph agent
        response = agent_executor.invoke({
            "messages": [{"role": "user", "content": request.message}]
        })

        # Extract the last message (AI response)
        last_message = response["messages"][-1]
        response_text = last_message.content

        # Generate session ID if not provided (simplified for MVP)
        session_id = x_session_id or "default-session"

        return ChatResponse(session_id=session_id, message=response_text)

    except Exception as e:
        print(f"Agent Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )
