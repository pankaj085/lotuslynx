# /backend/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers.auth_router import router as auth_router
from routers.product_router import router as product_router
from anyio import to_thread
import stripe
from core.config import settings


#create all tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Sync DB table creation (thread-safe)
    await to_thread.run_sync(lambda: Base.metadata.create_all(bind=engine))
    
    # Configure Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    yield
    # Shutdown: (e.g., close pools)
    # await engine.dispose()
    
# Initialize fastapi app
app = FastAPI(
    lifespan=lifespan,
    title="LotusLynx",
    description="E-commerce platform API built with FastAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=("*"),
    allow_methods=("*"),
    allow_headers=("*")
)    

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(product_router, tags=["Products"])

# read route
@app.get("/")
def read_root():
    return {"Message": "Welcome to LotusLynx.."}

# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }