"""
Resources Agent for Career Compass.
Uses AI to generate personalized learning resources based on user skills and gaps.
"""

import json
import google.generativeai as genai


RESOURCES_AGENT_SYSTEM_PROMPT = """
You are a learning resources specialist with extensive knowledge of:
- Online learning platforms (Coursera, Udemy, edX, LinkedIn Learning, Pluralsight)
- Free resources (YouTube channels, documentation, open-source projects)
- Books and publications
- Certifications and their value in the job market
- Hands-on project ideas for skill development

Your role is to recommend specific, actionable learning resources tailored to:
- The user's current skill level
- Their target career direction
- Available time commitment
- Learning style preferences

Always provide real, verifiable resources with specific course/resource names.
Prioritize free resources when available, but include premium options with clear value propositions.
"""


def generate_learning_resources(
    skills_to_develop: list,
    current_skills: list = None,
    target_role: str = None,
    time_commitment: str = "medium"  # low, medium, high
) -> dict:
    """
    Generate personalized learning resources based on skill gaps.
    
    Args:
        skills_to_develop: List of skills the user needs to learn/improve
        current_skills: List of user's existing skills (for context)
        target_role: Optional target career role
        time_commitment: User's available time (low/medium/high)
    
    Returns:
        Dict with categorized learning resources
    """
    
    skills_text = ", ".join(skills_to_develop) if skills_to_develop else "general career development"
    current_text = ", ".join(current_skills) if current_skills else "not specified"
    
    user_prompt = f"""
Generate a comprehensive learning plan for the following:

**Skills to Develop:**
{skills_text}

**Current Skills (for context):**
{current_text}

**Target Role:** {target_role or "General career advancement"}

**Time Commitment:** {time_commitment} (affects resource recommendations)

For each skill to develop, provide:
1. Free resources (YouTube, docs, tutorials)
2. Premium courses (Coursera, Udemy, etc.) with specific course names
3. Books or publications
4. Hands-on project ideas
5. Estimated time to proficiency
6. Recommended certifications (if applicable)

Return as JSON:
{{
  "learning_plan": [
    {{
      "skill": "skill_name",
      "priority": "High|Medium|Low",
      "estimated_time": "X weeks/months",
      "resources": {{
        "free": [
          {{"name": "resource_name", "url": "url_or_description", "type": "video|article|docs|tutorial", "description": "brief description"}}
        ],
        "premium": [
          {{"name": "course_name", "platform": "platform_name", "price_range": "$X-$Y", "description": "brief description"}}
        ],
        "books": [
          {{"title": "book_title", "author": "author_name", "description": "why this book"}}
        ],
        "projects": [
          {{"name": "project_idea", "difficulty": "beginner|intermediate|advanced", "description": "what you'll build"}}
        ],
        "certifications": [
          {{"name": "cert_name", "issuer": "issuer", "value": "why it matters"}}
        ]
      }}
    }}
  ],
  "recommended_learning_path": [
    {{"order": 1, "skill": "skill_name", "duration": "X weeks", "reason": "why learn this first"}}
  ],
  "weekly_schedule": {{
    "low_commitment": "X hours/week - brief description of approach",
    "medium_commitment": "X hours/week - brief description",
    "high_commitment": "X hours/week - brief description"
  }},
  "quick_wins": ["skill or resource for immediate progress"],
  "summary": "Overall learning strategy summary"
}}
"""
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=RESOURCES_AGENT_SYSTEM_PROMPT
    )
    
    try:
        response = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error generating resources: {e}")
        return {
            "error": str(e),
            "learning_plan": [],
            "raw_response": str(response.text) if 'response' in locals() else None
        }


def get_resources_for_skill(skill: str, depth: str = "comprehensive") -> dict:
    """
    Get detailed resources for a single skill.
    
    Args:
        skill: The skill to find resources for
        depth: "quick" for brief list, "comprehensive" for detailed plan
    """
    
    user_prompt = f"""
Provide {"a quick list of top 5" if depth == "quick" else "comprehensive"} learning resources for: {skill}

{"Return as JSON with: name, type, url, description" if depth == "quick" else "Include free resources, courses, books, projects, and certifications"}

Return as JSON:
{{
  "skill": "{skill}",
  "resources": [
    {{"name": "name", "type": "type", "url_or_info": "url/description", "description": "why useful", "difficulty": "beginner|intermediate|advanced"}}
  ],
  "best_starting_point": "recommendation for where to begin",
  "estimated_proficiency_time": "X weeks/months"
}}
"""
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=RESOURCES_AGENT_SYSTEM_PROMPT
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
        print(f"Error getting resources for {skill}: {e}")
        return {"error": str(e), "skill": skill, "resources": []}
