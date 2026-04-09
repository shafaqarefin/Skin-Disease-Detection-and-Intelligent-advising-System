from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.services.prediction_service import analyze_image
from app.services.llm_service import get_medical_advice, chat_about_diagnosis
from app.schemas.responses import AnalysisResponse, ErrorResponse, PredictionResponse, ChatRequest, ChatResponse
from app.schemas.auth import Message
from app.core.database import get_db
from app.services.database_service import DatabaseService
import uuid

router = APIRouter()


@router.post("/analyze_skin", response_model=AnalysisResponse, responses={400: {"model": ErrorResponse}})
async def analyze_skin_endpoint(file: UploadFile = File(...), user_id: int = Query(...), db: Session = Depends(get_db)):
    """Analyze skin image and create a diagnosis session with persistent storage."""
    try:
        # 1. Read the uploaded file
        contents = await file.read()

        # 2. Get prediction from CV model
        disease, confidence = analyze_image(contents)

        # 3. Get advice from LLM
        llm_advice = get_medical_advice(disease, confidence)

        # 4. Create unique session ID
        session_id = str(uuid.uuid4())

        # 5. Save to database
        db_session = DatabaseService.create_diagnosis_session(
            db=db,
            user_id=user_id,
            session_id=session_id,
            disease=disease,
            confidence=confidence,
            recommendations=llm_advice.get('recommendations'),
            next_steps=llm_advice.get('next_steps'),
            tips=llm_advice.get('tips'),
            system_context=llm_advice.get('system_context')
        )

        # 6. Return with session_id
        return AnalysisResponse(
            session_id=session_id,
            disease=disease,
            confidence=confidence,
            recommendations=llm_advice.get('recommendations'),
            next_steps=llm_advice.get('next_steps'),
            tips=llm_advice.get('tips'),
            system_context=llm_advice.get('system_context')
        )

    except Exception as e:
        # If anything fails, return a clean error message
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/classify_skin", response_model=PredictionResponse, responses={400: {"model": ErrorResponse}})
async def classify_skin_endpoint(file: UploadFile = File(...)):
    try:
        # 1. Read the uploaded file
        contents = await file.read()

        # 2. Get prediction from CV model
        disease, confidence = analyze_image(contents)

        # 3. Return formatted data matching the Pydantic schema
        return PredictionResponse(disease=disease, confidence=confidence)

    except Exception as e:
        # If anything fails, return a clean error message
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chat", response_model=ChatResponse, responses={400: {"model": ErrorResponse}})
async def chat_endpoint(chat_request: ChatRequest, db: Session = Depends(get_db)):
    """Multi-turn conversation endpoint. Maintains full chat history in database."""
    try:
        print(
            f"Chat request received - Session: {chat_request.session_id}, Message: {chat_request.message}")

        # Use history from request for backward compatibility, or fetch from DB if session_id provided
        history = chat_request.history if chat_request.history else []
        system_context = chat_request.system_context

        # If session_id is provided, fetch from database
        if chat_request.session_id:
            db_session = DatabaseService.get_diagnosis_session_by_session_id(
                db, chat_request.session_id)
            if not db_session:
                raise HTTPException(
                    status_code=404, detail="Diagnosis session not found")

            # Get existing messages from database
            db_messages = DatabaseService.get_session_messages(
                db, db_session.id)
            history = DatabaseService.convert_messages_to_schema(db_messages)
            system_context = db_session.system_context

        # Generate response using LLM
        response_text, updated_history = chat_about_diagnosis(
            disease=chat_request.disease,
            confidence=chat_request.confidence,
            user_message=chat_request.message,
            history=history,
            system_context=system_context
        )

        # Save to database if session_id provided
        if chat_request.session_id:
            db_session = DatabaseService.get_diagnosis_session_by_session_id(
                db, chat_request.session_id)
            if db_session:
                # Save user message to database
                DatabaseService.add_chat_message(
                    db, db_session.id, "user", chat_request.message)

                # Save assistant response to database
                DatabaseService.add_chat_message(
                    db, db_session.id, "assistant", response_text)

        print(
            f"Chat response generated successfully. History length: {len(updated_history)}")
        return ChatResponse(response=response_text, history=updated_history)

    except HTTPException:
        raise
    except Exception as e:
        error_detail = str(e)
        print(f"Chat endpoint error: {error_detail}")
        raise HTTPException(status_code=400, detail=error_detail)
