from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core.config import settings
from models.user import User
from dependencies.database import get_db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scheme_name="JWT"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current user from JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to check if user is active"""
    if current_user.disabled:  # Add this field to User model if needed
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user