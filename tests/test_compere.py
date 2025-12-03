"""
Unit tests for the Compere library.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from compere.main import app
from compere.modules.database import Base
from compere.modules.mab import UCB
from compere.modules.models import (
    Comparison,
    ComparisonCreate,
    Entity,
    EntityCreate,
    MABState,
)
from compere.modules.rating import expected_score, update_elo_ratings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def sample_entities(db_session):
    """Create sample entities for testing"""
    entity1 = EntityCreate(
        name="Restaurant A",
        description="A fine dining restaurant",
        image_urls=["http://example.com/a.jpg"]
    )
    entity2 = EntityCreate(
        name="Restaurant B",
        description="A casual dining spot",
        image_urls=["http://example.com/b.jpg"]
    )

    db_entity1 = Entity(**entity1.dict())
    db_entity2 = Entity(**entity2.dict())

    db_session.add(db_entity1)
    db_session.add(db_entity2)
    db_session.commit()
    db_session.refresh(db_entity1)
    db_session.refresh(db_entity2)

    return db_entity1, db_entity2

class TestEntityOperations:
    """Test entity CRUD operations"""

    def test_create_entity(self, db_session):
        """Test entity creation"""
        entity_data = EntityCreate(
            name="Test Restaurant",
            description="A test restaurant",
            image_urls=["http://example.com/test.jpg"]
        )

        entity = Entity(**entity_data.dict())
        db_session.add(entity)
        db_session.commit()
        db_session.refresh(entity)

        assert entity.id is not None
        assert entity.name == "Test Restaurant"
        assert entity.rating == 1500.0
        assert entity.image_urls == ["http://example.com/test.jpg"]

    def test_entity_validation(self):
        """Test entity validation"""
        # Test empty name
        with pytest.raises(ValueError, match="Name cannot be empty"):
            EntityCreate(name="", description="Test", image_urls=[])

        # Test long name
        with pytest.raises(ValueError, match="Name cannot exceed 200 characters"):
            EntityCreate(name="x" * 201, description="Test", image_urls=[])

        # Test invalid image URLs
        with pytest.raises(ValueError, match="Image URLs must be non-empty strings"):
            EntityCreate(name="Test", description="Test", image_urls=[""])

class TestRatingSystem:
    """Test Elo rating system"""

    def test_expected_score(self):
        """Test expected score calculation"""
        score = expected_score(1500, 1500)
        assert abs(score - 0.5) < 0.001

        score = expected_score(1600, 1400)
        assert score > 0.5

    def test_elo_update(self, db_session, sample_entities):
        """Test Elo rating updates"""
        entity1, entity2 = sample_entities
        initial_rating1 = entity1.rating
        initial_rating2 = entity2.rating

        # Entity1 wins
        update_elo_ratings(db_session, entity1, entity2, entity1.id)

        assert entity1.rating > initial_rating1
        assert entity2.rating < initial_rating2
        assert abs((entity1.rating + entity2.rating) - (initial_rating1 + initial_rating2)) < 0.001

class TestComparisons:
    """Test comparison operations"""

    def test_create_comparison(self, db_session, sample_entities):
        """Test comparison creation"""
        entity1, entity2 = sample_entities

        comparison_data = ComparisonCreate(
            entity1_id=entity1.id,
            entity2_id=entity2.id,
            selected_entity_id=entity1.id
        )

        comparison = Comparison(**comparison_data.dict())
        db_session.add(comparison)
        db_session.commit()
        db_session.refresh(comparison)

        assert comparison.id is not None
        assert comparison.entity1_id == entity1.id
        assert comparison.entity2_id == entity2.id
        assert comparison.selected_entity_id == entity1.id

class TestMAB:
    """Test Multi-Armed Bandit implementation"""

    def test_ucb_initialization(self, db_session, sample_entities):
        """Test UCB initialization"""
        _ucb = UCB(db_session)  # noqa: F841 - UCB init creates MAB states as side effect

        # Check that MAB states are created
        states = db_session.query(MABState).all()
        assert len(states) == 2

        for state in states:
            assert state.count == 0
            assert state.value == 0.0

    def test_ucb_selection(self, db_session, sample_entities):
        """Test UCB arm selection"""
        ucb = UCB(db_session)

        # First selection should return an entity ID
        entity_id = ucb.select_arm()
        assert entity_id in [entity.id for entity in sample_entities]

    def test_ucb_update(self, db_session, sample_entities):
        """Test UCB update mechanism"""
        entity1, entity2 = sample_entities
        ucb = UCB(db_session)

        # Update with reward
        ucb.update(entity1.id, 1.0)

        state = db_session.query(MABState).filter(MABState.entity_id == entity1.id).first()
        assert state.count == 1
        assert state.value == 1.0
        assert state.total_count == 1

class TestAPI:
    """Test API endpoints"""

    def test_create_entity_endpoint(self, test_client):
        """Test entity creation endpoint"""
        entity_data = {
            "name": "API Test Restaurant",
            "description": "Created via API",
            "image_urls": ["http://example.com/api.jpg"]
        }

        response = test_client.post("/entities/", json=entity_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == entity_data["name"]
        assert data["rating"] == 1500.0

    def test_list_entities_endpoint(self, test_client):
        """Test entity listing endpoint"""
        # Create a test entity first
        entity_data = {
            "name": "List Test Restaurant",
            "description": "For listing test",
            "image_urls": ["http://example.com/list.jpg"]
        }
        test_client.post("/entities/", json=entity_data)

        # Test listing
        response = test_client.get("/entities/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_ratings_endpoint(self, test_client):
        """Test ratings endpoint"""
        response = test_client.get("/ratings")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    run_tests()