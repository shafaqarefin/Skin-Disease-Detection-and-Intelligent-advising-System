import google.generativeai as genai
import json
from app.core.config import settings
from typing import List, Optional
from app.schemas.responses import Message

genai.configure(api_key=settings.GEMINI_API_KEY)
llm = genai.GenerativeModel(settings.LLM_MODEL)


def get_medical_advice(disease: str, confidence: float) -> dict:
    """Sends the CV prediction to Gemini and returns structured advice with system context for chatting."""

    prompt = f"""
    You are an expert AI dermatology assistant. A computer vision model has detected '{disease}' 
    with a confidence of {confidence:.2f} on a user's skin. 
    
    Provide a JSON response with EXACTLY this structure. All values must be strings. Do not include markdown formatting, code blocks, or the word 'json'. Return valid JSON only:
    {{
        "disease": "{disease}",
        "confidence": {confidence:.2f},
        "recommendations": "Brief 2-sentence explanation of the condition and symptoms",
        "next_steps": "Specific guidance on what to do next, such as consulting a dermatologist or using recommended treatments",
        "tips": "Provide 2-3 practical daily skincare tips as a single string, separated by periods or bullet points. Keep it concise."
    }}
    
    IMPORTANT: Ensure tips is a STRING, not an array or list. Combine all tips into one continuous text string.
    """

    response = llm.generate_content(prompt)

    # Clean the response in case Gemini includes markdown code blocks
    clean_json_string = response.text.replace(
        "```json", "").replace("```", "").strip()

    # Convert string to Python dictionary
    result = json.loads(clean_json_string)

    # Add system context for subsequent multi-turn conversation
    result["system_context"] = f"""You are an expert AI dermatology assistant. A patient has been diagnosed with '{disease}' (confidence: {confidence:.2f}) from a skin image analysis. 

You will have access to the full conversation history. Maintain consistency with previous responses and provide helpful, accurate medical information. Always encourage the patient to consult a dermatologist for professional medical advice."""

    return result


def chat_about_diagnosis(disease: str, confidence: float, user_message: str, history: Optional[List[Message]] = None, system_context: str = None) -> tuple:
    """Multi-turn conversation chat with full conversation history tracking.

    Maintains complete conversation history and uses system role for context.

    Args:
        disease: The diagnosed disease
        confidence: Confidence level of the diagnosis
        user_message: The current user message
        history: Previous messages in the conversation (from temporary session memory)
        system_context: System role that was set during analysis

    Returns:
        Tuple of (response_text, updated_history)
    """

    try:
        # Build full conversation context from temporary history
        conversation_context = ""
        if history and len(history) > 0:
            conversation_context = "\n\n=== CONVERSATION HISTORY ===\n"
            for msg in history:
                role = "Patient" if msg.role == "user" else "Assistant"
                conversation_context += f"\n{role}: {msg.content}"
            conversation_context += "\n\n=== END HISTORY ===\n"

        # Use the system context if provided, otherwise create a default one
        if not system_context:
            system_context = f"""You are an expert AI dermatology assistant. A patient has been diagnosed with '{disease}' (confidence: {confidence:.2f}) from a skin image analysis. 

You will have access to the full conversation history. Maintain consistency with previous responses and provide helpful, accurate medical information. Always encourage the patient to consult a dermatologist for professional medical advice."""

        prompt = f"""{system_context}
{conversation_context}
Patient's current message: {user_message}

Provide a helpful response to their message. Keep it concise and practical."""

        response = llm.generate_content(prompt)

        if response and hasattr(response, 'text'):
            response_text = response.text

            # Update history with new user message and assistant response
            # Always initialize as list if None
            updated_history = list(history) if history else []

            # Append user message
            updated_history.append(Message(role="user", content=user_message))

            # Append assistant response
            updated_history.append(
                Message(role="assistant", content=response_text))

            return response_text, updated_history
        else:
            raise Exception("Unable to generate response. Please try again.")

    except Exception as e:
        print(f"Error in chat_about_diagnosis: {str(e)}")
        raise Exception(f"Chat error: {str(e)}")
