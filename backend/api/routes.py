from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.database import init_db, get_db, Resume  
from contextlib import asynccontextmanager
from backend.parsing.parsing_helpers import parse_upload  
from typing import Optional


app = FastAPI(title="Career Compass")

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
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve user information by user ID.
    Queries the database for the user and returns their ID, email, name, and creation timestamp.
    """
    
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
    
    user_check = db.execute("SELECT id FROM users WHERE id = :user_id", {"user_id":user_id})
    if not user_check:
        raise HTTPException(status_code=404, detail="User not found")


    parsed = parse_upload(file)
    resume = Resume(
        user_id=user_id, 
        raw_text=parsed["raw_text"],
        parsed_skills=parsed["skills"],
        parsed_experience=parsed["experience"],            
        embedding=[chunk['embedding'] for chunk in parsed['chunks']])
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