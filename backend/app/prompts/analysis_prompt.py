"""
Analysis Prompt Templates for Initial Skin Disease Diagnosis
"""


def get_analysis_prompt(disease: str, confidence: float) -> str:
    """
    Generate initial analysis prompt for Gemini LLM.
    
    This prompt is used when the CV model first detects a skin disease.
    It asks the LLM to provide structured medical information.
    
    Args:
        disease: The detected disease name from CV model
        confidence: Confidence score from CV model (0-1)
    
    Returns:
        Formatted prompt string for LLM
    """
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
    return prompt.strip()


def get_system_context(disease: str, confidence: float) -> str:
    """
    Generate system context for multi-turn conversations.
    
    This context is set once during initial analysis and used for all subsequent
    chat messages in that conversation to maintain consistency.
    
    Args:
        disease: The diagnosed disease
        confidence: Confidence score of diagnosis (0-1)
    
    Returns:
        System context string to guide chat messages
    """
    system_context = f"""You are an expert AI dermatology assistant. A patient has been diagnosed with '{disease}' (confidence: {confidence:.2f}) from a skin image analysis. 

You will have access to the full conversation history. Maintain consistency with previous responses and provide helpful, accurate medical information. Always encourage the patient to consult a dermatologist for professional medical advice."""
    return system_context
