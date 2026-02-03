"""
Career Matcher Agent for Career Compass.
Uses AI to match user profiles to career paths and provide detailed transition plans.
"""

import json
import google.generativeai as genai


CAREER_MATCHER_SYSTEM_PROMPT = """
You are an expert career counselor and labor market analyst with deep knowledge of:
- Industry trends and emerging roles
- Career transition pathways
- Skill transferability across industries
- Salary ranges and job market demand
- Required qualifications and common career ladders

Your role is to:
- Match user profiles to suitable career paths
- Provide realistic assessments of transition difficulty
- Identify transferable skills and experience
- Create actionable transition roadmaps
- Consider both traditional and non-traditional career paths

Be honest about challenges while remaining encouraging. 
Provide data-driven insights when possible.
"""


def match_careers(
    skills: list,
    experience_summary: str = None,
    current_role: str = None,
    interests: list = None,
    education: str = None,
    constraints: dict = None
) -> dict:
    """
    Match user profile to potential careers with detailed analysis.
    
    Args:
        skills: List of user's skills
        experience_summary: Brief summary of work experience
        current_role: User's current job title
        interests: List of user's career interests
        education: Educational background
        constraints: Optional constraints (location, remote preference, etc.)
    
    Returns:
        Dict with matched careers and transition plans
    """
    
    # Handle both string lists and dict lists
    def extract_text_from_item(item, keys=["skill", "name", "title", "value", "interest"]):
        if isinstance(item, str):
            return item
        elif isinstance(item, dict):
            for key in keys:
                if key in item:
                    return str(item[key])
            return str(item)
        else:
            return str(item)
    
    skills_text = ", ".join([extract_text_from_item(s) for s in skills]) if skills else "Not specified"
    interests_text = ", ".join([extract_text_from_item(i, ["interest", "name", "title", "value"]) for i in interests]) if interests else "Open to exploration"
    
    user_prompt = f"""
Analyze this professional profile and recommend career matches:

**Current Role:** {current_role or "Not specified"}

**Skills:**
{skills_text}

**Experience:**
{experience_summary or "Not provided"}

**Education:** {education or "Not specified"}

**Interests:** {interests_text}

**Constraints:** {json.dumps(constraints) if constraints else "None specified"}

Provide 5-7 career path recommendations, ranging from:
- Direct transitions (high compatibility)
- Stretch roles (moderate effort required)
- Career pivots (significant transition required)

For each career, provide:
1. Match score (0-100)
2. Why this is a good match
3. Transferable skills from current profile
4. Skills gaps to fill
5. Typical transition timeline
6. Salary range expectations
7. Job market demand (Hot/Warm/Cool)
8. First 3 steps to pursue this path

Return as JSON:
{{
  "profile_summary": "Brief assessment of the candidate's profile",
  "career_matches": [
    {{
      "title": "Career Title",
      "match_score": 85,
      "match_type": "direct|stretch|pivot",
      "match_reason": "Why this career fits",
      "industry": "industry name",
      "transferable_skills": ["skill1", "skill2"],
      "skills_to_acquire": ["skill1", "skill2"],
      "experience_leverage": "How current experience helps",
      "transition_timeline": "X-Y months",
      "salary_range": {{
        "entry": "$X-$Y",
        "mid": "$X-$Y", 
        "senior": "$X-$Y"
      }},
      "job_market_demand": "Hot|Warm|Cool",
      "growth_outlook": "Description of career growth potential",
      "first_steps": [
        {{"step": 1, "action": "What to do", "timeline": "When"}},
        {{"step": 2, "action": "What to do", "timeline": "When"}},
        {{"step": 3, "action": "What to do", "timeline": "When"}}
      ],
      "success_stories": "Brief example or archetype of successful transition"
    }}
  ],
  "recommended_focus": "Which 2-3 careers to prioritize and why",
  "quick_wins": ["Immediate actions that apply to multiple career paths"],
  "skills_with_highest_roi": ["Skills that unlock the most opportunities"]
}}
"""
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=CAREER_MATCHER_SYSTEM_PROMPT
    )
    
    try:
        response = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.6,
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error matching careers: {e}")
        return {
            "error": str(e),
            "career_matches": [],
            "raw_response": str(response.text) if 'response' in locals() else None
        }


def get_transition_roadmap(
    current_role: str,
    target_role: str,
    current_skills: list,
    timeline: str = "6-12 months"
) -> dict:
    """
    Generate a detailed transition roadmap between two specific roles.
    
    Args:
        current_role: User's current position
        target_role: Desired career goal
        current_skills: User's existing skills
        timeline: Desired transition timeline
    """
    
    skills_text = ", ".join(current_skills) if current_skills else "Not specified"
    
    user_prompt = f"""
Create a detailed transition roadmap:

**From:** {current_role}
**To:** {target_role}
**Timeline:** {timeline}
**Current Skills:** {skills_text}

Provide a month-by-month action plan including:
- Skills to learn (in order)
- Resources to use
- Projects to build
- Networking actions
- Application strategy
- Interview preparation

Return as JSON:
{{
  "transition_summary": "Overview of the transition",
  "feasibility_score": 85,
  "monthly_plan": [
    {{
      "month": 1,
      "theme": "Phase theme",
      "goals": ["goal1", "goal2"],
      "actions": [
        {{"action": "What to do", "time_commitment": "X hours/week", "resources": ["resource1"]}}
      ],
      "milestones": ["What success looks like"]
    }}
  ],
  "critical_skills": ["Most important skills to acquire"],
  "portfolio_projects": [
    {{"name": "project name", "description": "what to build", "skills_demonstrated": ["skill1"]}}
  ],
  "networking_strategy": "How to build connections in target field",
  "common_pitfalls": ["What to avoid"],
  "success_indicators": ["How to know you're on track"]
}}
"""
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=CAREER_MATCHER_SYSTEM_PROMPT
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
        print(f"Error generating roadmap: {e}")
        return {
            "error": str(e),
            "transition_summary": "Error generating roadmap",
            "monthly_plan": []
        }
