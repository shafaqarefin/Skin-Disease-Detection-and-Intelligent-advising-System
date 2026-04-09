from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.database_service import DatabaseService
from app.schemas.auth import UserRegister, UserLogin, AuthResponse, UserSessions, SessionHistory, Message
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if username already exists
        existing_user = DatabaseService.get_user_by_username(
            db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Username already exists")

        # Create new user
        user = DatabaseService.create_user(
            db, user_data.username, user_data.password, user_data.email)

        return AuthResponse(
            success=True,
            message="Registration successful",
            user_id=user.id,
            username=user.username
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    try:
        user = DatabaseService.authenticate_user(
            db, user_data.username, user_data.password)

        if not user:
            raise HTTPException(
                status_code=401, detail="Invalid username or password")

        return AuthResponse(
            success=True,
            message="Login successful",
            user_id=user.id,
            username=user.username
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{user_id}", response_model=UserSessions)
async def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
    """Get all diagnosis sessions for a user"""
    try:
        sessions = DatabaseService.get_user_sessions(db, user_id)

        session_list = []
        for session in sessions:
            messages = DatabaseService.get_session_messages(db, session.id)
            message_list = DatabaseService.convert_messages_to_schema(messages)

            session_history = SessionHistory(
                session_id=session.session_id,
                disease=session.disease,
                confidence=session.confidence,
                recommendations=session.recommendations,
                next_steps=session.next_steps,
                tips=session.tips,
                created_at=session.created_at.isoformat(),
                messages=message_list
            )
            session_list.append(session_history)

        return UserSessions(sessions=session_list)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_detail(session_id: str, db: Session = Depends(get_db)):
    """Get detailed info about a specific diagnosis session"""
    try:
        session = DatabaseService.get_diagnosis_session_by_session_id(
            db, session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        messages = DatabaseService.get_session_messages(db, session.id)
        message_list = DatabaseService.convert_messages_to_schema(messages)

        return SessionHistory(
            session_id=session.session_id,
            disease=session.disease,
            confidence=session.confidence,
            recommendations=session.recommendations,
            next_steps=session.next_steps,
            tips=session.tips,
            created_at=session.created_at.isoformat(),
            messages=message_list
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
