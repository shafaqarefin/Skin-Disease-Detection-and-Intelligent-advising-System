from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.prediction_service import analyze_image
from app.services.llm_service import get_medical_advice, chat_about_diagnosis
from app.schemas.responses import AnalysisResponse, ErrorResponse, PredictionResponse, ChatRequest, ChatResponse

router = APIRouter()


@router.post("/analyze_skin", response_model=AnalysisResponse, responses={400: {"model": ErrorResponse}})
async def analyze_skin_endpoint(file: UploadFile = File(...)):
    try:
        # 1. Read the uploaded file
        contents = await file.read()

        # 2. Get prediction from CV model
        disease, confidence = analyze_image(contents)

        # 3. Get advice from LLM
        llm_advice = get_medical_advice(disease, confidence)

        # 4. Return formatted data matching the Pydantic schema
        return AnalysisResponse(**llm_advice)

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
async def chat_endpoint(chat_request: ChatRequest):
    """Chat with the LLM about a diagnosed skin condition."""
    try:
        print(
            f"Chat request received - Disease: {chat_request.disease}, Message: {chat_request.message}")

        response = chat_about_diagnosis(
            disease=chat_request.disease,
            confidence=chat_request.confidence,
            user_message=chat_request.message
        )

        print(f"Chat response generated successfully")
        return ChatResponse(response=response)

    except Exception as e:
        error_detail = str(e)
        print(f"Chat endpoint error: {error_detail}")
        raise HTTPException(status_code=400, detail=error_detail)
