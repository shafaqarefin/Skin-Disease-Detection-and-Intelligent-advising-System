"""
File with all Schema Defintions
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    # In production, use hashed passwords
    password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("DiagnosisSession", back_populates="user")


class DiagnosisSession(Base):
    __tablename__ = "diagnosis_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True,
                        nullable=False)  # UUID for frontend
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    disease = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    recommendations = Column(Text)
    next_steps = Column(Text)
    tips = Column(Text)
    system_context = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey(
        "diagnosis_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("DiagnosisSession", back_populates="messages")
