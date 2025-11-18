import os
from pathlib import Path
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pgvector.psycopg import register_vector

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://career_user:career_pass@localhost:5432/career_compass"
)

# Psycopg3 connection pool
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    kwargs={"row_factory": dict_row},  
)

def init_db():
    """
    Run schema.sql on startup.
    Safe to run repeatedly (schema uses IF NOT EXISTS).
    Also ensures pgvector is ready.
    """
    schema_path = Path(__file__).parent / "init" / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql not found at {schema_path}")

    with pool.connection() as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            sql = schema_path.read_text()
            cur.execute(sql)
        conn.commit()

def get_conn():
    with pool.connection() as conn:
        register_vector(conn)  
        yield conn