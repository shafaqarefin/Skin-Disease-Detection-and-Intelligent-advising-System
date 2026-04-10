"""
Chat Prompt Templates for Multi-turn Conversations
"""

from typing import Optional, List


def format_conversation_history(messages: Optional[List]) -> str:
    """
    Format conversation history into readable text.
    
    Converts a list of message objects into a formatted string showing
    the conversation between patient and assistant.
    
    Args:
        messages: List of message objects with role and content attributes
                 (can be Message objects or dicts with 'role' and 'content' keys)
    
    Returns:
        Formatted conversation history string, or empty string if no messages
    """
    if not messages or len(messages) == 0:
        return ""
    
    conversation_context = "\n\n=== CONVERSATION HISTORY ===\n"
    
    for msg in messages:
        # Handle both Message objects and dicts
        if hasattr(msg, 'role'):
            role_str = msg.role
            content_str = msg.content
        else:
            role_str = msg.get('role', 'unknown')
            content_str = msg.get('content', '')
        
        role = "Patient" if role_str == "user" else "Assistant"
        conversation_context += f"\n{role}: {content_str}"
    
    conversation_context += "\n\n=== END HISTORY ===\n"
    
    return conversation_context


def get_chat_prompt(
    system_context: str,
    conversation_history: str,
    user_message: str
) -> str:
    """
    Generate chat prompt for multi-turn conversation.
    
    Combines system context, conversation history, and current user message
    into a comprehensive prompt for the LLM.
    
    Args:
        system_context: System role and diagnosis context
        conversation_history: Formatted conversation history (from format_conversation_history)
        user_message: Current user message/question
    
    Returns:
        Formatted prompt string for LLM
    """
    prompt = f"""{system_context}
{conversation_history}
Patient's current message: {user_message}

Provide a helpful response to their message. Keep it concise and practical."""
    return prompt.strip()
