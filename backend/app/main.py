from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.seed.schemes import seed_schemes

from backend.app.api.auth import router as auth_router
from backend.app.api.profile import router as profile_router
from backend.app.api.schemes import router as schemes_router
from backend.app.api.eligibility import router as eligibility_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.emi import router as emi_router
from backend.app.api.geo import router as geo_router

from backend.app.ai.model_loader import model_loader

# Create DB Tables on startup
Base.metadata.create_all(bind=engine)

# Seed Scheme Data
db = SessionLocal()
try:
    seed_schemes(db)
finally:
    db.close()

from contextlib import asynccontextmanager
import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load local Hugging Face model in background thread when FastAPI starts up."""
    threading.Thread(
        target=model_loader.load_model,
        args=(settings.MODEL_NAME,),
        daemon=True
    ).start()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AI Government Loan Scheme Recommender for SC Beneficiaries",
    lifespan=lifespan
)

# Enable CORS for local web development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "model": settings.MODEL_NAME,
        "model_status": model_loader.get_status()
    }

# Include API Routers under /api
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(profile_router, prefix=settings.API_V1_STR)
app.include_router(schemes_router, prefix=settings.API_V1_STR)
app.include_router(eligibility_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=settings.API_V1_STR)
app.include_router(emi_router, prefix=settings.API_V1_STR)
app.include_router(geo_router, prefix=settings.API_V1_STR)

from backend.app.api.emi import calculate_emi_post, CalculationRequest

@app.post("/api/calculate")
def calculate_alias_post(data: CalculationRequest):
    return calculate_emi_post(data)


# Serve Frontend static files if frontend directory exists (mounted last)
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
