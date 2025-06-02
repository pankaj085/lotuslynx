# backend/routers/auth_router.py

# required imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session


# local imports
from core.auth import (
    get_password_hash,
    authenticate_user,
    create_tokens,
    get_current_user,
    Token
)
from core.config import settings
from database import get_db
from models.user import User
from schemas.user import(
    UserResponse,
    UserCreate
)


# Setup & Initialize router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# --------------------------------
# register endpoint
# --------------------------------
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with:
    - **username**: Unique username
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars)
    """
    #Check for existing username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    #check for existing email
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username = user_data.username,
        email = user_data.email,
        hashed_password = hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# --------------------------------
# login endpoint
# --------------------------------
@router.post(
    "/login",
    response_model=Token,
    summary="Authenticated user"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return tokens:
    - **username**: Your username
    - **password**: Your password
    Returns:
    - **access_token**: JWT for API access
    - **refresh_token**: Token to get new access tokens
    - **token_type**: Always 'bearer'
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    return create_tokens(str(user.username))

# --------------------------------
# Refresh Token Endpoint
# --------------------------------

@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token"
)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Get new access token using refresh token
    """
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")
        
        username = payload.get("sub")
        if not isinstance(username, str):
            raise JWTError("Invalid token: missing or invalid username")
    
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise JWTError("User not found")
            
        return create_tokens(username)  # Now username is guaranteed to be str
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
# --------------------------------
# /user/me endpoint (protected route)
# --------------------------------
@router.post(
    "/me",
    response_model=UserResponse,
    summary="Get current user credentials"
)
async def read_user_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get details of the currently authenticated user
    """
    return current_user
