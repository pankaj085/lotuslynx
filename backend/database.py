# backend/databse.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load env variables from .env
load_dotenv()

# get DB_URL from .enc
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# ensures SQLALCHEMY_DATABASE_URL is not None before passing it to create_engine. 
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# create engine 
engine = create_engine(SQLALCHEMY_DATABASE_URL)

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