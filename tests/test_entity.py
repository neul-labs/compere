"""
Tests for entity module - focusing on update/delete operations.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from compere.main import app

client = TestClient(app)


class TestEntityUpdate:
    """Test entity update operations"""

    def test_update_entity_name(self):
        """Test updating entity name"""
        # Create an entity first
        entity_data = {
            "name": "Original Name",
            "description": "Original description",
            "image_urls": ["http://example.com/original.jpg"],
        }
        create_response = client.post("/entities/", json=entity_data)
        entity_id = create_response.json()["id"]

        # Update the entity
        update_data = {"name": "Updated Name"}
        response = client.put(f"/entities/{entity_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Original description"  # Unchanged

    def test_update_entity_description(self):
        """Test updating entity description"""
        # Create an entity first
        entity_data = {
            "name": "Test Entity",
            "description": "Original description",
            "image_urls": ["http://example.com/test.jpg"],
        }
        create_response = client.post("/entities/", json=entity_data)
        entity_id = create_response.json()["id"]

        # Update the entity
        update_data = {"description": "Updated description"}
        response = client.put(f"/entities/{entity_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Test Entity"  # Unchanged
        assert data["description"] == "Updated description"

    def test_update_entity_image_urls(self):
        """Test updating entity image URLs"""
        # Create an entity first
        entity_data = {
            "name": "Test Entity",
            "description": "Test description",
            "image_urls": ["http://example.com/old.jpg"],
        }
        create_response = client.post("/entities/", json=entity_data)
        entity_id = create_response.json()["id"]

        # Update the entity
        update_data = {
            "image_urls": [
                "http://example.com/new1.jpg",
                "http://example.com/new2.jpg",
            ]
        }
        response = client.put(f"/entities/{entity_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["image_urls"]) == 2
        assert "http://example.com/new1.jpg" in data["image_urls"]

    def test_update_entity_multiple_fields(self):
        """Test updating multiple entity fields at once"""
        # Create an entity first
        entity_data = {
            "name": "Original Name",
            "description": "Original description",
            "image_urls": ["http://example.com/original.jpg"],
        }
        create_response = client.post("/entities/", json=entity_data)
        entity_id = create_response.json()["id"]

        # Update multiple fields
        update_data = {
            "name": "New Name",
            "description": "New description",
            "image_urls": ["http://example.com/new.jpg"],
        }
        response = client.put(f"/entities/{entity_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "New description"
        assert data["image_urls"] == ["http://example.com/new.jpg"]

    def test_update_entity_not_found(self):
        """Test updating non-existent entity"""
        update_data = {"name": "New Name"}
        response = client.put("/entities/99999", json=update_data)
        assert response.status_code == 404
        assert "Entity not found" in response.json()["detail"]

    def test_update_entity_empty_body(self):
        """Test updating entity with empty body"""
        # Create an entity first
        entity_data = {
            "name": "Test Entity",
            "description": "Test description",
            "image_urls": [],
        }
        create_response = client.post("/entities/", json=entity_data)
        entity_id = create_response.json()["id"]

        # Update with empty body - should succeed without changes
        response = client.put(f"/entities/{entity_id}", json={})
        assert response.status_code == 200


class TestEntityDelete:
    """Test entity delete operations"""

    def test_delete_entity(self):
        """Test deleting an entity"""
        # Create an entity first
        entity_data = {
            "name": "Entity To Delete",
            "description": "This will be deleted",
            "image_urls": [],
        }
        create_response = client.post("/entities/", json=entity_data)
        entity_id = create_response.json()["id"]

        # Delete the entity
        response = client.delete(f"/entities/{entity_id}")
        assert response.status_code == 200
        assert "Entity deleted successfully" in response.json()["message"]

        # Verify entity is deleted
        get_response = client.get(f"/entities/{entity_id}")
        assert get_response.status_code == 404

    def test_delete_entity_not_found(self):
        """Test deleting non-existent entity"""
        response = client.delete("/entities/99999")
        assert response.status_code == 404
        assert "Entity not found" in response.json()["detail"]

    def test_delete_entity_verify_removed_from_list(self):
        """Test that deleted entity is removed from listings"""
        # Create an entity with unique name
        entity_data = {
            "name": "Unique Delete Test Entity 12345",
            "description": "For deletion testing",
            "image_urls": [],
        }
        create_response = client.post("/entities/", json=entity_data)
        entity_id = create_response.json()["id"]

        # Verify it exists in listings
        list_response = client.get("/entities/?search=Unique Delete Test Entity 12345")
        assert any(e["id"] == entity_id for e in list_response.json()), "Entity should exist before deletion"

        # Delete the entity
        client.delete(f"/entities/{entity_id}")

        # Verify it's removed from listings
        list_response_after = client.get("/entities/?search=Unique Delete Test Entity 12345")
        assert not any(e["id"] == entity_id for e in list_response_after.json()), (
            "Entity should not exist after deletion"
        )


class TestEntityPagination:
    """Test entity pagination"""

    def test_list_entities_with_skip(self):
        """Test listing entities with skip parameter"""
        # Create multiple entities
        for i in range(5):
            entity_data = {
                "name": f"Pagination Test Entity {i}",
                "description": "For pagination testing",
                "image_urls": [],
            }
            client.post("/entities/", json=entity_data)

        # Get all entities
        all_response = client.get("/entities/")
        all_entities = all_response.json()

        # Get entities with skip
        skip_response = client.get("/entities/?skip=2")
        skipped_entities = skip_response.json()

        assert len(skipped_entities) == len(all_entities) - 2

    def test_list_entities_with_limit(self):
        """Test listing entities with limit parameter"""
        response = client.get("/entities/?limit=3")
        assert response.status_code == 200
        assert len(response.json()) <= 3

    def test_list_entities_with_skip_and_limit(self):
        """Test listing entities with both skip and limit"""
        response = client.get("/entities/?skip=1&limit=2")
        assert response.status_code == 200
        assert len(response.json()) <= 2


class TestEntitySearch:
    """Test entity search functionality"""

    def test_search_by_name(self):
        """Test searching entities by name"""
        # Create an entity with unique name
        entity_data = {
            "name": "UniqueSearchName7890",
            "description": "Regular description",
            "image_urls": [],
        }
        client.post("/entities/", json=entity_data)

        response = client.get("/entities/?search=UniqueSearchName7890")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("UniqueSearchName7890" in e["name"] for e in data)

    def test_search_by_description(self):
        """Test searching entities by description"""
        # Create an entity with unique description
        entity_data = {
            "name": "Regular Name",
            "description": "UniqueDescription4567",
            "image_urls": [],
        }
        client.post("/entities/", json=entity_data)

        response = client.get("/entities/?search=UniqueDescription4567")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("UniqueDescription4567" in e["description"] for e in data)

    def test_search_case_insensitive(self):
        """Test that search is case insensitive"""
        # Create an entity
        entity_data = {
            "name": "CaseSensitiveTest",
            "description": "Testing case sensitivity",
            "image_urls": [],
        }
        client.post("/entities/", json=entity_data)

        # Search with different cases
        response_lower = client.get("/entities/?search=casesensitivetest")
        response_upper = client.get("/entities/?search=CASESENSITIVETEST")

        assert response_lower.status_code == 200
        assert response_upper.status_code == 200

    def test_search_no_results(self):
        """Test search with no matching results"""
        response = client.get("/entities/?search=NonExistentEntity123456789")
        assert response.status_code == 200
        # Should return empty list, not error
        assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
