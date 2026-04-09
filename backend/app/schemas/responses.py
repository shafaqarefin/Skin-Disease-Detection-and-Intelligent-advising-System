from pydantic import BaseModel
from typing import Optional, List


class Message(BaseModel):
    """Represents a single message in the conversation."""
    role: str  # "user" or "assistant"
    content: str


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
    session_id: Optional[str] = None  # Session ID for persistent chat history
    disease: str
    confidence: float
    message: str
    history: Optional[List[Message]] = None  # Temporary session history
    system_context: Optional[str] = None  # System role from analysis


class ChatResponse(BaseModel):
    response: str
    # Updated conversation history including the new response
    history: List[Message]


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
