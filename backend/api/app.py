import json
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any, Tuple

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Raw Postgres access
from backend.db.pg import init_db, get_conn
from backend.db.pg_vectors import (
    insert_user,
    get_user,
    insert_resume_with_chunks,
    fetch_latest_resume,
    fetch_resume_chunks,
    search_similar_chunks,
)

# Parsing
from backend.parsing.parsing_helpers import parse_upload
from backend.utils.llm import summarize_chunks

# Embeddings / similarity
from backend.utils.embeddings import init_client
import google.generativeai as genai


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Database connection pool initialized.")
    yield
    print("Shutting down...")


app = FastAPI(title="Career Compass", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



def simple_placeholder_recommendations():
    ...
    # need to implement something with proper recommendations. 


@app.get("/")
def read_root():
    return {"message": "Welcome to the Career Compass API"}


@app.post("/users")
def create_user(email: str, name: str, conn = Depends(get_conn)):
    user_id = insert_user(conn, email=email, name=name)
    return {"user_id": user_id, "email": email, "name": name}


@app.get("/users/{user_id}")
def get_user_route(user_id: int, conn = Depends(get_conn)):
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
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDFs are supported")

    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    parsed = parse_upload(file)  # { raw_text, skills, experience, chunks:[{section, content, summary, embedding}] }

    resume_id = insert_resume_with_chunks(
        conn=conn,
        user_id=user_id,
        raw_text=parsed["raw_text"],
        parsed_skills_text=json.dumps(parsed["skills"]),
        parsed_experience_text=json.dumps(parsed["experience"]),
        chunks=parsed["chunks"],
    )

    return {
        "message": "Resume uploaded and processed successfully",
        "resume_id": resume_id,
        "filename": file.filename,
        "parsed_data": {
            "chunks": [
                {
                    "section": chunk["section"],
                    "content": chunk["content"],
                    "summary": chunk["summary"],
                }
                for chunk in parsed["chunks"]
            ],
            "skills": parsed["skills"],
            "experience": parsed["experience"],
            "total_chunks": len(parsed["chunks"]),
        },
    }


@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, conn = Depends(get_conn)):
    resume = fetch_latest_resume(conn, user_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume_id = resume.get("resume_id")

    try:
        skills = json.loads(resume.get("parsed_skills") or "[]")
    except Exception:
        skills = []
    try:
        experience = json.loads(resume.get("parsed_experience") or "[]")
    except Exception:
        experience = []

    chunks = fetch_resume_chunks(conn, resume_id=resume_id)
    chunk_summaries = summarize_chunks(chunks)

    recommendations = simple_placeholder_recommendations(
        skills=skills,
        experience=experience,
        chunk_summaries=chunk_summaries,
        user_interests=None,
        current_role=None,
    )

    return {
        "user_id": user_id,
        "resume_id": resume_id,
        "skills": skills,
        "experience": experience,
        "chunk_sections": [summary for summary, _ in chunk_summaries],
        "recommendations": recommendations,
        "status": "placeholder",
    }


@app.get("/resume/analyze/{user_id}")
def analyze_resume(user_id: int, conn = Depends(get_conn)):
    resume = fetch_latest_resume(conn, user_id)
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found for this user")

    resume_id = resume.get("resume_id")
    chunks = fetch_resume_chunks(conn, resume_id=resume_id)

    analysis = {
        "sections": [
            {
                "section": chunk["section"],
                "sample": (chunk.get("summary") or chunk.get("content") or "")[:400],
            }
            for chunk in chunks
        ],
        "note": "Detailed AI analysis not yet implemented.",
    }

    return {
        "user_id": user_id,
        "resume_id": resume_id,
        "analysis": analysis,
    }


@app.get("/search/chunks")
def search_chunks(
    query: str = Query(..., description="Natural language query"),
    user_id: Optional[int] = Query(None),
    conn = Depends(get_conn),
):
    init_client()
    embedding = genai.embed_content(model="models/text-embedding-004", content=query)["embedding"]
    rows = search_similar_chunks(conn, query_embedding=embedding, user_id=user_id, limit=10)
    return {"query": query, "results": rows}