import json
from contextlib import asynccontextmanager
from typing import Optional

# --- FastAPI ---
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


# --- Internal Modules: Database ---
from backend.db.database import init_db, get_db, Resume
from backend.db.pg import init_db, get_conn
from backend.db.pg_vectors import (
    insert_user,
    get_user,
    insert_resume_with_chunks,
    fetch_latest_resume,
    fetch_resume_chunks,
    search_similar_chunks,
)

# --- Internal Modules: Agents & Parsing ---
from backend.agents.recommender import generate_recommendations
from backend.agents.resume_analyzer import analyze_resume_deep
from backend.parsing.parsing_helpers import parse_upload

# --- Embeddings / AI ---
from backend.utils.embeddings import init_client
import google.generativeai as genai

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
def create_user(email: str, name: str, conn = Depends(get_conn)):
    user_id = insert_user(conn, email=email, name=name)
    return {"user_id": user_id, "email": email, "name": name}
    
    


@app.get("/users/{user_id}")
def get_user(user_id: int, conn = Depends(get_conn)):
    """
    Retrieve user information by user ID.
    Queries the database for the user and returns their ID, email, name, and creation timestamp.
    """
    
    row = get_user(conn, user_id)
    if not row: 
        raise HTTPException(status_code=404, detail="User not found")
    return row
    
    
@app.post("/resume/upload")
async def upload_resume(
    user_id: int, 
    file: UploadFile = File(...),
    conn = Depends(get_conn)
):
    """
    Upload and process a user's resume file.
    Validates that the file is a PDF, checks if the user exists, parses the resume content,
    stores the parsed data in the database, and returns a summary including parsed chunks, skills, and experience.
    """
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDFs are supported")
    
    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")
        

    parsed = parse_upload(file) # returns raw_text, skills, experience, chunks (with embeddings)
    
    resume_id = insert_resume_with_chunks(
        conn=conn,
        user_id=user_id,
        raw_text=parsed["raw_text"],
        parsed_skills_text=json.dumps(parsed["skills"]),
        parsed_experience_text=json.dumps(parsed["experience"]),
        chunks=parsed["chunks"],  # each has section, content, summary, embedding(list[float])
    )
    
    
    return {
            "message": "Resume uploaded and processed successfully",
            "resume_id": resume_id,
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
def get_recommendations(user_id: int, conn = Depends(get_db)):
    """
    Get recommendations input data from Postgres (no agents/AI yet).
    Returns parsed skills/experience and an empty recommendations list.
    """
   
    resume = fetch_latest_resume(conn, user_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    
    try:
        skills = json.loads(resume.get("parsed_skills") or "[]")
    except Exception:
        skills = []

    try:
        experience = json.loads(resume.get("parsed_experience") or "[]")
    except Exception:
        experience = []

    return {
        "user_id": user_id,
        "resume_id": resume["id"],
        "skills": skills,
        "experience": experience,
        "recommendations": [],  # placeholder until AI is implemented
        "status": "not_implemented"
    }
    
    
    
@app.get("/resume/analyze/{user_id}")
def analyze_resume(user_id: int, conn = Depends(get_db)):
    """
    Get deep AI analysis of a user's resume including:
    - Core competencies
    - Career progression patterns
    - Strengths and areas for development
    - Potential career pivots
    - Actionable resume improvements
    """
    
    resume = fetch_latest_resume(conn, user_id)    
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found for this user")
    
    chunks = fetch_resume_chunks(conn, resume_id=resume["id"])
    
    analysis = analyze_resume_deep(
        raw_text=resume.get("raw_text") or "",
        sections=[{"section": chunk["section"], "summary": chunk["summary"], "content": chunk["content"]} for chunk in chunks],
    )
    
    return {"user_id": user_id, 
            "resume_id": resume["id"], 
            "analysis": analysis}
    
    
@app.get("/search/chunks")
def search_chunks(
    query: str = Query(..., description="Natural language query"),
    user_id: Optional[int] = Query(None),
    conn = Depends(get_conn),
):
    
    init_client()
    embeddings = genai.embed_content(model="models/text-embedding-004", content=query)["embedding"]

    rows = search_similar_chunks(conn, query_embedding=embeddings, user_id=user_id, limit=10)
    return {"query": query, "results": rows}
    