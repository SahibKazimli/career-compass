import json
from backend.utils.llm import SKILL_ANALYZER_SYSTEM_PROMPT
import google.generativeai as genai



def analyze_skills(skills: list, target_role: str = None) -> dict:
    """
    Analyze user's skills and identify gaps for a target role
    """
    skills_text = ", ".join(skills)
    
    if target_role:
        user_prompt = f"""
Analyze these skills for someone targeting a {target_role} role:
{skills_text}

Provide:
1. Transferable skills that apply to {target_role}
2. Skills gaps that need to be filled
3. Prioritized learning path (what to learn first)
4. Estimated timeframe for skill acquisition
5. Specific resources (courses, projects, certifications)

Return as JSON:
{{
  "transferable_skills": ["skill1", "skill2"],
  "skill_gaps": ["gap1", "gap2"],
  "learning_path": [
    {{"skill": "skill_name", "priority": "High|Medium|Low", "timeframe": "X weeks/months"}}
  ],
  "recommended_resources": [
    {{"skill": "skill_name", "resources": ["resource1", "resource2"]}}
  ],
  "overall_readiness": "string describing readiness for target role"
}}
"""
    else:
        user_prompt = f"""
Analyze these skills:
{skills_text}

Return as JSON with:
- core_technical_skills
- soft_skills
- leadership_skills
- standout_skills
- skills_to_strengthen
- potential_career_directions
"""
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SKILL_ANALYZER_SYSTEM_PROMPT
    )
    
    try:
        response = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.5,
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error analyzing skills: {e}")
        return {
            "error": str(e),
            "raw_response": str(response.text) if 'response' in locals() else None
        }