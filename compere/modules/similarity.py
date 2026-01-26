"""
Entity similarity calculations for intelligent pairing.
"""

from collections.abc import Sequence

import numpy as np
from fastapi import APIRouter, Depends
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import get_db
from .errors import handle_database_error
from .models import Entity, EntityOut

router = APIRouter()

# Module-level vectorizer for consistent embeddings
_vectorizer: TfidfVectorizer | None = None


def _get_entity_text(entity: Entity) -> str:
    """Extract text representation from entity for embedding."""
    parts = [entity.name]
    if entity.description:
        parts.append(entity.description)
    return " ".join(parts)


def generate_embeddings(entities: Sequence[Entity]) -> np.ndarray:
    """Generate TF-IDF embeddings for a list of entities.

    Uses TF-IDF vectorization on entity name and description to create
    meaningful text-based embeddings for similarity comparison.

    Args:
        entities: Sequence of Entity objects to embed

    Returns:
        numpy array of shape (n_entities, n_features) containing embeddings
    """
    global _vectorizer

    if len(entities) == 0:
        return np.array([])

    # Extract text from entities
    texts = [_get_entity_text(entity) for entity in entities]

    # Create or refit vectorizer
    # Note: In production, consider using pre-trained embeddings
    # (e.g., sentence-transformers, OpenAI embeddings) for better quality
    _vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words="english",
        ngram_range=(1, 2),
    )

    try:
        embeddings = _vectorizer.fit_transform(texts).toarray()
    except ValueError:
        # If vectorization fails (e.g., all stop words), return random embeddings
        embeddings = np.random.rand(len(entities), 100)

    return embeddings


def get_dissimilar_entities(db: Session, n: int = 2) -> list[Entity]:
    """Get entities that are most dissimilar for meaningful comparisons.

    Uses TF-IDF embeddings and cosine similarity to find the pair of
    entities that are most different from each other.

    Args:
        db: Database session
        n: Number of entities to return (default 2)

    Returns:
        List of n most dissimilar entities
    """
    entities = db.query(Entity).all()

    if len(entities) < n:
        return list(entities)

    if len(entities) == n:
        return list(entities)

    # Generate embeddings for all entities
    embeddings = generate_embeddings(entities)

    # Calculate pairwise cosine similarity
    similarities = cosine_similarity(embeddings)

    # Set diagonal to 1 to avoid selecting same entity
    np.fill_diagonal(similarities, 1.0)

    # Find the pair with lowest similarity (most dissimilar)
    most_dissimilar_pair = np.unravel_index(np.argmin(similarities), similarities.shape)

    return [entities[most_dissimilar_pair[0]], entities[most_dissimilar_pair[1]]]


@router.get("/dissimilar_entities", response_model=list[EntityOut])
def get_dissimilar_entities_route(db: Session = Depends(get_db)) -> list[Entity]:
    """Get dissimilar entities for comparison.

    Returns a pair of entities that are most dissimilar based on their
    text content (name and description). This helps ensure meaningful
    comparisons between different types of entities.
    """
    try:
        return get_dissimilar_entities(db)
    except SQLAlchemyError as e:
        handle_database_error(e, "get dissimilar entities")
