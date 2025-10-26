from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import init_db, get_db, User, Resume
from contextlib import asynccontextmanager
import tempfile
from parsing.resume_parser import genai_parse_pdf
from utils.embeddings import embed_resume_chunks
from parsing.parsing_helpers import parse_upload

app = FastAPI(title="Career Compass")

# Initialize db on startup 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    init_db()
    print("Database initialized! career_compass.db file created.")
    yield
    # Shutdown: Clean up resources (if needed)
    print("Shutting down...")


@app.get("/")
def read_root(): 
    return {"message": "Welcome to the Career Compass API"}


@app.post("/users")
def create_user(email:str, name:str, db: Session=Depends(get_db)):
    # Create a new user
    query = "INSERT INTO users (email, name, created_at) VALUES (:email, :name, datetime('now'))"
    db.execute(query, {"email": email, "name": name})
    db.commit()
    
    result = db.execute("SELECT last_insert_rowid()")
    user_id = next(result)[0]
    
    return {"id": user_id, "email": email, "name": name}
    
    


@app.get("/users/{user_id}")
def get_user(user_id: id, db: Session = Depends(get_db)):
    
    query = "SELECT * FROM users WHERE id = :user_id"
    result = db.execute(query, {"id": user_id})
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
    user_id: id, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDFs are supported")
    
    user_check = db.execute("SELECT id FROM users WHERE id = :user_id", {"user_id":user_id})
    if not user_check:
        raise HTTPException(status_code=404, detail="User not found")


    parsed = parse_upload(file)
    resume = Resume(
        user_id=user_id, 
        raw_text=parsed["raw_text"],
        parsed_skills=parsed["skills"],
        parsed_experience=["experience"],            
        embedding=[]
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume.id,
        "filename": file.filename
    }
    