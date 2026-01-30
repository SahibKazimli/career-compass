import json
import os
import tempfile
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi. middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.db.pg import init_db, get_conn
from backend.db.pg_vectors import (
    insert_user,
    get_user,
    insert_resume_with_chunks,
    fetch_latest_resume,
    fetch_resume_chunks,
    search_similar_chunks,
)
from backend.parsing.parsing_helpers import parse_upload
from backend.utils.llm import summarize_chunks
from backend.utils.embeddings import init_client
from backend.agents.recommender import generate_recommendations
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


@app.get("/")
def read_root():
    return {"message": "Welcome to the Career Compass API"}


@app.post("/users")
def create_user(email: str, name: str, conn=Depends(get_conn)):
    user_id = insert_user(conn, email=email, name=name)
    return {"user_id": user_id, "email": email, "name": name}


@app.get("/users/{user_id}")
def get_user_route(user_id:  int, conn=Depends(get_conn)):
    row = get_user(conn, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@app.post("/resume/upload")
async def upload_resume(
    user_id: int,
    file: UploadFile = File(...),
    conn=Depends(get_conn)
):
    if not file.filename. lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDFs are supported")

    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    parsed = parse_upload(file)

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
            "skills":  parsed["skills"],
            "experience": parsed["experience"],
            "total_chunks": len(parsed["chunks"]),
        },
    }


@app.get("/recommendations/{user_id}")
def get_recommendations(
    user_id:  int,
    user_interests: Optional[str] = Query(None, description="User's career interests"),
    current_role: Optional[str] = Query(None, description="User's current job role"),
    regenerate: bool = Query(False, description="Force regeneration of recommendations"),
    conn=Depends(get_conn)
):
    """
    Get AI-generated career recommendations based on user's resume. 
    First checks for cached recommendations, regenerates if not found.
    """
    resume = fetch_latest_resume(conn, user_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.  Please upload a resume first.")

    # First, try to fetch existing recommendations from database
    if not regenerate:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.id, r.skill_gaps, r.learning_path, r.raw_text, 
                       cp.title, cp.description, cp.avg_salary
                FROM recommendations r
                JOIN career_paths cp ON r.career_path_id = cp.id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
                LIMIT 5
            """, (user_id,))
            rows = cur.fetchall()
            
            if rows:
                recommendations = []
                for row in rows:
                    raw = json.loads(row["raw_text"]) if row["raw_text"] else {}
                    recommendations.append({
                        "title": row["title"] or raw.get("title", "Career Path"),
                        "match_reason": raw.get("match_reason", row["description"] or "Based on your profile"),
                        "relevant_existing_skills": raw.get("relevant_existing_skills", []),
                        "skills_to_develop": json.loads(row["skill_gaps"]) if row["skill_gaps"] else raw.get("skills_to_develop", []),
                        "transition_difficulty": raw.get("transition_difficulty", "Medium"),
                        "estimated_salary_range": row["avg_salary"] or raw.get("estimated_salary_range", "Competitive"),
                        "first_steps": json.loads(row["learning_path"]) if row["learning_path"] else raw.get("first_steps", []),
                    })
                
                return {
                    "user_id": user_id,
                    "resume_id": resume.get("resume_id"),
                    "recommendations": {
                        "recommendations": recommendations,
                        "overall_assessment": "Based on your resume analysis",
                        "cached": True
                    }
                }

    # Generate new recommendations if not cached
    recommendations = generate_recommendations(
        conn=conn,
        user_id=user_id,
        user_interests=user_interests,
        current_role=current_role
    )

    return {
        "user_id": user_id,
        "resume_id": resume.get("resume_id"),
        "recommendations": recommendations
    }


@app.get("/resume/analyze/{user_id}")
def analyze_resume(user_id:  int, conn=Depends(get_conn)):
    resume = fetch_latest_resume(conn, user_id)
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found for this user")

    resume_id = resume.get("resume_id")
    chunks = fetch_resume_chunks(conn, resume_id=resume_id)

    analysis = {
        "sections": [
            {
                "section": chunk["section"],
                "sample": (chunk. get("summary") or chunk.get("content") or "")[:400],
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
    query:  str = Query(..., description="Natural language query"),
    user_id: Optional[int] = Query(None),
    conn=Depends(get_conn),
):
    init_client()
    embedding = genai.embed_content(model="models/text-embedding-004", content=query)["embedding"]
    rows = search_similar_chunks(conn, query_embedding=embedding, user_id=user_id, limit=10)
    return {"query": query, "results": rows}


async def stream_workflow(
    orchestrator,
    user_id: int,
    tmp_path: str,
    filename: str
) -> AsyncGenerator[bytes, None]:
    """
    Async generator that yields NDJSON (newline-delimited JSON).
    """
    try:
        async for event in orchestrator.run_resume_workflow_stream(user_id, tmp_path, filename):
            yield json.dumps(event).encode('utf-8') + b'\n'
    except Exception as e:
        error_event = {
            "type": "error",
            "data": {"message": str(e), "error_type": type(e).__name__}
        }
        yield json.dumps(error_event).encode('utf-8') + b'\n'
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/resume/process")
async def process_resume_full(
    user_id: int,
    file: UploadFile = File(... ),
    stream:  bool = Query(False, description="Enable streaming for real-time progress updates"),
    conn=Depends(get_conn)
):
    """
    Process resume through full orchestrator pipeline.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDFs are supported")

    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    file_bytes = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp. write(file_bytes)
        tmp_path = tmp.name

    from backend.agents.orchestrator import Orchestrator
    orchestrator = Orchestrator()

    if stream:
        return StreamingResponse(
            stream_workflow(orchestrator, user_id, tmp_path, file.filename),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    else:
        try:
            result = await orchestrator.run_resume_workflow(user_id, tmp_path, file.filename)
            return result
        finally: 
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


@app.get("/users/email/{email}")
def get_user_by_email(email: str, conn=Depends(get_conn)):
    """Get user by email address."""
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, email, name, created_at FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@app.get("/skills/{user_id}")
def get_skills_analysis(user_id: int, conn=Depends(get_conn)):
    """Get the latest skills analysis for a user."""
    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, analysis_data, created_at 
            FROM skills_analysis 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
            """,
            (user_id,)
        )
        row = cur.fetchone()
    
    if not row:
        return {"user_id": user_id, "skills": [], "message": "No skills analysis found. Please upload a resume first."}
    
    analysis_data = json.loads(row.get("analysis_data", "{}")) if row.get("analysis_data") else {}
    return {
        "user_id": user_id,
        "analysis_id": row.get("id"),
        "skills": analysis_data,
        "created_at": row.get("created_at")
    }


@app.get("/analysis/{user_id}")
def get_resume_analysis(user_id: int, conn=Depends(get_conn)):
    """Get the latest resume analysis for a user."""
    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, analysis_data, created_at 
            FROM resume_analysis 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
            """,
            (user_id,)
        )
        row = cur.fetchone()
    
    if not row:
        return {"user_id": user_id, "analysis": None, "message": "No resume analysis found. Please upload a resume first."}
    
    analysis_data = json.loads(row.get("analysis_data", "{}")) if row.get("analysis_data") else {}
    return {
        "user_id": user_id,
        "analysis_id": row.get("id"),
        "analysis": analysis_data,
        "created_at": row.get("created_at")
    }


@app.get("/roadmap/{user_id}")
def get_roadmap(user_id: int, conn=Depends(get_conn)):
    """Get personalized career roadmap based on recommendations."""
    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch latest recommendation
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, raw_text, skill_gaps, learning_path, created_at 
            FROM recommendations 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
            """,
            (user_id,)
        )
        row = cur.fetchone()
    
    if not row:
        return {"user_id": user_id, "roadmap": None, "message": "No roadmap found. Please upload a resume first."}
    
    raw_text = row.get("raw_text", "{}")
    recommendations = json.loads(raw_text) if raw_text else {}
    skill_gaps = json.loads(row.get("skill_gaps", "[]")) if row.get("skill_gaps") else []
    learning_path = json.loads(row.get("learning_path", "[]")) if row.get("learning_path") else []
    
    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "skill_gaps": skill_gaps,
        "learning_path": learning_path,
        "created_at": row.get("created_at")
    }