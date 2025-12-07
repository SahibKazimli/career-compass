import os
import json
from typing import Dict, Any

from backend.db.pg import get_conn
from backend.parsing.resume_parser import genai_parse_pdf
from backend.utils.embeddings import embed_resume_chunks
from backend.db.pg_vectors import insert_resume_with_chunks
from backend.agents.recommender import generate_recommendations
from backend.db.recommendations import save_recommendations

class Orchestrator:
    """
    Coordinates the AI agents to process a user's career transition.
    Triggered directly by API background tasks.
    """

    def run_resume_workflow(self, user_id: int, file_path: str, original_filename: str):
        """
        Full pipeline: Parse PDF -> Save to DB -> Generate Recommendations
        """
        # Get a dedicated connection for this background run
        conn_gen = get_conn()
        conn = next(conn_gen)
        
        try:
            print(f"[Orchestrator] Starting workflow for user {user_id}...")

            # 1. PARSE & EMBED
            # ---------------------------------------------------------
            print(f"[Orchestrator] Parsing resume: {original_filename}")
            parsed_resume = genai_parse_pdf(file_path, original_filename)
            embedded_resume = embed_resume_chunks(parsed_resume)
            
            # Extract high-level fields for the resume table
            skills = []
            experience = []
            for chunk in embedded_resume['chunks']:
                sec_lower = chunk['section'].lower()
                if 'skill' in sec_lower:
                    skills.append(chunk['content'])
                if any(x in sec_lower for x in ['work', 'experience']):
                    experience.append(chunk['content'])

            # 2. SAVE TO DB
            # ---------------------------------------------------------
            print(f"[Orchestrator] Saving resume to database...")
            insert_resume_with_chunks(
                conn=conn,
                user_id=user_id,
                raw_text="Parsed from PDF",
                parsed_skills_text=json.dumps(skills),
                parsed_experience_text=json.dumps(experience),
                chunks=embedded_resume["chunks"]
            )

            # 3. RECOMMENDATIONS AGENT
            # ---------------------------------------------------------
            print(f"[Orchestrator] Generating career recommendations...")
            recs = generate_recommendations(conn, user_id)
            
            save_recommendations(conn, user_id, recs)
            print(f"[Orchestrator] Workflow complete for user {user_id}.")

        except Exception as e:
            print(f"[Orchestrator] CRITICAL ERROR: {e}")
        finally:
            conn.close()
            if os.path.exists(file_path):
                os.remove(file_path)