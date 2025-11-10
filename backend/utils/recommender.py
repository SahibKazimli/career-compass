import json
import re
from typing import List, Dict, Tuple, Any, Optional
from sqlalchemy.orm import Session
from db.database import Resume
from llm import RECOMMENDER_PROMPT, get_chat_model



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
    summaries: List[tuple[str, str]] = []
    for ch in chunks[:max_sections]:
        section = ch.get("section", "Section")
        summary = ch.get("summary")
        content = ch.get("content", "")
        text = (summary or content) or ""
        if len(text) > max_chars_per_section:
            text = text[:max_chars_per_section] + "…"
        summaries.append((section, text))
    return summaries


def build_recommendations_prompt(
    skills: List[str],
    experience: List[str],
    chunk_summaries: List[Tuple[str, str]],
    user_interests: Optional[str] = None, 
    current_role: Optional[str] = None
) -> str: 
    """
    Constructs a compact, structured prompt for recommendations.
    Embeddings are NOT included to keep tokens/cost low.
    """
    skills_block = "\n".join(f"- {skill}" for skill in skills) if skills else "None"
    exp_block = "\n".join(f"- {e}" for e in experience) if experience else "None"

    sections_block = "\n".join(
        f"- {sec}: {txt}" for (sec, txt) in chunk_summaries
    ) if chunk_summaries else "None"

    interests = user_interests or "Not specified"
    role = current_role or "Not specified"
    
    return RECOMMENDER_PROMPT.format(
        role=role,
        skills_block=skills_block,
        exp_block=exp_block,
        sections_block=sections_block,
        interests=interests
    )   
        
        
        
def load_resume_data_from_db(db: Session, user_id: int) -> Dict[str, Any]:
    """Load the latest parsed resume for a user from DB."""
    resume_row = (
        db.query(Resume)
          .filter(Resume.user_id == user_id)
          .order_by(Resume.id.desc())
          .first()
    )
    
    if not resume_row:
        raise ValueError(f"No resume found for user {user_id}")
    
    skills = _json_load_safe(resume_row.parsed_skills, default=[])
    experience = _json_load_safe(resume_row.parsed_experience, default=[])
    chunks = _json_load_safe(resume_row.embedding, default=[])
    
    return {"skills": skills, "experience": experience, "chunks": chunks}
        

def generate_recommendations(
    db: Session,
    user_id: int,
    user_interests: Optional[str] = None, 
    current_role: Optional[str] = None,
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
    
    resume_data = load_resume_data_from_db(db, user_id)
    
    # Assemble prompt 
    chunk_summaries = summarize_chunks(resume_data["chunks"])
    prompt = build_recommendations_prompt(
        skills=resume_data["skills"],
        experience=resume_data["experience"],
        chunk_summaries=chunk_summaries,
        user_interests=user_interests,
        current_role=current_role
    )
        
    model = get_chat_model(model_name)
    response = model.generate_content(prompt)
    return response
    
    
    
    