from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import init_db, get_db, User, Resume
from contextlib import asynccontextmanager

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
    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name}


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
    content = await file.read()
    
    # Just storing PDF file name for now, parsing will be implemented later
    resume = Resume(
        user_id=user_id, 
        raw_text=f"Uploaded file: {file.filename}",
        parsed_skills=[],
        parsed_experience=[]
        embedding=[]
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    