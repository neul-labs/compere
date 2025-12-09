#!/usr/bin/env python3
"""
Complete example demonstrating all Compere features.
This example shows both library usage and API interaction.
"""

import os
import sys

import requests

# Add the compere package to the path for library usage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def library_usage_example():
    """Demonstrate library usage directly"""
    print("=" * 50)
    print("LIBRARY USAGE EXAMPLE")
    print("=" * 50)

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from compere.modules.database import Base
    from compere.modules.mab import UCB
    from compere.modules.models import (
        Comparison,
        Entity,
    )
    from compere.modules.rating import update_elo_ratings

    # Use in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("\n1. Creating sample entities...")

        # Create entities
        entities_data = [
            {
                "name": "Burger Palace",
                "description": "Best burgers in town",
                "image_urls": ["http://example.com/burger.jpg"],
            },
            {
                "name": "Pizza Corner",
                "description": "Authentic Italian pizza",
                "image_urls": ["http://example.com/pizza.jpg"],
            },
            {"name": "Sushi Zen", "description": "Fresh sushi daily", "image_urls": ["http://example.com/sushi.jpg"]},
        ]

        entities = []
        for entity_data in entities_data:
            entity = Entity(**entity_data)
            db.add(entity)
            db.commit()
            db.refresh(entity)
            entities.append(entity)
            print(f"  Created: {entity.name} (ID: {entity.id}, Rating: {entity.rating})")

        print("\n2. Initializing Multi-Armed Bandit...")
        ucb = UCB(db)
        print("  MAB initialized with persistent state")

        print("\n3. Performing comparisons...")
        comparisons_data = [
            (entities[0], entities[1], entities[0]),  # Burger wins vs Pizza
            (entities[1], entities[2], entities[2]),  # Sushi wins vs Pizza
            (entities[0], entities[2], entities[0]),  # Burger wins vs Sushi
        ]

        for entity1, entity2, winner in comparisons_data:
            # Create comparison record
            comparison = Comparison(entity1_id=entity1.id, entity2_id=entity2.id, selected_entity_id=winner.id)
            db.add(comparison)
            db.commit()

            # Update Elo ratings
            update_elo_ratings(db, entity1, entity2, winner.id)

            # Update MAB
            if winner == entity1:
                ucb.update(entity1.id, 1.0)
                ucb.update(entity2.id, 0.0)
            else:
                ucb.update(entity1.id, 0.0)
                ucb.update(entity2.id, 1.0)

            print(f"  {entity1.name} vs {entity2.name} -> Winner: {winner.name}")

        print("\n4. Final ratings:")
        db.refresh(entities[0])
        db.refresh(entities[1])
        db.refresh(entities[2])

        sorted_entities = sorted(entities, key=lambda x: x.rating, reverse=True)
        for i, entity in enumerate(sorted_entities, 1):
            print(f"  {i}. {entity.name}: {entity.rating:.2f}")

        print("\n5. MAB next suggestion:")
        next_entity_id = ucb.select_arm()
        next_entity = db.query(Entity).get(next_entity_id)
        print(f"  MAB suggests involving: {next_entity.name}")

    finally:
        db.close()


def api_usage_example():
    """Demonstrate API usage"""
    print("\n" + "=" * 50)
    print("API USAGE EXAMPLE")
    print("=" * 50)

    base_url = "http://localhost:8090"

    # Check if server is running
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code != 200:
            print("❌ Server not running. Start with: uv run compere")
            return
    except requests.ConnectionError:
        print("❌ Server not running. Start with: uv run compere")
        return

    print("✅ Server is running!")

    print("\n1. Creating entities via API...")
    entities_data = [
        {"name": "Coffee Shop A", "description": "Great espresso", "image_urls": ["http://example.com/coffee1.jpg"]},
        {"name": "Coffee Shop B", "description": "Amazing latte art", "image_urls": ["http://example.com/coffee2.jpg"]},
    ]

    created_entities = []
    for entity_data in entities_data:
        response = requests.post(f"{base_url}/entities/", json=entity_data)
        if response.status_code == 200:
            entity = response.json()
            created_entities.append(entity)
            print(f"  Created: {entity['name']} (ID: {entity['id']})")
        else:
            print(f"  Failed to create {entity_data['name']}: {response.text}")

    if len(created_entities) < 2:
        print("❌ Need at least 2 entities for comparison")
        return

    print("\n2. Listing all entities...")
    response = requests.get(f"{base_url}/entities/")
    if response.status_code == 200:
        entities = response.json()
        print(f"  Total entities: {len(entities)}")
        for entity in entities[-5:]:  # Show last 5
            print(f"    {entity['name']}: {entity['rating']:.2f}")

    print("\n3. Creating a comparison...")
    entity1, entity2 = created_entities[0], created_entities[1]
    comparison_data = {
        "entity1_id": entity1["id"],
        "entity2_id": entity2["id"],
        "selected_entity_id": entity1["id"],  # entity1 wins
    }

    response = requests.post(f"{base_url}/comparisons/", json=comparison_data)
    if response.status_code == 200:
        comparison = response.json()
        print(f"  Comparison created (ID: {comparison['id']})")
        print(f"  Winner: {entity1['name']}")

    print("\n4. Getting updated ratings...")
    response = requests.get(f"{base_url}/ratings")
    if response.status_code == 200:
        entities = response.json()
        print("  Current leaderboard:")
        for i, entity in enumerate(entities[:5], 1):
            print(f"    {i}. {entity['name']}: {entity['rating']:.2f}")

    print("\n5. MAB next comparison suggestion...")
    response = requests.get(f"{base_url}/mab/next_comparison")
    if response.status_code == 200:
        suggestion = response.json()
        print(f"  MAB suggests: {suggestion['entity1']['name']} vs {suggestion['entity2']['name']}")

    print("\n6. Getting comparison history...")
    response = requests.get(f"{base_url}/comparisons/")
    if response.status_code == 200:
        comparisons = response.json()
        print(f"  Total comparisons: {len(comparisons)}")


def configuration_example():
    """Show configuration options"""
    print("\n" + "=" * 50)
    print("CONFIGURATION EXAMPLE")
    print("=" * 50)

    config_vars = {
        "DATABASE_URL": "sqlite:///./compere.db",
        "ELO_K_FACTOR": "32.0",
        "AUTH_ENABLED": "false",
        "RATE_LIMIT_ENABLED": "false",
        "RATE_LIMIT_REQUESTS": "100",
        "RATE_LIMIT_WINDOW": "60",
        "LOG_LEVEL": "INFO",
        "ENVIRONMENT": "development",
    }

    print("Environment variables you can set:")
    for key, default in config_vars.items():
        current = os.getenv(key, default)
        print(f"  {key}={current}")

    print("\nTo use PostgreSQL:")
    print("  export DATABASE_URL=postgresql://user:password@localhost/compere")

    print("\nTo enable authentication:")
    print("  export AUTH_ENABLED=true")
    print("  export SECRET_KEY=your-secret-key-here")

    print("\nTo enable rate limiting:")
    print("  export RATE_LIMIT_ENABLED=true")
    print("  export RATE_LIMIT_REQUESTS=50")


def main():
    """Run all examples"""
    print("COMPERE - Comprehensive Usage Examples")
    print("This example demonstrates library usage, API interaction, and configuration.")
    print("\nNote: For API examples, start the server first with: uv run compere")

    # Always run library example
    library_usage_example()

    # Run API example if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        api_usage_example()

    # Show configuration
    configuration_example()

    print("\n" + "=" * 50)
    print("EXAMPLE COMPLETED")
    print("=" * 50)
    print("Next steps:")
    print("1. Install dependencies: uv sync")
    print("2. Start server: uv run compere")
    print("3. Visit http://localhost:8090/docs for API documentation")
    print("4. Run tests: uv run pytest")


if __name__ == "__main__":
    main()
