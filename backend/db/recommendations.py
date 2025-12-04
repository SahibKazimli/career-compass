import json
from typing import List, Dict, Any
from psycopg import Connection

def save_recommendation(conn: Connection, user_id: int, recommendations_data: Dict[str, any]):
    """
    Helper that saves the list of recommended career paths to the database.
    Handles checking/creating the 'career_paths' entries automatically.
    """
    
    recs = recommendations_data.get("recommendations", [])
    
    with conn.cursor() as cur:
        for rec in recs:
            title = rec.get("title")
            
            # 1. Ensure Career Path exists
            cur.execute("SELECT id FROM career_paths WHERE title = %s", (title,))
            row = cur.fetchone()
            
            if row: 
                path_id = row["id"]
            else:
                cur.execute(
                    """INSERT INTO career_paths (title, description, avg_salary)
                    VALUES (%s, %s, %s)
                    """,
                    (title, rec.get["match_reason"], rec.get("estimated_salary_range"))
                )
                path_id = cur.fetchone()["id"]

            # 2. Save the personalized recommendation link
            cur.execute(
                """
                INSERT INTO recommendations 
                (user_id, career_path_id, skill_gaps, learning_path, raw_text)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    user_id, 
                    path_id, 
                    json.dumps(rec.get("skills_to_develop", [])),
                    json.dumps(rec.get("first_steps", [])),
                    json.dumps(rec) # Store full object just in case
                )
            )
    conn.commit()