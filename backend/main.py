# /backend/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers.auth_router import router as auth_router 
from anyio import to_thread


#create all tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Sync DB table creation (thread-safe)
    await to_thread.run_sync(lambda: Base.metadata.create_all(bind=engine))
    yield
    # Shutdown: (e.g., close pools)
    # await engine.dispose()
    
    
# Initialize fastapi app
app = FastAPI(lifespan=lifespan,
    title="LotusLynx"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=("*"),
    allow_methods=("*"),
    allow_headers=("*")
)    

# Include routers
app.include_router(auth_router, tags=["Authentication"])

# read route
@app.get("/")
def read_root():
    return {"Message": "Welcome to LotusLynx.."}

# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}