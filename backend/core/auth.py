# backend/core/auth.py

from datetime import datetime, timedelta, timezone
from typing import Optional, cast
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Local imports
from models import User
from schemas import UserResponse
from database import SessionLocal

# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

# Setup password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load config from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES_STR = os.getenv("ACCESS_TOKEN_EXPIRE_TIME")  # in minutes

# Validate required config
if not SECRET_KEY or not ALGORITHM:
    raise ValueError("Missing required environment variables: 'SECRET_KEY' and 'ALGORITHM'")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES_STR or 30)
except (TypeError, ValueError):
    raise ValueError("ACCESS_TOKEN_EXPIRE_TIME must be a valid integer")

# -----------------------------
# Utility Functions
# -----------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=str(ALGORITHM)) #type: ignore
    return encoded_jwt

def get_user(username: str) -> Optional[User]:
    with SessionLocal() as db:
        return db.query(User).filter(User.username == username).first()

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user(username)
    if not user or not verify_password(password, cast(str, user.hashed_password)):
        return None
    return user

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[str(ALGORITHM)]) #type: ignore
        username = payload.get("sub")
        if not isinstance(username, str): 
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user