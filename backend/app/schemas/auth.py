from pydantic import BaseModel
from typing import Optional, List


class Message(BaseModel):
    """Represents a single message in the conversation."""
    role: str  # "user" or "assistant"
    content: str


class UserRegister(BaseModel):
    """Request for user registration"""
    username: str
    password: str
    email: str


class UserLogin(BaseModel):
    """Request for user login"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Response with user info"""
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Response after authentication"""
    success: bool
    message: str
    user_id: Optional[int] = None
    username: Optional[str] = None


class AnalysisResponse(BaseModel):
    session_id: str  # Unique ID for this diagnosis session
    disease: str
    confidence: float
    recommendations: str
    next_steps: str
    tips: str
    system_context: str  # System role for subsequent chatting


class ConversationHistory(BaseModel):
    """Tracks conversation history between user and assistant."""
    messages: List[Message] = []  # Empty list for new sessions


class PredictionResponse(BaseModel):
    disease: str
    confidence: float


class ChatRequest(BaseModel):
    # Session ID (can be None for new session from DB)
    session_id: Optional[str] = None
    disease: str
    confidence: float
    message: str
    history: Optional[List[Message]] = None  # Message history
    system_context: Optional[str] = None  # System role from analysis


class ChatResponse(BaseModel):
    response: str
    # Updated conversation history including the new response
    history: List[Message]


class SessionHistory(BaseModel):
    """Complete diagnosis session with chat history"""
    session_id: str
    disease: str
    confidence: float
    recommendations: str
    next_steps: str
    tips: str
    created_at: str
    messages: List[Message]


class UserSessions(BaseModel):
    """List of user's past sessions"""
    sessions: List[SessionHistory]


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
