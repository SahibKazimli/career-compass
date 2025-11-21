import json
from typing import Optional, Dict, Any, List
from psycopg import Connection, Cursor
from uuid import uuid4

"""
A module for producing events which control the multiagent system.
"""

# All functions assume a raw psycopg connection from pg.py

def publish_event(conn: Connection, event_type: str,
                  user_id: Optional[int]=None,
                  resume_id: Optional[int]=None,
                  run_id: Optional[str]=None,
                  payload: Optional[Dict[str, Any]]=None) -> str:
    event_id = str(uuid4())
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO agent_events (event_id, event_type, user_id, resume_id, run_id, payload)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING event_id
            """,
            (event_id, event_type, user_id, resume_id, run_id,
             json.dumps(payload) if payload else json.dumps({}))
        )
        eid = cur.fetchone()["event_id"]
    conn.commit()
    return eid


def fetch_pending_events(conn: Connection, limit: int=20) -> List[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM agent_events
            WHERE status = 'pending'
            ORDER BY created_at ASC
            LIMIT %s
            """,
            (limit,)
        )
        return cur.fetchall()
    
def mark_event_status(conn: Connection, event_id: str, status: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE agent_events
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE event_id = %s
            """,
            (status, event_id)
        )
    conn.commit()
    
    
def increment_attempts(conn, event_id: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE agent_events
            SET attempts = attempts + 1, updated_at = CURRENT_TIMESTAMP
            WHERE event_id = %s
            """,
            (event_id,)
        )
    conn.commit()
    

def append_run_state(conn, run_id: str, patch: Dict[str, Any]):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE agent_runs
            SET state = COALESCE(state, '{}'::jsonb) || %s::jsonb,
                updated_at = CURRENT_TIMESTAMP
            WHERE run_id = %s
            """,
            (json.dumps(patch), run_id)
        )
    conn.commit()
    

def create_run(conn, user_id: int, target_role: str) -> str:
    run_id = str(uuid4())
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO agent_runs (run_id, user_id, target_role)
            VALUES (%s, %s, %s)
            RETURNING run_id
            """,
            (run_id, user_id, target_role)
        )
        rid = cur.fetchone()["run_id"]
    conn.commit()
    return rid


def mark_run_status(conn, run_id: str, status: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE agent_runs
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE run_id = %s
            """,
            (status, run_id)
        )
    conn.commit()