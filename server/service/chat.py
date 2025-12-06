from typing import Optional
from server.data_access.AWS.bedrock_service import BedrockService
from server.data_access.AWS.config import (
    AWS_ACCESS_KEY,
    AWS_SECRET,
    AWS_REGION,
    AWS_SHORT_TERM_KEY,
)
from .session_manager import session_manager


if (not AWS_ACCESS_KEY or not AWS_SECRET) and not AWS_SHORT_TERM_KEY:
    raise ValueError(
        "AWS credentials not found in .env file. "
        "Please add AWS_ACCESS_KEY and AWS_SECRET OR AWS_SHORT_TERM_KEY to .env"
    )

bedrock_service = BedrockService(
    aws_access_key=AWS_ACCESS_KEY, aws_secret_key=AWS_SECRET, region=AWS_REGION
)


def chat(message: str, session_id: Optional[str] = None) -> tuple[str, str]:
    session = session_manager.get_or_create_session(session_id)
    history = session_manager.get_history(session.session_id)

    try:
        response = bedrock_service.send_message(
            message=message, conversation_history=history
        )

        session_manager.add_message(session.session_id, "user", message)
        session_manager.add_message(session.session_id, "assistant", response)

        return response, session.session_id

    except RuntimeError as e:
        raise RuntimeError(f"Failed to get AI response: {str(e)}")
