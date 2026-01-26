from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .config import get_elo_k_factor
from .database import get_db
from .models import Entity, EntityOut

router = APIRouter()


def expected_score(rating_a: float, rating_b: float) -> float:
    """Calculate expected score for entity A against entity B."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_elo_ratings(db: Session, entity1: Entity, entity2: Entity, winner_id: int) -> None:
    """Update Elo ratings for two entities based on comparison result."""
    k_factor = get_elo_k_factor()
    expected_a = expected_score(entity1.rating, entity2.rating)
    expected_b = 1 - expected_a

    if winner_id == entity1.id:
        score_a, score_b = 1, 0
    elif winner_id == entity2.id:
        score_a, score_b = 0, 1
    else:
        score_a, score_b = 0.5, 0.5

    entity1.rating += k_factor * (score_a - expected_a)
    entity2.rating += k_factor * (score_b - expected_b)

    db.commit()


@router.get("/ratings", response_model=list[EntityOut])
def get_ratings(db: Session = Depends(get_db)):
    """Get all entities sorted by rating (leaderboard)"""
    return db.query(Entity).order_by(Entity.rating.desc()).all()
