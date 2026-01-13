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


@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, conn=Depends(get_conn)):
    resume = fetch_latest_resume(conn, user_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Use the REAL recommender agent
    recommendations = generate_recommendations(
        conn=conn,
        user_id=user_id,
        user_interests=None,  # Could add as query param
        current_role=None     # Could add as query param
    )
    
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

@app. get("/")
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
def get_recommendations(user_id: int, conn=Depends(get_conn)):
    resume = fetch_latest_resume(conn, user_id)
    if not resume: 
        raise HTTPException(status_code=404, detail="Resume not found")

    resume_id = resume. get("resume_id")

    try:
        skills = json.loads(resume. get("parsed_skills") or "[]")
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
        "resume_id":  resume_id,
        "skills":  skills,
        "experience": experience,
        "chunk_sections": [summary for summary, _ in chunk_summaries],
        "recommendations": recommendations,
        "status": "placeholder",
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


@app. get("/search/chunks")
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
    Each line is a complete JSON object representing a workflow event.
    """
    try:
        async for event in orchestrator.run_resume_workflow_stream(user_id, tmp_path, filename):
            # Yield each event as a JSON line followed by newline
            yield json.dumps(event).encode('utf-8') + b'\n'
    except Exception as e:
        # Yield error event if something goes wrong
        error_event = {
            "type": "error",
            "data": {"message": str(e), "error_type": type(e).__name__}
        }
        yield json.dumps(error_event).encode('utf-8') + b'\n'
    finally:
        # Clean up temp file
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
    
    Args:
        user_id: The user's ID
        file: PDF resume file
        stream:  If True, returns NDJSON stream for real-time progress updates
        
    Returns:
        If stream=False: JSON response with final results
        If stream=True:  NDJSON stream with progress events
    """
    # Validate file type
    if not file. filename.lower().endswith(". pdf"):
        raise HTTPException(status_code=400, detail="Only PDFs are supported")
    
    # Validate user exists
    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Save uploaded file temporarily
    file_bytes = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix='. pdf') as tmp:
        tmp. write(file_bytes)
        tmp_path = tmp.name
    
    # Import orchestrator
    from backend.agents.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    
    if stream:
        # Return streaming response with NDJSON
        return StreamingResponse(
            stream_workflow(orchestrator, user_id, tmp_path, file.filename),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering if behind nginx
            }
        )
    else:
        # Non-streaming:  wait for complete result
        try:
            result = await orchestrator. run_resume_workflow(user_id, tmp_path, file. filename)
            return result
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)