# main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .modules.database import Base, engine
from .modules.models import Entity, Comparison, MABState  # noqa: F401 - Import models to register them with SQLAlchemy
from .modules.entity import router as EntityRouter
from .modules.comparison import router as ComparisonRouter
from .modules.rating import router as RatingRouter
from .modules.similarity import router as SimilarityRouter
from .modules.mab import router as MABRouter
from .modules.auth import router as AuthRouter
from .modules.config import get_config
from .modules.middleware import create_rate_limit_middleware, create_logging_middleware

load_dotenv()

# Validate environment and setup logging
config = get_config()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Compere",
    description="An advanced comparative rating system that leverages Multi-Armed Bandit (MAB) algorithms and Elo ratings to provide fair and efficient entity comparisons.",
    version="0.1.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
rate_limit_middleware = create_rate_limit_middleware()
if rate_limit_middleware.enabled:
    app.add_middleware(
        type(rate_limit_middleware),
        calls=rate_limit_middleware.calls,
        period=rate_limit_middleware.period,
        enabled=rate_limit_middleware.enabled
    )
    logger.info(f"Rate limiting enabled: {rate_limit_middleware.calls} requests per {rate_limit_middleware.period}s")

# Add logging middleware
logging_middleware = create_logging_middleware()
if logging_middleware.enabled:
    app.add_middleware(
        type(logging_middleware),
        enabled=logging_middleware.enabled
    )
    logger.info("Request logging enabled")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(AuthRouter, prefix="/auth", tags=["authentication"])
app.include_router(EntityRouter)
app.include_router(ComparisonRouter)
app.include_router(RatingRouter)
app.include_router(SimilarityRouter)
app.include_router(MABRouter)

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Compere application")
    logger.info(f"Environment: {config.get('environment')}")
    logger.info(f"Database: {config.get('database_url')}")
    logger.info(f"ELO K-factor: {config.get('elo_k_factor')}")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Compere application")