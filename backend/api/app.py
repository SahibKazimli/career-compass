from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.db.database import init_db, get_db, Resume  
from backend.agents.recommender import generate_recommendations
from contextlib import asynccontextmanager
from backend.parsing.parsing_helpers import parse_upload  
from backend.agents.resume_analyzer import analyze_resume_deep
import json
from fastapi.middleware.cors import CORSMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application lifespan by initializing the database on startup and handling any necessary cleanup on shutdown.
    Prints status messages indicating the initialization and shutdown phases.
    """
    init_db()
    print("Database initialized! career_compass.db file created.")
    yield
    print("Shutting down...")
    
app = FastAPI(title="Career Compass", lifespan=lifespan)

# 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # All origins for dev
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root(): 
    return {"message": "Welcome to the Career Compass API"}


@app.post("/users")
def create_user(email:str, name:str, db: Session=Depends(get_db)):

    # Create a new user
    query = text("INSERT INTO users (email, name, created_at) VALUES (:email, :name, datetime('now'))")
    db.execute(query, {"email": email, "name": name})
    db.commit()
    
    result = db.execute(text("SELECT last_insert_rowid()"))
    user_id = next(result)[0]
    
    return {"id": user_id, "email": email, "name": name}
    
    


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve user information by user ID.
    Queries the database for the user and returns their ID, email, name, and creation timestamp.
    """
    
    query = text("SELECT * FROM users WHERE id = :user_id")
    result = db.execute(query, {"user_id": user_id})
    rows = list(result)
    
    if not rows: 
        raise HTTPException(status_code=404, detail="user not found")
    user = rows[0]
    
    return {
        "id": user[0],
        "email": user[1],
        "name": user[2],
        "created_at": str(user[3]) if user[3] else None
    }    
    
    
@app.post("/resume/upload")
async def upload_resume(
    user_id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a user's resume file.
    Validates that the file is a PDF, checks if the user exists, parses the resume content,
    stores the parsed data in the database, and returns a summary including parsed chunks, skills, and experience.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDFs are supported")
    
    user_check = db.execute(text("SELECT id FROM users WHERE id = :user_id"), {"user_id":user_id})
    if not user_check:
        raise HTTPException(status_code=404, detail="User not found")


    parsed = parse_upload(file)
    resume = Resume(
        user_id=user_id, 
        raw_text=parsed["raw_text"],
        parsed_skills=json.dumps(parsed["skills"]),
        parsed_experience=json.dumps(parsed["experience"]),            
        embedding=json.dumps(parsed["chunks"]))
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    
    return {
            "message": "Resume uploaded and processed successfully",
            "resume_id": resume.id,
            "filename": file.filename,
            "parsed_data": {
                "chunks": [
                    {
                        "section": chunk['section'],
                        "content": chunk['content'],
                        "summary": chunk['summary']
                        
                    }
                    for chunk in parsed['chunks']
                ],
                "skills": parsed["skills"],
                "experience": parsed["experience"],
                "total_chunks": len(parsed["chunks"])
            },
        }
    
    
@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """
    Get AI-powered career recommendations for a user based on their resume
    """
    
    resume = db.query(Resume).filter(Resume.user_id == user_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    
    skills = json.loads(resume.parsed_skills)
    experience = json.loads(resume.parsed_experience)
    
    recommendations = generate_recommendations(skills, experience, resume.raw_text)
    
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }
    
    
@app.get("/resume/analyze/{user_id}")
def analyze_resume(user_id: int, db: Session = Depends(get_db)):
    """
    Get deep AI analysis of a user's resume including:
    - Core competencies
    - Career progression patterns
    - Strengths and areas for development
    - Potential career pivots
    - Actionable resume improvements
    """
    
    # Load the most recent resume for the user
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.id.desc())
        .first()
    )
    
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found for this user")
    
    # Parse the stored chunks (they're stored as JSON string)
    chunks = json.loads(resume.embedding)
    
    # Call the analyzer
    analysis = analyze_resume_deep(
        raw_text=resume.raw_text,
        sections=chunks
    )
    
    return {
        "user_id": user_id,
        "resume_id": resume.id,
        "analysis": analysis
    }
    
    
@app.get("/skills/analyze/{user_id}")
def analyze_skills(user_id: int, target_role: str = None, db: Session = Depends(get_db)):
    """
    Analyze user's skills with optional target role comparison
    """
    
    resume = db.query(Resume).filter(Resume.user_id == user_id).first()
    if not resume: 
        raise HTTPException(status_code=404, detail="Resume not found")
    
    skills = json.loads(resume.parsed_skills)
    analysis = analyze_resume_deep(skills)
    
    return {
        "user_id": user_id, 
        "target_role": target_role, 
        "skills_analysis": analysis
    }
    
    