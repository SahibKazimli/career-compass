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
User Background:
- Current Role: {role}

Skills:
{skills_block}

Experience:
{exp_block}

Resume Sections (summaries):
{sections_block}

User Interests:
{interests}

Based on the above, recommend 3-5 realistic career paths. For each:
- title
- match_reason (tie to their background)
- relevant_existing_skills
- skills_to_develop
- transition_difficulty (Easy/Medium/Hard)
- estimated_salary_range (rough)
- first_steps (3 concrete actions)

Return STRICT JSON only in this schema:
{{
  "recommendations": [
    {{
      "title": "string",
      "match_reason": "string",
      "relevant_existing_skills": ["string"],
      "skills_to_develop": ["string"],
      "transition_difficulty": "Easy|Medium|Hard",
      "estimated_salary_range": "string",
      "first_steps": ["string", "string", "string"]
    }}
  ],
  "overall_assessment": "string"
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
    