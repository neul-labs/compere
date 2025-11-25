import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import get_db
from .models import Entity, EntityCreate, EntityOut, EntityUpdate, MessageResponse

# Elo configuration
ELO_INITIAL_RATING = float(os.getenv("ELO_INITIAL_RATING", "1500.0"))

router = APIRouter()

@router.post("/entities/", response_model=EntityOut)
def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    """Create a new entity"""
    try:
        db_entity = Entity(**entity.model_dump(), rating=ELO_INITIAL_RATING)
        db.add(db_entity)
        db.commit()
        db.refresh(db_entity)
        return db_entity
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/entities/", response_model=List[EntityOut])
def list_entities(
    skip: int = Query(0, ge=0, description="Number of entities to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entities to return"),
    search: Optional[str] = Query(None, description="Search in entity names and descriptions"),
    db: Session = Depends(get_db)
):
    """Get list of entities with optional search and pagination"""
    try:
        query = db.query(Entity)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Entity.name.ilike(search_term)) |
                (Entity.description.ilike(search_term))
            )

        entities = query.order_by(Entity.rating.desc()).offset(skip).limit(limit).all()
        return entities
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/entities/{entity_id}", response_model=EntityOut)
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """Get a single entity by ID"""
    try:
        db_entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if db_entity is None:
            raise HTTPException(status_code=404, detail="Entity not found")
        return db_entity
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/entities/{entity_id}", response_model=EntityOut)
def update_entity(entity_id: int, entity_update: EntityUpdate, db: Session = Depends(get_db)):
    """Update an existing entity"""
    try:
        db_entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if db_entity is None:
            raise HTTPException(status_code=404, detail="Entity not found")

        update_data = entity_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_entity, field, value)

        db.commit()
        db.refresh(db_entity)
        return db_entity
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/entities/{entity_id}", response_model=MessageResponse)
def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    """Delete an entity"""
    try:
        db_entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if db_entity is None:
            raise HTTPException(status_code=404, detail="Entity not found")

        db.delete(db_entity)
        db.commit()
        return {"message": "Entity deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
