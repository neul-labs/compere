from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import numpy as np
from math import sqrt, log

from .database import get_db
from .models import Entity, Comparison, MABState

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
                mab_state = MABState(
                    entity_id=entity.id,
                    arm_index=i,
                    count=0,
                    value=0.0,
                    total_count=0
                )
                self.db.add(mab_state)
        self.db.commit()

    def select_arm(self):
        """Select arm using UCB algorithm"""
        states = self.db.query(MABState).all()
        if not states:
            return None

        total_count = sum(state.total_count for state in states)
        if total_count == 0:
            # If no trials yet, select randomly
            return states[0].entity_id

        ucb_values = {}
        for state in states:
            if state.count == 0:
                return state.entity_id
            ucb_values[state.entity_id] = state.value + sqrt(2 * log(total_count) / state.count)

        return max(ucb_values, key=ucb_values.get)

    def update(self, entity_id: int, reward: float):
        """Update MAB state for given entity"""
        state = self.db.query(MABState).filter(MABState.entity_id == entity_id).first()
        if state:
            state.count += 1
            n = state.count
            state.value = ((n - 1) / n) * state.value + (1 / n) * reward
            state.total_count += 1
            self.db.commit()

@router.get("/mab/next_comparison")
def get_next_comparison(db: Session = Depends(get_db)):
    """Get next comparison using MAB algorithm"""
    entities = db.query(Entity).all()
    if len(entities) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 entities for comparison")

    ucb = UCB(db)

    entity1_id = ucb.select_arm()
    entity2_id = ucb.select_arm()

    # Ensure we get two different entities
    attempts = 0
    while entity2_id == entity1_id and attempts < 10:
        entity2_id = ucb.select_arm()
        attempts += 1

    if entity2_id == entity1_id:
        # Fallback: just pick two different entities
        entity_ids = [e.id for e in entities]
        entity1_id, entity2_id = entity_ids[0], entity_ids[1]

    entity1 = db.query(Entity).get(entity1_id)
    entity2 = db.query(Entity).get(entity2_id)

    return {"entity1": entity1, "entity2": entity2}

@router.post("/mab/update")
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