import json
import os
import tempfile
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import settings
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
from backend.agents.resources_agent import generate_learning_resources, get_resources_for_skill
from backend.agents.career_matcher import match_careers, get_transition_roadmap
from backend.api.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    PasswordChange,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    get_optional_user,
    get_user_by_email_with_password,
    create_user_with_password,
    update_user_password,
    delete_user_account,
)
import google.generativeai as genai


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Database connection pool initialized.")
    yield
    print("Shutting down...")


app = FastAPI(title="Career Compass", lifespan=lifespan)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# =====================
# Health Check
# =====================

@app.get("/")
def read_root():
    return {"message": "Welcome to the Career Compass API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy"}


# =====================
# Authentication Endpoints
# =====================

@app.post("/auth/register", response_model=TokenResponse)
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserRegister, conn=Depends(get_conn)):
    """Register a new user account."""
    # Check if email already exists
    existing = get_user_by_email_with_password(conn, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Create user with hashed password
    password_hash = hash_password(user_data.password)
    user_id = create_user_with_password(conn, user_data.email, user_data.name, password_hash)
    
    # Generate tokens
    access_token = create_access_token(user_id, user_data.email)
    refresh_token = create_refresh_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600
    )


@app.post("/auth/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin, conn=Depends(get_conn)):
    """Login with email and password."""
    user = get_user_by_email_with_password(conn, credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user has a password set
    if not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please set a password for your account"
        )
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate tokens
    access_token = create_access_token(user["user_id"], user["email"])
    refresh_token = create_refresh_token(user["user_id"])
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600
    )


@app.post("/auth/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
async def refresh_token(request: Request, conn=Depends(get_conn)):
    """Refresh access token using refresh token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = int(payload.get("sub"))
    
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, email FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = create_access_token(user["user_id"], user["email"])
    new_refresh_token = create_refresh_token(user["user_id"])
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user info."""
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        name=current_user["name"],
        created_at=str(current_user.get("created_at", ""))
    )


@app.put("/auth/password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    conn=Depends(get_conn)
):
    """Change the current user's password."""
    # Get user with password
    user = get_user_by_email_with_password(conn, current_user["email"])
    
    # Verify current password if one exists
    if user.get("password_hash"):
        if not verify_password(password_data.current_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Update password
    new_hash = hash_password(password_data.new_password)
    update_user_password(conn, current_user["user_id"], new_hash)
    
    return {"message": "Password updated successfully"}


@app.delete("/auth/account")
async def delete_account(
    current_user: dict = Depends(get_current_user),
    conn=Depends(get_conn)
):
    """Delete the current user's account."""
    delete_user_account(conn, current_user["user_id"])
    return {"message": "Account deleted successfully"}


# =====================
# Legacy User Endpoints (for backward compatibility, will require auth in future)
# =====================

@app.post("/users")
def create_user_legacy(email: str, name: str, conn=Depends(get_conn)):
    """Create user (legacy endpoint - use /auth/register instead)."""
    user_id = insert_user(conn, email=email, name=name)
    return {"user_id": user_id, "email": email, "name": name}


@app.get("/users/{user_id}")
def get_user_route(user_id: int, conn=Depends(get_conn)):
    row = get_user(conn, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@app.get("/users/email/{email}")
def get_user_by_email(email: str, conn=Depends(get_conn)):
    """Get user by email address."""
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, email, name, created_at FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row


# =====================
# Resume Endpoints
# =====================

@app.post("/resume/upload")
@limiter.limit("10/minute")
async def upload_resume(
    request: Request,
    user_id: int,
    file: UploadFile = File(...),
    conn=Depends(get_conn)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDFs are supported")

    # Check file size
    file_bytes = await file.read()
    if len(file_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    await file.seek(0)  # Reset file position

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
            "skills": parsed["skills"],
            "experience": parsed["experience"],
            "total_chunks": len(parsed["chunks"]),
        },
    }


@app.get("/recommendations/{user_id}")
def get_recommendations(
    user_id: int,
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
        raise HTTPException(status_code=404, detail="Resume not found. Please upload a resume first.")

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
def analyze_resume(user_id: int, conn=Depends(get_conn)):
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
@limiter.limit("5/minute")
async def process_resume_full(
    request: Request,
    user_id: int,
    file: UploadFile = File(...),
    stream: bool = Query(False, description="Enable streaming for real-time progress updates"),
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
    
    # Check file size
    if len(file_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(file_bytes)
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


# =============================================================================
# RESOURCES ENDPOINTS (AI-Generated Learning Resources)
# =============================================================================

@app.get("/resources/{user_id}")
@limiter.limit(settings.RATE_LIMIT)
def get_user_resources(
    request: Request,
    user_id: int,
    time_commitment: str = Query("medium", regex="^(low|medium|high)$"),
    target_role: Optional[str] = None,
    conn=Depends(get_conn)
):
    """
    Generate AI-powered learning resources based on user's skill gaps.
    Uses the skills analysis to determine what resources to recommend.
    """
    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch skills analysis to get skills_to_strengthen
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT analysis_data FROM skills_analysis 
            WHERE user_id = %s 
            ORDER BY created_at DESC LIMIT 1
            """,
            (user_id,)
        )
        row = cur.fetchone()
    
    if not row or not row.get("analysis_data"):
        raise HTTPException(
            status_code=404, 
            detail="No skills analysis found. Please upload a resume first."
        )
    
    skills_data = json.loads(row["analysis_data"])
    skills_to_develop = skills_data.get("skills_to_strengthen", [])
    current_skills = skills_data.get("core_technical_skills", [])
    
    # Clean up skill descriptions (remove time estimates from strings)
    cleaned_skills = []
    for skill in skills_to_develop[:5]:  # Limit to top 5
        if isinstance(skill, str):
            # Strip time estimates like "(Estimated time: ...)"
            clean = skill.split("(Estimated")[0].strip()
            clean = clean.split(":")[0].strip() if ":" in clean else clean
            cleaned_skills.append(clean)
    
    # Generate resources using AI agent
    resources = generate_learning_resources(
        skills_to_develop=cleaned_skills,
        current_skills=current_skills[:10],  # Limit context
        target_role=target_role,
        time_commitment=time_commitment
    )
    
    return {
        "user_id": user_id,
        "skills_analyzed": cleaned_skills,
        "time_commitment": time_commitment,
        "target_role": target_role,
        "resources": resources
    }


@app.get("/resources/skill/{skill_name}")
@limiter.limit(settings.RATE_LIMIT)
def get_skill_resources(
    request: Request,
    skill_name: str,
    depth: str = Query("comprehensive", regex="^(quick|comprehensive)$")
):
    """
    Get learning resources for a specific skill.
    """
    resources = get_resources_for_skill(skill_name, depth=depth)
    return resources


# =============================================================================
# CAREER MATCHING ENDPOINTS (AI-Powered Career Recommendations)
# =============================================================================

@app.get("/careers/{user_id}")
@limiter.limit(settings.RATE_LIMIT)
def get_career_matches(
    request: Request,
    user_id: int,
    target_role: Optional[str] = None,
    conn=Depends(get_conn)
):
    """
    Get AI-generated career path matches based on user profile.
    """
    if not get_user(conn, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Gather user data from various analyses
    skills_data = {}
    analysis_data = {}
    
    with conn.cursor() as cur:
        # Get skills analysis
        cur.execute(
            "SELECT analysis_data FROM skills_analysis WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        row = cur.fetchone()
        if row and row.get("analysis_data"):
            skills_data = json.loads(row["analysis_data"])
        
        # Get resume analysis
        cur.execute(
            "SELECT analysis_data FROM resume_analysis WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        row = cur.fetchone()
        if row and row.get("analysis_data"):
            analysis_data = json.loads(row["analysis_data"])
    
    if not skills_data and not analysis_data:
        raise HTTPException(
            status_code=404,
            detail="No profile data found. Please upload a resume first."
        )
    
    # Extract relevant info for career matching
    all_skills = []
    all_skills.extend(skills_data.get("core_technical_skills", []))
    all_skills.extend(skills_data.get("soft_skills", []))
    
    experience_summary = analysis_data.get("career_progression_pattern", "")
    interests = skills_data.get("potential_career_directions", [])
    
    # Generate career matches
    matches = match_careers(
        skills=all_skills[:20],  # Limit context
        experience_summary=experience_summary[:500] if experience_summary else "",
        current_role="",  # Could be extracted from resume
        interests=interests[:5] if interests else []
    )
    
    return {
        "user_id": user_id,
        "skills_analyzed": len(all_skills),
        "career_matches": matches
    }


@app.post("/careers/roadmap")
@limiter.limit(settings.RATE_LIMIT)
def create_transition_roadmap(
    request: Request,
    current_role: str = Query(..., description="Your current job title"),
    target_role: str = Query(..., description="Your target career"),
    timeline: str = Query("6-12 months", description="Desired transition timeline"),
    user_id: Optional[int] = None,
    conn=Depends(get_conn)
):
    """
    Generate a detailed career transition roadmap.
    """
    current_skills = []
    
    # If user_id provided, get their skills
    if user_id:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT analysis_data FROM skills_analysis WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            row = cur.fetchone()
            if row and row.get("analysis_data"):
                skills_data = json.loads(row["analysis_data"])
                current_skills = skills_data.get("core_technical_skills", [])
    
    # Generate roadmap
    roadmap = get_transition_roadmap(
        current_role=current_role,
        target_role=target_role,
        current_skills=current_skills[:15],
        timeline=timeline
    )
    
    return {
        "current_role": current_role,
        "target_role": target_role,
        "timeline": timeline,
        "roadmap": roadmap
    }