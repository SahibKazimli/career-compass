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
            "SELECT * FROM users WHERE user_id = %s", (user_id),
        )
    row = cur.fetchone()
    return row
    