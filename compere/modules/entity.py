from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import get_elo_initial_rating
from .database import get_db
from .errors import handle_database_error, handle_not_found
from .models import Entity, EntityCreate, EntityOut, EntityUpdate, MessageResponse

router = APIRouter()


@router.post("/entities/", response_model=EntityOut)
def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    """Create a new entity"""
    try:
        db_entity = Entity(**entity.model_dump(), rating=get_elo_initial_rating())
        db.add(db_entity)
        db.commit()
        db.refresh(db_entity)
        return db_entity
    except SQLAlchemyError as e:
        db.rollback()
        handle_database_error(e, "create entity")


@router.get("/entities/", response_model=list[EntityOut])
def list_entities(
    skip: int = Query(0, ge=0, description="Number of entities to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entities to return"),
    search: str | None = Query(None, description="Search in entity names and descriptions"),
    db: Session = Depends(get_db),
):
    """Get list of entities with optional search and pagination"""
    try:
        query = db.query(Entity)

        if search:
            search_term = f"%{search}%"
            query = query.filter((Entity.name.ilike(search_term)) | (Entity.description.ilike(search_term)))

        entities = query.order_by(Entity.rating.desc()).offset(skip).limit(limit).all()
        return entities
    except SQLAlchemyError as e:
        handle_database_error(e, "list entities")


@router.get("/entities/{entity_id}", response_model=EntityOut)
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """Get a single entity by ID"""
    try:
        db_entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if db_entity is None:
            handle_not_found("Entity", entity_id)
        return db_entity
    except SQLAlchemyError as e:
        handle_database_error(e, "get entity")


@router.put("/entities/{entity_id}", response_model=EntityOut)
def update_entity(entity_id: int, entity_update: EntityUpdate, db: Session = Depends(get_db)):
    """Update an existing entity"""
    try:
        db_entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if db_entity is None:
            handle_not_found("Entity", entity_id)

        update_data = entity_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_entity, field, value)

        db.commit()
        db.refresh(db_entity)
        return db_entity
    except SQLAlchemyError as e:
        db.rollback()
        handle_database_error(e, "update entity")


@router.delete("/entities/{entity_id}", response_model=MessageResponse)
def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    """Delete an entity"""
    try:
        db_entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if db_entity is None:
            handle_not_found("Entity", entity_id)

        db.delete(db_entity)
        db.commit()
        return {"message": "Entity deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        handle_database_error(e, "delete entity")
