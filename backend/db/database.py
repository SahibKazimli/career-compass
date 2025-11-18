from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from pgvector.sqlalchemy import Vector
from datetime import datetime
from pathlib import Path
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://career_user:career_pass@localhost:5432/career_compass"
)

# check_same_thread = False, required for FastAPI
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread":False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime)


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    parsed_skills = Column(Text) # JSON string
    parsed_experience = Column(Text) # JSON string
    embedding = Column(Text) # JSON array as string for MVP 
    created_at = Column(DateTime, default=datetime)


class CareerPath(Base):
    __tablename__ = "career_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    required_skills = Column(Text)  # JSON string
    embedding = Column(Text)  # JSON array as string
    avg_salary = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime)
    
    
class Recommendations(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    raw_text = Column(Text)
    career_path_id = Column(Integer)
    similarity_score = Column(Float)
    skill_gaps = Column(Text)  # JSON string
    learning_path = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)



def init_db():
    """
    Initialize database by running schema.sql.
    Safe to run multiple times (uses IF NOT EXISTS).
    """
    try:
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"schema.sql not found at {schema_path}")
        
        print(f"Reading schema from: {schema_path}")
        
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        
        # Execute schema.sql
        with engine.connect() as conn:
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
            
            for i, statement in enumerate(statements, 1):
                print(f"Executing statement {i}/{len(statements)}...")
                conn.execute(text(statement))
            
            conn.commit()
        
        print("Database initialized successfully from schema.sql")
        print("pgvector extension enabled")
        print("All tables and indexes created")
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise
    
    
    
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()