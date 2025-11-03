import google.generativeai as genai 
from llm import RECOMMENDER_PROMPT, get_chat_model
from typing import List, Dict, Tuple, Any, Optional
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


def summarize_chunks(chunks: List[Dict[str, Any]], max_sections: int=6, max_chars_per_section = 700) -> List[Tuple[str, str]]:
    """
    Make chunk content compact for the LLM prompt.
    Prefer each chunk's summary if present; otherwise truncate content.
    """
    summaries = List[tuple[str, str]] = []
    for ch in chunks[:max_sections]:
        section = ch.get("section", "Section")
        summary = ch.get("summary")
        content = ch.get("content", "")
        text = (summary or content) or ""
        if len(text) > max_chars_per_section:
            text = text[:max_chars_per_section] + "…"
        summaries.append((section, text))
    return summaries

        

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
    
    