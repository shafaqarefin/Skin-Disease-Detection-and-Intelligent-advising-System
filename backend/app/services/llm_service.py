import google.generativeai as genai
import json
from app.core.config import settings

# Configure the SDK with the secure key
genai.configure(api_key=settings.GEMINI_API_KEY)
llm = genai.GenerativeModel('models/gemini-2.5-flash')


def get_medical_advice(disease: str, confidence: float) -> dict:
    """Sends the CV prediction to Gemini and returns structured advice."""

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
    return json.loads(clean_json_string)


def chat_about_diagnosis(disease: str, confidence: float, user_message: str) -> str:
    """Chat with the LLM about the diagnosed condition."""

    try:
        prompt = f"""
You are an expert AI dermatology assistant. A patient has been diagnosed with '{disease}' 
(confidence: {confidence:.2f}) from a skin image analysis.

The patient has asked: {user_message}

Provide helpful, accurate medical information about their condition in response to their question.
Keep responses concise and practical. Always remind them to consult a dermatologist for professional medical advice.
        """

        response = llm.generate_content(prompt)

        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "Unable to generate response. Please try again."

    except Exception as e:
        print(f"Error in chat_about_diagnosis: {str(e)}")
        raise Exception(f"Chat error: {str(e)}")
