from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from server.agent.core import get_agent_executor
from server.service.session_manager import session_manager


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
    Session context is maintained using the session manager.

    Args:
        request: ChatRequest with message field
        x_session_id: Optional session ID for conversation continuity

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

        # Get or create session
        session = session_manager.get_or_create_session(x_session_id)
        session_id = session.session_id

        # Build messages list from conversation history
        history = session_manager.get_history(session_id)
        messages = []
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add the current user message
        messages.append({"role": "user", "content": request.message})

        # Invoke the LangGraph agent with full conversation history
        response = agent_executor.invoke({"messages": messages})

        # Extract the last message (AI response)
        last_message = response["messages"][-1]
        response_text = last_message.content

        # Store messages in session history
        session_manager.add_message(session_id, "user", request.message)
        session_manager.add_message(session_id, "assistant", response_text)

        return ChatResponse(session_id=session_id, message=response_text)

    except Exception as e:
        print(f"Agent Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
