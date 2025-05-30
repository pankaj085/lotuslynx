# /backend/main.py

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from database import engine, Base
from routers.auth_router  import router as auth_router

#create all tables
Base.metadata.create_all(bind=engine)

# Initialize fastapi app
app = FastAPI(
    title="LotusLynx",
    description="An E-commerce Platform - Authentication & User Management",
    version="1.0.0"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# include routers
app.include_router(auth_router)

# read route
@app.get("/")
def read_root():
    return {"Message": "Welcome to LotusLynx.."}