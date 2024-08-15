# main.py
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from modules.database import Base
from modules.entity import Entity, EntityRouter
from modules.comparison import ComparisonRouter
from modules.user import User, UserRouter
from modules.rating import RatingRouter
from modules.similarity import SimilarityRouter
from modules.security import SecurityRouter
from modules.mab import MABRouter

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(EntityRouter)
app.include_router(ComparisonRouter)
app.include_router(UserRouter)
app.include_router(RatingRouter)
app.include_router(SimilarityRouter)
app.include_router(SecurityRouter)
app.include_router(MABRouter)