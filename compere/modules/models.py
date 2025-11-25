from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from .database import Base


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    image_urls = Column(JSON)  # Store as JSON array
    rating = Column(Float, default=1500.0)

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    entity1_id = Column(Integer, ForeignKey("entities.id"))
    entity2_id = Column(Integer, ForeignKey("entities.id"))
    selected_entity_id = Column(Integer, ForeignKey("entities.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MABState(Base):
    __tablename__ = "mab_states"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), unique=True)
    arm_index = Column(Integer)
    count = Column(Integer, default=0)
    value = Column(Float, default=0.0)
    total_count = Column(Integer, default=0)

# Pydantic models for API responses
class EntityCreate(BaseModel):
    name: str
    description: str
    image_urls: List[str]

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) > 200:
            raise ValueError('Name cannot exceed 200 characters')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description cannot exceed 1000 characters')
        return v or ""

    @validator('image_urls')
    def validate_image_urls(cls, v):
        if not isinstance(v, list):
            raise ValueError('Image URLs must be a list')
        if len(v) > 10:
            raise ValueError('Cannot have more than 10 image URLs')
        for url in v:
            if not isinstance(url, str) or not url.strip():
                raise ValueError('Image URLs must be non-empty strings')
        return v

class EntityOut(BaseModel):
    id: int
    name: str
    description: str
    image_urls: List[str]
    rating: float

    class Config:
        from_attributes = True

class EntityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_urls: Optional[List[str]] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Name cannot be empty')
            if len(v.strip()) > 200:
                raise ValueError('Name cannot exceed 200 characters')
            return v.strip()
        return v

    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Description cannot exceed 1000 characters')
        return v

    @validator('image_urls')
    def validate_image_urls(cls, v):
        if v is not None:
            if not isinstance(v, list):
                raise ValueError('Image URLs must be a list')
            if len(v) > 10:
                raise ValueError('Cannot have more than 10 image URLs')
            for url in v:
                if not isinstance(url, str) or not url.strip():
                    raise ValueError('Image URLs must be non-empty strings')
        return v

class ComparisonCreate(BaseModel):
    entity1_id: int
    entity2_id: int
    selected_entity_id: int

class ComparisonOut(BaseModel):
    id: int
    entity1_id: int
    entity2_id: int
    selected_entity_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str

class NextComparisonResponse(BaseModel):
    entity1: EntityOut
    entity2: EntityOut
