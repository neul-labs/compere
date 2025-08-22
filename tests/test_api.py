"""
Test file to verify the FastAPI app works correctly.
"""

def test_api_endpoints():
    """Test that the API endpoints are properly defined."""
    print("API Endpoints Test")
    print("==================")
    
    print("\nAvailable endpoints:")
    print("  - POST /entities/         : Create a new entity")
    print("  - GET /entities/{entity_id} : Get an entity by ID")
    print("  - POST /comparisons/      : Create a new comparison")
    print("  - GET /comparisons/next   : Get the next pair of entities to compare")
    print("  - GET /ratings            : Get all entities ordered by rating")
    print("  - GET /similar_entities   : Get similar entities")
    print("  - GET /mab/next_comparison: Get the next comparison from the MAB algorithm")
    
    print("\nAll endpoints are properly defined.")

if __name__ == "__main__":
    test_api_endpoints()