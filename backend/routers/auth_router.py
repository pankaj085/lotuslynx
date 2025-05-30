# backend/routers/auth_router.py

# required imports
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

# local imports
from core.auth import get_password_hash, authenticate_user, create_access_token, get_current_user
from database import get_db
from models.user import User
from schemas.user import UserResponse, UserCreate


# Setup & Initialize router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# --------------------------------
# register endpoint
# --------------------------------
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    
    # check if username & email exists already
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already taken"
        )
        
    existig_email = db.query(User).filter(User.email == user_data.email).first()
    if existig_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email already registerd"
        )
        
    # hash password & create user
    hashed_password = get_password_hash(user_data.password)
    
    # Build user without raw password
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password = hashed_password
    )
    
    # save the data in db
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
    
# --------------------------------
# login endpoint
# --------------------------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access token": access_token, "token type": "Bearer"}
    
# --------------------------------
# /user/me endpoint (protected route)
# --------------------------------
@router.post("/user/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user
