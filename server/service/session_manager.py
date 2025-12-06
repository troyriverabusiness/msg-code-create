"""
Session management for chat conversations.

TODO: Replace in-memory storage with Redis or database for production use.
This will allow sessions to persist across server restarts and scale horizontally.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ChatSession:
    """Represents a chat session with conversation history."""

    session_id: str
    created_at: datetime
    last_activity: datetime
    messages: List[Dict[str, str]] = field(default_factory=list)


class SessionManager:
    """Manages chat sessions in memory with TTL support."""

    def __init__(self, session_ttl_hours: int = 1, max_messages: int = 10):
        """
        Initialize session manager.

        Args:
            session_ttl_hours: Hours until session expires (default: 1)
            max_messages: Maximum messages to keep in history (default: 10)
        """
        self.sessions: Dict[str, ChatSession] = {}
        self.session_ttl = timedelta(hours=session_ttl_hours)
        self.max_messages = max_messages

    def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        """
        Get existing session or create a new one.

        Args:
            session_id: Optional session ID. If None, creates new session.

        Returns:
            ChatSession object
        """
        # Clean up expired sessions
        self._cleanup_expired()

        # Create new session if no ID provided or session doesn't exist
        if not session_id or session_id not in self.sessions:
            new_id = session_id if session_id else str(uuid.uuid4())
            now = datetime.now()
            session = ChatSession(
                session_id=new_id, created_at=now, last_activity=now, messages=[]
            )
            self.sessions[new_id] = session
            return session

        # Return existing session and update last activity
        session = self.sessions[session_id]
        session.last_activity = datetime.now()
        return session

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to session history.

        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        session.messages.append({"role": role, "content": content})

        # Trim to max_messages (keep most recent)
        if len(session.messages) > self.max_messages:
            session.messages = session.messages[-self.max_messages :]

        session.last_activity = datetime.now()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        if session_id not in self.sessions:
            return []

        return self.sessions[session_id].messages.copy()

    def _cleanup_expired(self) -> None:
        """Remove expired sessions from memory."""
        now = datetime.now()
        expired_ids = [
            sid
            for sid, session in self.sessions.items()
            if now - session.last_activity > self.session_ttl
        ]

        for sid in expired_ids:
            del self.sessions[sid]

    def get_session_count(self) -> int:
        """Get number of active sessions."""
        self._cleanup_expired()
        return len(self.sessions)


# Global session manager instance
session_manager = SessionManager(session_ttl_hours=1, max_messages=10)
