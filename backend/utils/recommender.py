import google.generativeai as genai 
from llm import RECOMMENDER_PROMPT, get_chat_model
from typing import Dict, Any, Optional
import json



def _json_load_safe(value: Optional[str], default):
    """
    Safely json.loads() a DB Text field, returning a default on error/None.
    """
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def generate_recommendations(
    resume_data: Dict[str, Any],
    user_interests: Optional[str] = None, 
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Generate personalized career path recommendations based on resume data.
    
    Args:
        resume_data: Parsed resume data with skills, experience, chunks
        user_interests: Optional user-provided career interests/goals
        model_name: The Gemini model to use
        
    Returns:
        Dictionary with career recommendations and reasoning
    """
    
    model = get_chat_model(model_name)
    
    # Build context and parse resume
    
    