import os
import json
import asyncio
from typing import Dict, Any

from backend.db.pg import get_conn
from backend.parsing.resume_parser import genai_parse_pdf
from backend.utils.embeddings import embed_resume_chunks
from backend.db.pg_vectors import insert_resume_with_chunks

from backend.agents.recommender import generate_recommendations
from backend.agents.skills_agent import analyze_skills 
from backend.db.recommendations import save_recommendations

class Orchestrator:
    """
    Async Orchestrator.
    Manages the workflow and runs agents in parallel where possible.
    """

    async def run_resume_workflow(self, user_id: int, file_path: str, original_filename: str):
        # We need a synchronous connection for the DB parts, 
        # or we treat DB calls as blocking blocks within the async flow.
        conn_gen = get_conn()
        conn = next(conn_gen)
        
        try:
            print(f"[Orchestrator] 1. Parsing Resume...")
            # Ideally, make genai_parse_pdf async, but for now we can run it in a thread
            # to avoid blocking the main event loop if other requests come in
            parsed_resume = await asyncio.to_thread(genai_parse_pdf, file_path, original_filename)
            
            print(f"[Orchestrator] 2. Embedding & Saving...")
            embedded_resume = await asyncio.to_thread(embed_resume_chunks, parsed_resume)
            
            # Extract fields for DB
            skills = []
            experience = []
            for chunk in embedded_resume['chunks']:
                if 'skill' in chunk['section'].lower():
                    skills.append(chunk['content'])
                if any(x in chunk['section'].lower() for x in ['work', 'experience']):
                    experience.append(chunk['content'])

            # DB Write (Sync)
            insert_resume_with_chunks(
                conn=conn,
                user_id=user_id,
                raw_text="Parsed from PDF",
                parsed_skills_text=json.dumps(skills),
                parsed_experience_text=json.dumps(experience),
                chunks=embedded_resume["chunks"]
            )

            # 3. PARALLEL AGENT EXECUTION
            print(f"[Orchestrator] 3. Running Agents in Parallel...")
            
            # We define tasks to run simultaneously
            # TODO: Need to update these functions to async or wrap them
            task_recommend = asyncio.to_thread(generate_recommendations, conn, user_id)
            task_skills    = asyncio.to_thread(analyze_skills, skills) # Example of a second agent

            # Wait for both to finish
            recommendations, skills_analysis = await asyncio.gather(task_recommend, task_skills)
            
            # 4. Save Results
            save_recommendations(conn, user_id, recommendations)
            
            print(f"[Orchestrator] Workflow complete. Agents finished.")

        except Exception as e:
            print(f"[Orchestrator] Error: {e}")
        finally:
            conn.close()
            if os.path.exists(file_path):
                os.remove(file_path)