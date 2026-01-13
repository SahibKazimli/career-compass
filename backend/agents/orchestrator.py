import os
import json
import asyncio
from typing import Dict, Any
from datetime import datetime

from backend.db.pg import get_conn
from backend.parsing.resume_parser import genai_parse_pdf
from backend.utils.embeddings import embed_resume_chunks
from backend.db.pg_vectors import insert_resume_with_chunks

from backend.agents.recommender import generate_recommendations
from backend.agents.skills_agent import analyze_skills 
from backend.agents.resume_analyzer import analyze_resume_deep
from backend.db.recommendations import save_recommendation


class Orchestrator: 
    """
    Async Orchestrator. 
    Manages the workflow and runs agents in parallel where possible.
    """
    
    def __init__(self):
        self.agents = {}
        
    def register_agent(self, name: str, func, *args, **kwargs):
        """Register an agent to run in parallel"""
        self.agents[name] = (func, args, kwargs)
    
    async def run_all_agents(self):
        """Execute all registered agents in parallel"""
        tasks = {
            name: asyncio.to_thread(func, *args, **kwargs)
            for name, (func, args, kwargs) in self.agents.items()
        }
        results = await asyncio.gather(*tasks. values(), return_exceptions=True)
        return dict(zip(tasks.keys(), results))
    

    async def run_resume_workflow(self, user_id: int, file_path: str, original_filename: str):
        conn_gen = get_conn()
        conn = next(conn_gen)
        
        try:
            print(f"[Orchestrator] 1. Parsing Resume...")
            parsed_resume = await asyncio.to_thread(genai_parse_pdf, file_path, original_filename)
            
            print(f"[Orchestrator] 2. Embedding & Saving...")
            embedded_resume = await asyncio.to_thread(embed_resume_chunks, parsed_resume)
            
            skills = []
            experience = []
            for chunk in embedded_resume['chunks']: 
                if 'skill' in chunk['section'].lower():
                    skills.append(chunk['content'])
                if any(x in chunk['section'].lower() for x in ['work', 'experience']):
                    experience.append(chunk['content'])

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
            
            task_recommend = asyncio.to_thread(generate_recommendations, conn, user_id)
            task_skills = asyncio.to_thread(analyze_skills, skills) 
            task_deep_analysis = asyncio.to_thread(analyze_resume_deep, embedded_resume['chunks'])

            recommendations, skills_analysis, deep_analysis = await asyncio.gather(
                task_recommend, 
                task_skills,
                task_deep_analysis,
                return_exceptions=True
            )
            
            # 4. Save Results
            print(f"[Orchestrator] 4. Saving Results...")
            
            # Save recommendations
            if not isinstance(recommendations, Exception):
                save_recommendation(conn, user_id, recommendations)
            else:
                print(f"[Orchestrator] Recommendations agent failed: {recommendations}")
            
            # Save skills analysis directly
            if not isinstance(skills_analysis, Exception):
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO skills_analysis (user_id, analysis_data, created_at)
                        VALUES (%s, %s, %s)
                        """,
                        (user_id, json.dumps(skills_analysis), datetime.utcnow())
                    )
                conn.commit()
            else:
                print(f"[Orchestrator] Skills agent failed: {skills_analysis}")
            
            # Save deep analysis directly
            if not isinstance(deep_analysis, Exception):
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO resume_analysis (user_id, analysis_data, created_at)
                        VALUES (%s, %s, %s)
                        """,
                        (user_id, json.dumps(deep_analysis), datetime.utcnow())
                    )
                conn.commit()
            else:
                print(f"[Orchestrator] Deep analysis agent failed: {deep_analysis}")
            
            print(f"[Orchestrator] Workflow complete. All agents finished.")

        except Exception as e:
            print(f"[Orchestrator] Error: {e}")
        finally:
            conn.close()
            if os.path.exists(file_path):
                os.remove(file_path)