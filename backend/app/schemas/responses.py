from pydantic import BaseModel
from typing import Optional


class AnalysisResponse(BaseModel):
    disease: str
    confidence: float
    recommendations: str
    next_steps: str
    tips: str


class PredictionResponse(BaseModel):
    disease: str
    confidence: float


class ChatRequest(BaseModel):
    disease: str
    confidence: float
    message: str


class ChatResponse(BaseModel):
    response: str


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
