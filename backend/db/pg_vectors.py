from typing import List, Dict, Any, Optional
from psycopg import Connection

def insert_user(conn: Connection, email: str, name: str) -> int:
    """
    Add a new user to the database and return their ID.
    """
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (email, name) VALUES (%s, %s) RETURNING user_id",
            (email, name),
        )
        user_id = cur.fetchone()["user_id"]
    conn.commit()
    return user_id


def get_user(conn: Connection, user_id: int) -> Optional[Dict]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM users WHERE user_id = %s", 
            (user_id,),
        )
        row = cur.fetchone()
    return row
    
    
def insert_resume(
    conn: Connection, 
    user_id: int,
    raw_text: str, 
    parsed_skills_text: str, 
    parsed_experience_text: str 
    ) -> Optional[Dict]:
    
    with conn.cursor() as cur: 
        cur.execute(
            """
            INSERT INTO resumes (user_id, raw_text, parsed_skills, parsed_experience, embedding)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING resume_id
            """,
            (user_id, raw_text, parsed_skills_text, parsed_experience_text, None)
        )
        resume_id = cur.fetchone()["resume_id"]
    return resume_id    
    
        
def insert_resume_with_chunks(
    conn: Connection,
    user_id: int,
    raw_text: str,
    parsed_skills_text: str,
    parsed_experience_text: str,
    chunks: List[Dict[str, Any]],  # each: {section, content, summary, embedding: List[float]}
) -> int:
    """
    Inserts a resume row, then bulk-inserts chunk rows with vector embeddings.
    Assumes embeddings are lists[float] with length 768.
    """
    
    inserted_resume_id = insert_resume(conn, user_id, raw_text, parsed_skills_text, parsed_experience_text)
    
    with conn.cursor() as cur: 
        # Insert chunks
        if chunks:
            cur.executemany(
                """
                INSERT INTO resume_chunks (resume_id, section, content, summary, embedding)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    (
                        inserted_resume_id,
                        ch.get("section"),
                        ch.get("content"),
                        ch.get("summary"),
                        ch.get("embedding"),  # pgvector adapter handles list -> vector
                    )
                    for ch in chunks
                ],
            )
    conn.commit()
    return inserted_resume_id


def fetch_latest_resume(conn, user_id: int) -> Optional[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM resumes
            WHERE user_id = %s
            ORDER BY resume_id DESC
            LIMIT 1
            """,
            (user_id,),
        )
        return cur.fetchone()


def fetch_resume_chunks(conn: Connection, resume_id: int) -> List[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, section, content, summary
            FROM resume_chunks
            WHERE resume_id = %s
            ORDER BY id ASC
            """,
            (resume_id,),
        )
        return cur.fetchall()


def search_similar_chunks(
    conn: Connection,
    query_embedding: List[float],
    user_id: Optional[int] = None,
    limit: int = 5,
) -> List[dict]:
    """
    ANN search using cosine distance. If user_id provided, restrict to that user's resumes.
    """
    with conn.cursor() as cur:
        if user_id is None:
            cur.execute(
                """
                SELECT rc.id, rc.resume_id, rc.section, rc.summary, rc.content,
                       (rc.embedding <-> %s) AS distance
                FROM resume_chunks rc
                ORDER BY rc.embedding <-> %s
                LIMIT %s
                """,
                (query_embedding, query_embedding, limit),
            )
        else:
            cur.execute(
                """
                SELECT rc.id, rc.resume_id, rc.section, rc.summary, rc.content,
                       (rc.embedding <-> %s) AS distance
                FROM resume_chunks rc
                JOIN resumes r ON r.resume_id = rc.resume_id
                WHERE r.user_id = %s
                ORDER BY rc.embedding <-> %s
                LIMIT %s
                """,
                (query_embedding, user_id, query_embedding, limit),
            )
        return cur.fetchall()
    