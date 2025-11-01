import google.generativeai as genai
from dotenv import load_dotenv
import os
import pathlib
from typing import List, Dict, Any, Optional

"""
Central module for all LLM operations in Career Compass.
Handles model initialization, chat interactions, prompts and tool definitions.
"""


def init_gemini_client():
    """
    Initialize the Google Generative AI client with API key.
    This should be called once at application startup or before using any Gemini features.
    """
    find_path = pathlib.Path(__file__).resolve()
    env_path = find_path.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # Fallback
        
    api_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not api_key:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in environment variables")
    
    genai.configure(api_key=api_key)
    print("Gemini client initialized")


def get_chat_model(model_name: str="gemini-2.5-flash",
                   system_instruction: Optional[str]=None,
                   tools: Optional[List]=None) -> genai.GenerativeModel:
    """
    Get a Gemini model instance for chat/completion tasks.
    Will add tools if needed.
    """
    init_gemini_client()    
    return genai.GenerativeModel(model_name)


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

CAREER_ADVISOR_SYSTEM_PROMPT = """
You are an expert career advisor specializing in career transitions.
Your role is to:
- Analyze users' backgrounds, skills, and experience
- Suggest realistic and achievable career paths
- Provide honest assessments of skill gaps and transition difficulty
- Recommend concrete learning resources and action plans
- Be encouraging yet realistic about timelines and challenges

Always provide actionable advice with specific next steps.
"""


RECOMMENDER_PROMPT = """
    {context}
    
    Based on this background, provide:
    1. Top 3-5 career paths that would be a good fit
    2. For each path, explain why it's a good match
    3. Key skills they already have for each path
    4. Skills they need to develop for each path
    5. Estimated transition difficulty (Easy/Medium/Hard)
    
    Format your response as JSON with this structure:
    {{
        "recommendations": [
            {{
                "career_title": "Career Name",
                "match_reason": "Why this is a good fit",
                "existing_skills": ["skill1", "skill2"],
                "skills_to_develop": ["skill1", "skill2"],
                "difficulty": "Medium",
                "salary_range": "Estimated range if known"
            }}
        ],
        "summary": "Overall assessment and advice"
    }}
    """


    
SKILL_ANALYZER_SYSTEM_PROMPT = """
You are a technical skill analyst with deep knowledge of various industries and roles.
Your role is to:
- Identify transferable skills across different careers
- Assess skill gaps objectively
- Recommend prioritized learning paths
- Estimate realistic timeframes for skill acquisition
- Suggest specific courses, projects, and resources

Be precise and data-driven in your assessments.
"""

RESUME_ANALYZER_SYSTEM_PROMPT = """
You are an expert resume analyst and career counselor.
Analyze resumes to extract:
- Core competencies and technical skills
- Soft skills and leadership qualities
- Career progression patterns
- Strengths and unique value propositions
- Potential career pivots based on background

Provide detailed, structured analysis.
"""
    
