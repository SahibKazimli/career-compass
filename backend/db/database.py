from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# For MVP - storing everything in one database 
SQLALCHEMY_DATABASE_URL = "sqlite:///./career_compass.db"

# check_same_thread = False, required for FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
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


# Create all tables 
def init_db():
    Base.metadata.create_all(bind=engine)
    
    
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()