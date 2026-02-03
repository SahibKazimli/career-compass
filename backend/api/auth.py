"""
Authentication module for Career Compass.
Handles JWT tokens, password hashing, and user authentication.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

from backend.config import settings
from backend.db.pg import get_conn

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


# Pydantic models for auth endpoints
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    user_id: int
    email: str
    name: str
    created_at: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# Password utilities using bcrypt directly
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# JWT utilities
def create_access_token(user_id: int, email: str) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Authentication dependency
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    conn=Depends(get_conn)
) -> dict:
    """
    Dependency to get the current authenticated user.
    Returns user data or raises 401 if not authenticated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload.get("sub"))
    
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id, email, name, created_at FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cur.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return dict(user)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    conn=Depends(get_conn)
) -> Optional[dict]:
    """
    Dependency to optionally get the current user.
    Returns None if not authenticated (for public endpoints).
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, conn)
    except HTTPException:
        return None


# Database operations for auth
def get_user_by_email_with_password(conn, email: str) -> Optional[dict]:
    """Get user by email including password hash."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id, email, name, password_hash, created_at FROM users WHERE email = %s",
            (email,)
        )
        return cur.fetchone()


def create_user_with_password(conn, email: str, name: str, password_hash: str) -> int:
    """Create a new user with password hash."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (email, name, password_hash) 
            VALUES (%s, %s, %s) 
            RETURNING user_id
            """,
            (email, name, password_hash)
        )
        conn.commit()
        result = cur.fetchone()
        return result["user_id"]


def update_user_password(conn, user_id: int, password_hash: str) -> bool:
    """Update user's password hash."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (password_hash, user_id)
        )
        conn.commit()
        return cur.rowcount > 0


def delete_user_account(conn, user_id: int) -> bool:
    """Delete a user account and all associated data."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        return cur.rowcount > 0
