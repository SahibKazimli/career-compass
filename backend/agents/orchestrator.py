import json
from backend.db.events import publish_event, append_run_state, mark_run_status
from backend.parsing.parsing_helpers import parse_upload
from backend.agents.resume_analyzer import analyze_resume_deep
from backend.agents.recommender import generate_recommendations
from backend.agents.skills_agent import analyze_skills  
from typing import Dict, Any, List, Tuple, Optional
from backend.db.events import create_run, update_run_state, fetch_run
from backend.db.pg_vectors import fetch_latest_resume



    