"""Chat service with AWS Bedrock integration"""

from typing import Optional
from service.bedrock_service import BedrockService
from service.session_manager import session_manager
from service.config import AWS_ACCESS_KEY, AWS_SECRET, AWS_REGION


# Initialize Bedrock service
if not AWS_ACCESS_KEY or not AWS_SECRET:
    raise ValueError(
        "AWS credentials not found in .env file. "
        "Please add AWS_ACCESS_KEY and AWS_SECRET to .env"
    )

bedrock_service = BedrockService(
    aws_access_key=AWS_ACCESS_KEY, aws_secret_key=AWS_SECRET, region=AWS_REGION
)


def chat(message: str, session_id: Optional[str] = None) -> tuple[str, str]:
    """
    Process a chat message and return AI response.

    Args:
        message: User's message
        session_id: Optional session ID for conversation continuity

    Returns:
        Tuple of (response_message, session_id)

    Raises:
        RuntimeError: If Bedrock API call fails
    """
    # Get or create session
    session = session_manager.get_or_create_session(session_id)

    # Get conversation history
    history = session_manager.get_history(session.session_id)

    try:
        # Send message to Bedrock with conversation context
        response = bedrock_service.send_message(
            message=message, conversation_history=history
        )

        # Add user message and assistant response to history
        session_manager.add_message(session.session_id, "user", message)
        session_manager.add_message(session.session_id, "assistant", response)

        return response, session.session_id

    except RuntimeError as e:
        # Re-raise API errors to be handled by route
        raise RuntimeError(f"Failed to get AI response: {str(e)}")
