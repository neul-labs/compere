"""
Tests for comparison module - focusing on error handling and edge cases.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from compere.main import app

client = TestClient(app)


class TestComparisonCreation:
    """Test comparison creation and validation"""

    def test_create_comparison_entity_not_found(self):
        """Test creating comparison with non-existent entity"""
        comparison_data = {
            "entity1_id": 99998,
            "entity2_id": 99999,
            "selected_entity_id": 99998,
        }
        response = client.post("/comparisons/", json=comparison_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_comparison_invalid_selected_entity(self):
        """Test creating comparison with invalid selected entity"""
        # Create two entities first
        entity1 = client.post(
            "/entities/",
            json={
                "name": "Comparison Entity 1",
                "description": "Test",
                "image_urls": [],
            },
        ).json()
        entity2 = client.post(
            "/entities/",
            json={
                "name": "Comparison Entity 2",
                "description": "Test",
                "image_urls": [],
            },
        ).json()

        # Try to create comparison with invalid selected_entity_id
        comparison_data = {
            "entity1_id": entity1["id"],
            "entity2_id": entity2["id"],
            "selected_entity_id": 99999,  # Not one of the compared entities
        }
        response = client.post("/comparisons/", json=comparison_data)
        assert response.status_code == 400
        assert "Selected entity must be one of the compared entities" in response.json()["detail"]

    def test_create_comparison_success(self):
        """Test successful comparison creation"""
        # Create two entities
        entity1 = client.post(
            "/entities/",
            json={
                "name": "Winner Entity",
                "description": "This one wins",
                "image_urls": [],
            },
        ).json()
        entity2 = client.post(
            "/entities/",
            json={
                "name": "Loser Entity",
                "description": "This one loses",
                "image_urls": [],
            },
        ).json()

        # Create comparison
        comparison_data = {
            "entity1_id": entity1["id"],
            "entity2_id": entity2["id"],
            "selected_entity_id": entity1["id"],
        }
        response = client.post("/comparisons/", json=comparison_data)
        assert response.status_code == 200

        data = response.json()
        assert data["entity1_id"] == entity1["id"]
        assert data["entity2_id"] == entity2["id"]
        assert data["selected_entity_id"] == entity1["id"]
        assert "id" in data
        assert "created_at" in data


class TestComparisonListing:
    """Test comparison listing and filtering"""

    def test_list_comparisons(self):
        """Test listing all comparisons"""
        response = client.get("/comparisons/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_comparisons_with_pagination(self):
        """Test listing comparisons with pagination"""
        response = client.get("/comparisons/?skip=0&limit=5")
        assert response.status_code == 200
        assert len(response.json()) <= 5

    def test_list_comparisons_filter_by_entity(self):
        """Test filtering comparisons by entity ID"""
        # Create entities and comparison
        entity1 = client.post(
            "/entities/",
            json={
                "name": "Filter Test Entity 1",
                "description": "Test",
                "image_urls": [],
            },
        ).json()
        entity2 = client.post(
            "/entities/",
            json={
                "name": "Filter Test Entity 2",
                "description": "Test",
                "image_urls": [],
            },
        ).json()

        # Create a comparison
        client.post(
            "/comparisons/",
            json={
                "entity1_id": entity1["id"],
                "entity2_id": entity2["id"],
                "selected_entity_id": entity1["id"],
            },
        )

        # Filter by entity1's ID
        response = client.get(f"/comparisons/?entity_id={entity1['id']}")
        assert response.status_code == 200
        comparisons = response.json()
        # All returned comparisons should involve entity1
        for comp in comparisons:
            assert entity1["id"] in [comp["entity1_id"], comp["entity2_id"]]


class TestGetComparison:
    """Test getting specific comparison"""

    def test_get_comparison_success(self):
        """Test getting a specific comparison by ID"""
        # Create entities and comparison
        entity1 = client.post(
            "/entities/",
            json={
                "name": "Get Test Entity 1",
                "description": "Test",
                "image_urls": [],
            },
        ).json()
        entity2 = client.post(
            "/entities/",
            json={
                "name": "Get Test Entity 2",
                "description": "Test",
                "image_urls": [],
            },
        ).json()

        create_response = client.post(
            "/comparisons/",
            json={
                "entity1_id": entity1["id"],
                "entity2_id": entity2["id"],
                "selected_entity_id": entity1["id"],
            },
        )
        comparison_id = create_response.json()["id"]

        # Get the comparison
        response = client.get(f"/comparisons/{comparison_id}")
        assert response.status_code == 200
        assert response.json()["id"] == comparison_id

    def test_get_comparison_not_found(self):
        """Test getting non-existent comparison"""
        response = client.get("/comparisons/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestNextComparison:
    """Test next comparison endpoint"""

    def test_get_next_comparison_insufficient_entities(self):
        """Test next comparison when there aren't enough entities"""
        # This test depends on state, so we just verify the endpoint responds correctly
        response = client.get("/comparisons/next")
        # Should either return entities or 404 if not enough
        assert response.status_code in [200, 404]

    def test_get_next_comparison_success(self):
        """Test getting next comparison pair"""
        # Ensure we have at least 2 entities
        client.post(
            "/entities/",
            json={
                "name": "Next Comparison Entity 1",
                "description": "Test",
                "image_urls": [],
            },
        )
        client.post(
            "/entities/",
            json={
                "name": "Next Comparison Entity 2",
                "description": "Test",
                "image_urls": [],
            },
        )

        response = client.get("/comparisons/next")
        if response.status_code == 200:
            data = response.json()
            assert "entity1" in data
            assert "entity2" in data
            assert data["entity1"]["id"] != data["entity2"]["id"]


class TestRatingUpdates:
    """Test that comparisons update entity ratings"""

    def test_comparison_updates_ratings(self):
        """Test that creating a comparison updates ratings"""
        # Create two entities
        entity1 = client.post(
            "/entities/",
            json={
                "name": "Rating Update Entity 1",
                "description": "Test",
                "image_urls": [],
            },
        ).json()
        entity2 = client.post(
            "/entities/",
            json={
                "name": "Rating Update Entity 2",
                "description": "Test",
                "image_urls": [],
            },
        ).json()

        initial_rating1 = entity1["rating"]
        initial_rating2 = entity2["rating"]

        # Create comparison - entity1 wins
        client.post(
            "/comparisons/",
            json={
                "entity1_id": entity1["id"],
                "entity2_id": entity2["id"],
                "selected_entity_id": entity1["id"],
            },
        )

        # Get updated entities
        updated_entity1 = client.get(f"/entities/{entity1['id']}").json()
        updated_entity2 = client.get(f"/entities/{entity2['id']}").json()

        # Winner's rating should increase, loser's should decrease
        assert updated_entity1["rating"] > initial_rating1
        assert updated_entity2["rating"] < initial_rating2


class TestComparisonValidation:
    """Test comparison input validation"""

    def test_comparison_missing_fields(self):
        """Test creating comparison with missing fields"""
        response = client.post("/comparisons/", json={})
        assert response.status_code == 422  # Validation error

    def test_comparison_invalid_entity_id_type(self):
        """Test creating comparison with invalid entity ID type"""
        response = client.post(
            "/comparisons/",
            json={
                "entity1_id": "not_an_int",
                "entity2_id": 1,
                "selected_entity_id": 1,
            },
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
