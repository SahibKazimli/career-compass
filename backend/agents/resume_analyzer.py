import google.generativeai as genai
from backend.utils.llm import RESUME_ANALYZER_PROMPT
from typing import List, Dict, Tuple, Any, Optional
from sqlalchemy.orm import Session
from backend.db.database import Resume
from dotenv import load_dotenv
import os
import json

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))



def analyze_resume_deep(raw_text: str, sections: list) -> dict:
    """
    Deep analysis of resume to extract insights from already parsed sections.
    sections is the list you stored (chunks with {section, content, summary}).
    """
    
    # Keep prompt compact by limiting content length
    sections_text = "\n\n".join([
        f"Section: {sec.get('section')}\nSummary: {sec.get('summary')}\nContent (truncated): {sec.get('content','')[:800]}"
        for sec in sections[:5]
    ])

    user_prompt = f"""
    Analyze this resume in depth and return ONLY valid JSON with:
    - core_competencies (technical and soft skills)
    - career_progression_pattern
    - leadership_qualities
    - unique_value_proposition
    - potential_career_pivots (3-5)
    - strengths_to_leverage
    - areas_for_development
    - actionable_resume_improvements (bullet list)

    Resume context:
    {sections_text}
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=RESUME_ANALYZER_PROMPT
    )
    
    try:
        resp = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.6,
                response_mime_type="application/json"
            )
        )
        return json.loads(resp.text)
    except Exception as e:
        return {"error": str(e)}
    
    

