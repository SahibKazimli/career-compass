import json
import re
from typing import List, Dict, Tuple, Any, Optional
from psycopg import Connection

from backend.db.pg_vectors import fetch_latest_resume, fetch_resume_chunks
from backend.utils.llm import RECOMMENDER_PROMPT, get_chat_model, summarize_chunks, _json_load_safe




def build_recommendations_prompt(
    skills: List[str],
    experience: List[str],
    chunk_summaries: List[Tuple[str, str]],
    user_interests: Optional[str] = None, 
    current_role: Optional[str] = None
) -> str: 
    """
    Constructs a compact, structured prompt for recommendations.
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
        
        
        
def load_resume_data_from_db(conn: Connection, user_id: int) -> Dict[str, Any]:
    """Load the latest parsed resume for a user from DB."""
    resume_row = fetch_latest_resume(conn, user_id)
    if not resume_row:
        raise ValueError(f"No resume found for user {user_id}")
    
    # In pg_vectors.fetch_latest_resume, parsed_skills / parsed_experience are text/json strings
    skills = _json_load_safe(resume_row.parsed_skills, default=[])
    experience = _json_load_safe(resume_row.parsed_experience, default=[])
    
    resume_id = resume_row.get("resume_id") or resume_row.get("id")
    chunks = fetch_resume_chunks(conn, resume_id=resume_id)
    
    return {"skills": skills, "experience": experience, "chunks": chunks}


def _extract_json(text: str) -> Optional[dict]:
    """Extract JSON from LLM response, handling markdown fences."""
    if not text:
        return None
    
    try:
        return json.loads(text)
    except:
        pass
    
    # Try extracting from ```json``` fences
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    
    return None
        

def generate_recommendations(
    conn: Connection,
    user_id: int,
    user_interests: Optional[str] = None, 
    current_role: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Generate personalized career path recommendations based on resume data.

    Uses raw Postgres connection and pgvector-backed tables.
    """
    
    resume_data = load_resume_data_from_db(conn, user_id)
    
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
    
    parsed_response = _extract_json(getattr(response, "text", ""))
    if not parsed_response: 
        return {
            "recommendations": [],
            "overall_assessment": "",
            "raw_response": getattr(response, "text", ""),
            "model_used": model_name
        }
    
    parsed_response["model_used"] = model_name
    return parsed_response
    
    
    