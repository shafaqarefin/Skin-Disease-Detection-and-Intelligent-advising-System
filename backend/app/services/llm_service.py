import google.generativeai as genai
import json
from app.core.config import settings
from typing import List, Optional
from app.schemas.responses import Message
from app.prompts.analysis_prompt import get_analysis_prompt, get_system_context
from app.prompts.chat_prompt import get_chat_prompt, format_conversation_history

genai.configure(api_key=settings.GEMINI_API_KEY)
llm = genai.GenerativeModel(settings.LLM_MODEL)


def get_medical_advice(disease: str, confidence: float) -> dict:
    """Sends the CV prediction to Gemini and returns structured advice with system context for chatting."""

    # Get prompt from prompts folder
    prompt = get_analysis_prompt(disease, confidence)
    
    response = llm.generate_content(prompt)

    # Clean the response in case Gemini includes markdown code blocks
    clean_json_string = response.text.replace(
        "```json", "").replace("```", "").strip()

    # Convert string to Python dictionary
    result = json.loads(clean_json_string)

    # Add system context for subsequent multi-turn conversation
    result["system_context"] = get_system_context(disease, confidence)

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
        conversation_context = format_conversation_history(history)

        # Use the system context if provided, otherwise create a default one
        if not system_context:
            system_context = get_system_context(disease, confidence)

        # Get prompt from prompts folder
        prompt = get_chat_prompt(system_context, conversation_context, user_message)

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
