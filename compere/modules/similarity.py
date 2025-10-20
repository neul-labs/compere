from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .database import get_db
from .models import Entity

router = APIRouter()

def generate_embedding(entity: Entity):
    # This is a placeholder function. In a real implementation, you would use
    # an LLM or another ML model to generate embeddings based on the entity's
    # text and image data.
    return np.random.rand(100)  # Return a random 100-dimensional vector

def get_dissimilar_entities(db: Session, n=2):
    """Get entities that are most dissimilar for meaningful comparisons"""
    entities = db.query(Entity).all()
    if len(entities) < n:
        return entities

    embeddings = np.array([generate_embedding(entity) for entity in entities])
    similarities = cosine_similarity(embeddings)

    # Set diagonal to 1 to avoid selecting same entity
    np.fill_diagonal(similarities, 1)

    # Select two entities with lowest similarity (most dissimilar)
    most_dissimilar_pair = np.unravel_index(np.argmin(similarities), similarities.shape)
    return [entities[most_dissimilar_pair[0]], entities[most_dissimilar_pair[1]]]

def get_similar_entities(db: Session, n=2):
    """Legacy function - now returns dissimilar entities for better comparisons"""
    return get_dissimilar_entities(db, n)

@router.get("/similar_entities")
def get_similar_entities_route(db: Session = Depends(get_db)):
    """Get dissimilar entities for comparison (renamed for backward compatibility)"""
    return get_similar_entities(db)

@router.get("/dissimilar_entities")
def get_dissimilar_entities_route(db: Session = Depends(get_db)):
    """Get dissimilar entities for comparison"""
    return get_dissimilar_entities(db)