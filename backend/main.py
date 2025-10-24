from fastapi import FastAPI, UploadFile, File, Depends
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


    