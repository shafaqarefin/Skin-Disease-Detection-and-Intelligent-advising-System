from sqlalchemy.orm import Session
from app.core.models import User, DiagnosisSession, ChatMessage
from app.schemas.responses import Message
from typing import List, Optional
import hashlib


class DatabaseService:
    """A single DB object for all interaction"""

    @staticmethod
    def create_user(db: Session, username: str, password: str, email: str) -> User:
        """Create a new user"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = User(username=username, password=hashed_password, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user - returns user if credentials match"""
        user = DatabaseService.get_user_by_username(db, username)
        if not user:
            return None

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user.password == hashed_password:
            return user
        return None

    @staticmethod
    def create_diagnosis_session(db: Session, user_id: int, session_id: str, disease: str,
                                 confidence: float, recommendations: str, next_steps: str,
                                 tips: str, system_context: str) -> DiagnosisSession:
        """Create a new diagnosis session"""
        session = DiagnosisSession(
            session_id=session_id,
            user_id=user_id,
            disease=disease,
            confidence=confidence,
            recommendations=recommendations,
            next_steps=next_steps,
            tips=tips,
            system_context=system_context
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_diagnosis_session_by_session_id(db: Session, session_id: str) -> Optional[DiagnosisSession]:
        """Get diagnosis session by session_id (UUID)"""
        return db.query(DiagnosisSession).filter(DiagnosisSession.session_id == session_id).first()

    @staticmethod
    def get_user_sessions(db: Session, user_id: int) -> List[DiagnosisSession]:
        """Get all diagnosis sessions for a user"""
        return db.query(DiagnosisSession).filter(DiagnosisSession.user_id == user_id).order_by(DiagnosisSession.created_at.desc()).all()

    @staticmethod
    def add_chat_message(db: Session, session_id: int, role: str, content: str) -> ChatMessage:
        """Add a chat message to a diagnosis session"""
        message = ChatMessage(session_id=session_id,
                              role=role, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_session_messages(db: Session, session_id: int) -> List[ChatMessage]:
        """Get all chat messages for a diagnosis session"""
        return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()

    @staticmethod
    def convert_messages_to_schema(messages: List[ChatMessage]) -> List[dict]:
        """Convert database messages to dictionaries (compatible with Pydantic serialization)"""
        return [{"role": msg.role, "content": msg.content} for msg in messages]
