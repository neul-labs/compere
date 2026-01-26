"""
Comparison management and creation.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import get_db
from .errors import handle_database_error, handle_not_found, handle_validation_error
from .models import (
    Comparison,
    ComparisonCreate,
    ComparisonOut,
    Entity,
    NextComparisonResponse,
)
from .rating import update_elo_ratings
from .similarity import get_dissimilar_entities

router = APIRouter()


@router.post("/comparisons/", response_model=ComparisonOut)
async def create_comparison(
    comparison: ComparisonCreate,
    db: Session = Depends(get_db),
) -> Comparison:
    """Create a new comparison and update ratings."""
    try:
        # Check if entities exist
        entity1 = db.query(Entity).filter(Entity.id == comparison.entity1_id).first()
        entity2 = db.query(Entity).filter(Entity.id == comparison.entity2_id).first()

        if not entity1:
            handle_not_found("Entity", comparison.entity1_id)
        if not entity2:
            handle_not_found("Entity", comparison.entity2_id)

        # Validate selected entity
        if comparison.selected_entity_id not in [comparison.entity1_id, comparison.entity2_id]:
            handle_validation_error("Selected entity must be one of the compared entities")

        # Create comparison
        db_comparison = Comparison(**comparison.model_dump())
        db.add(db_comparison)
        db.commit()
        db.refresh(db_comparison)

        # Update Elo ratings
        update_elo_ratings(db, entity1, entity2, comparison.selected_entity_id)

        return db_comparison
    except SQLAlchemyError as e:
        db.rollback()
        handle_database_error(e, "create comparison")


@router.get("/comparisons/", response_model=list[ComparisonOut])
def list_comparisons(
    skip: int = Query(0, ge=0, description="Number of comparisons to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of comparisons to return"),
    entity_id: int | None = Query(None, description="Filter by entity ID"),
    db: Session = Depends(get_db),
) -> list[Comparison]:
    """Get list of comparisons with optional filtering and pagination."""
    try:
        query = db.query(Comparison)

        if entity_id:
            query = query.filter(
                (Comparison.entity1_id == entity_id) | (Comparison.entity2_id == entity_id)
            )

        comparisons = query.order_by(Comparison.created_at.desc()).offset(skip).limit(limit).all()
        return comparisons
    except SQLAlchemyError as e:
        handle_database_error(e, "list comparisons")


# NOTE: This route MUST be defined BEFORE /comparisons/{comparison_id}
# otherwise "next" gets interpreted as a comparison_id parameter
@router.get("/comparisons/next", response_model=NextComparisonResponse)
async def get_next_comparison(db: Session = Depends(get_db)) -> dict:
    """Get next pair of entities for comparison using similarity."""
    try:
        entities = get_dissimilar_entities(db)
        if len(entities) < 2:
            handle_validation_error("Not enough entities for comparison (need at least 2)")
        return {"entity1": entities[0], "entity2": entities[1]}
    except SQLAlchemyError as e:
        handle_database_error(e, "get next comparison")


@router.get("/comparisons/{comparison_id}", response_model=ComparisonOut)
def get_comparison(comparison_id: int, db: Session = Depends(get_db)) -> Comparison:
    """Get a single comparison by ID."""
    try:
        comparison = db.query(Comparison).filter(Comparison.id == comparison_id).first()
        if comparison is None:
            handle_not_found("Comparison", comparison_id)
        return comparison
    except SQLAlchemyError as e:
        handle_database_error(e, "get comparison")
