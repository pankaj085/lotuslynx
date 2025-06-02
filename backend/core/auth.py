# backend/core/auth.py
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Local imports
from core.config import settings
from models.user import User
from database import get_db

# -----------------------------
# Security Setup
# -----------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scheme_name="JWT"
)

# -----------------------------
# Models
# -----------------------------

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None

# -----------------------------
# Core Authentication Utilities
# -----------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Securely verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a secure password hash using bcrypt."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generate a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_DAYS)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generate a JWT refresh token with longer expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# -----------------------------
# User Authentication
# -----------------------------

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Verify user credentials against database."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, str(user.hashed_password)):
        return None
    return user

# -----------------------------
# Dependency Injections
# -----------------------------

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """Dependency to get the current authenticated user from JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise credentials_exception from e

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Dependency to verify user is active."""
    if current_user.disabled:  # Add this field to User model if needed
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# -----------------------------
# Token Management
# -----------------------------

def create_tokens(username: str) -> Token:
    """Generate both access and refresh tokens."""
    return Token(
        access_token=create_access_token({"sub": username}),
        refresh_token=create_refresh_token({"sub": username}),
        token_type="bearer"
    )

def validate_token(token: str) -> dict:
    """Validate and decode a JWT token with type checking."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") not in ["access", "refresh"]:
            raise JWTError("Invalid token type")
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )