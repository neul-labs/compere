from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from .database import get_db
from .models import Entity

router = APIRouter()

class EntityCreate(BaseModel):
    name: str
    description: str
    image_urls: List[str]

@router.post("/entities/", response_model=Entity)
def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    db_entity = Entity(**entity.dict())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity

@router.get("/entities/{entity_id}", response_model=Entity)
def read_entity(entity_id: int, db: Session = Depends(get_db)):
    db_entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return db_entity
