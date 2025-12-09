import os
import random
from math import log, sqrt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import (
    Comparison,
    Entity,
    MABState,
    MessageResponse,
    NextComparisonResponse,
)

# UCB/MAB Configuration
UCB_EXPLORATION_CONSTANT = float(os.getenv("UCB_EXPLORATION_CONSTANT", "1.414"))
UCB_UNEXPLORED_WEIGHT = float(os.getenv("UCB_UNEXPLORED_WEIGHT", "1000.0"))
PAIRING_UCB_WEIGHT = float(os.getenv("PAIRING_UCB_WEIGHT", "0.3"))
PAIRING_SIMILARITY_WEIGHT = float(os.getenv("PAIRING_SIMILARITY_WEIGHT", "0.4"))
PAIRING_RANDOM_WEIGHT = float(os.getenv("PAIRING_RANDOM_WEIGHT", "0.3"))
PAIRING_RATING_THRESHOLD = float(os.getenv("PAIRING_RATING_THRESHOLD", "200.0"))
RECENT_COMPARISON_LIMIT = int(os.getenv("RECENT_COMPARISON_LIMIT", "5"))

router = APIRouter()


class UCB:
    def __init__(self, db: Session):
        self.db = db
        self._initialize_states()

    def _initialize_states(self):
        """Initialize MAB states for all entities"""
        entities = self.db.query(Entity).all()
        for i, entity in enumerate(entities):
            existing_state = self.db.query(MABState).filter(MABState.entity_id == entity.id).first()
            if not existing_state:
                mab_state = MABState(entity_id=entity.id, arm_index=i, count=0, value=0.0, total_count=0)
                self.db.add(mab_state)
        self.db.commit()

    def get_ucb_scores(self):
        """Calculate UCB scores for all entities"""
        states = self.db.query(MABState).all()
        if not states:
            return {}

        total_count = sum(state.total_count for state in states)
        if total_count == 0:
            total_count = 1  # Avoid log(0)

        ucb_scores = {}
        for state in states:
            if state.count == 0:
                # Entities with no comparisons get infinite UCB (prioritize exploration)
                ucb_scores[state.entity_id] = float("inf")
            else:
                ucb_scores[state.entity_id] = state.value + UCB_EXPLORATION_CONSTANT * sqrt(
                    2 * log(total_count) / state.count
                )

        return ucb_scores

    def select_pair(self, exclude_recent=True):
        """Select a pair of entities for comparison using UCB"""
        entities = self.db.query(Entity).all()
        if len(entities) < 2:
            return None, None

        ucb_scores = self.get_ucb_scores()

        # Select first entity using weighted random based on UCB scores
        # This adds exploration while still favoring high UCB entities
        weights = []
        for entity in entities:
            score = ucb_scores.get(entity.id, 0)
            # Handle infinite scores (unexplored entities)
            if score == float("inf"):
                weights.append(UCB_UNEXPLORED_WEIGHT)  # High weight for unexplored
            else:
                weights.append(max(score, 0.1))  # Ensure positive weight

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Weighted random selection for first entity
        entity1 = random.choices(entities, weights=weights, k=1)[0]

        # For second entity, use a mixed strategy:
        # 1. Prioritize entities with fewer comparisons against entity1
        # 2. Consider rating similarity for informative comparisons
        # 3. Add some randomness for variety

        remaining_entities = [e for e in entities if e.id != entity1.id]

        if exclude_recent:
            # Get entities that entity1 was recently compared with
            recent_comparisons = (
                self.db.query(Comparison)
                .filter((Comparison.entity1_id == entity1.id) | (Comparison.entity2_id == entity1.id))
                .order_by(Comparison.created_at.desc())
                .limit(min(RECENT_COMPARISON_LIMIT, len(remaining_entities) - 1))
                .all()
            )

            recent_opponent_ids = set()
            for comp in recent_comparisons:
                if comp.entity1_id == entity1.id:
                    recent_opponent_ids.add(comp.entity2_id)
                else:
                    recent_opponent_ids.add(comp.entity1_id)

            # Filter out recently compared entities if we have enough alternatives
            non_recent = [e for e in remaining_entities if e.id not in recent_opponent_ids]
            if non_recent:
                remaining_entities = non_recent

        # Score remaining entities for selection
        entity_scores = []
        for entity in remaining_entities:
            score = 0

            # Factor 1: UCB score (exploration value)
            score += ucb_scores.get(entity.id, 0) * PAIRING_UCB_WEIGHT

            # Factor 2: Rating similarity (more informative comparisons)
            rating_diff = abs(entity1.rating - entity.rating)
            # Prefer entities within threshold rating points
            if rating_diff < PAIRING_RATING_THRESHOLD:
                score += (PAIRING_RATING_THRESHOLD - rating_diff) / PAIRING_RATING_THRESHOLD * PAIRING_SIMILARITY_WEIGHT

            # Factor 3: Randomness for variety
            score += random.random() * PAIRING_RANDOM_WEIGHT

            entity_scores.append((entity, score))

        # Sort by score and pick the best
        entity_scores.sort(key=lambda x: x[1], reverse=True)
        entity2 = entity_scores[0][0]

        return entity1, entity2

    def select_arm(self):
        """Select single arm using UCB algorithm (for backwards compatibility)"""
        ucb_scores = self.get_ucb_scores()
        if not ucb_scores:
            return None

        # Return entity with highest UCB score
        return max(ucb_scores, key=ucb_scores.get)

    def update(self, entity_id: int, reward: float):
        """Update MAB state for given entity"""
        state = self.db.query(MABState).filter(MABState.entity_id == entity_id).first()
        if state:
            state.count += 1
            n = state.count
            state.value = ((n - 1) / n) * state.value + (1 / n) * reward

            # Update total_count for all states
            all_states = self.db.query(MABState).all()
            for s in all_states:
                s.total_count = sum(st.count for st in all_states)

            self.db.commit()


@router.get("/mab/next_comparison", response_model=NextComparisonResponse)
def get_mab_next_comparison(db: Session = Depends(get_db)):
    """Get next comparison using MAB algorithm"""
    entities = db.query(Entity).all()
    if len(entities) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 entities for comparison")

    ucb = UCB(db)
    entity1, entity2 = ucb.select_pair(exclude_recent=True)

    if entity1 is None or entity2 is None:
        # Fallback: random selection
        selected = random.sample(entities, 2)
        entity1, entity2 = selected[0], selected[1]

    return {"entity1": entity1, "entity2": entity2}


@router.post("/mab/update", response_model=MessageResponse)
def update_mab(comparison_id: int, db: Session = Depends(get_db)):
    """Update MAB state based on comparison result"""
    comparison = db.query(Comparison).get(comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")

    ucb = UCB(db)

    # Update UCB based on the comparison result
    if comparison.selected_entity_id == comparison.entity1_id:
        ucb.update(comparison.entity1_id, 1.0)
        ucb.update(comparison.entity2_id, 0.0)
    elif comparison.selected_entity_id == comparison.entity2_id:
        ucb.update(comparison.entity1_id, 0.0)
        ucb.update(comparison.entity2_id, 1.0)
    else:
        # Tie case
        ucb.update(comparison.entity1_id, 0.5)
        ucb.update(comparison.entity2_id, 0.5)

    return {"message": "MAB updated successfully"}
