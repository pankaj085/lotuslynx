# backend/databse.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load env variables from .env
load_dotenv()

# get DB_URL from .enc
DATABASE_URL = os.getenv("DATABASE_URL")

# ensures DATABASE_URL is not None before passing it to create_engine. 
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# create engine 
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True
)

# sesseionlocal class - will be usedin dependencies
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class - used in models.py
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()