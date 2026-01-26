# Library Usage

Use Compere as a Python library for direct integration without running a separate server.

## Installation

```bash
uv add compere
# or
pip install compere
```

## Basic Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from compere.modules.database import Base
from compere.modules.models import EntityCreate, ComparisonCreate
from compere.modules.entity import create_entity
from compere.modules.comparison import create_comparison
from compere.modules.rating import get_ratings

# Create database engine
engine = create_engine("sqlite:///./my_comparisons.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Create a session
db = SessionLocal()
```

## Working with Entities

### Create Entities

```python
from compere.modules.models import EntityCreate
from compere.modules.entity import create_entity

# Create an entity
entity = create_entity(EntityCreate(
    name="Product A",
    description="Our flagship product",
    image_urls=["https://example.com/product-a.jpg"]
), db)

print(f"Created: {entity.name} (ID: {entity.id}, Rating: {entity.rating})")
```

### List Entities

```python
from compere.modules.entity import list_entities

# Get all entities
entities = list_entities(db=db, skip=0, limit=100)

# Search by name
results = list_entities(db=db, search="Product")
```

### Update Entity

```python
from compere.modules.models import EntityUpdate
from compere.modules.entity import update_entity

updated = update_entity(
    entity_id=1,
    entity_update=EntityUpdate(description="Updated description"),
    db=db
)
```

### Delete Entity

```python
from compere.modules.entity import delete_entity

delete_entity(entity_id=1, db=db)
```

## Recording Comparisons

### Create a Comparison

```python
from compere.modules.models import ComparisonCreate
from compere.modules.comparison import create_comparison

# User preferred entity1 over entity2
comparison = create_comparison(ComparisonCreate(
    entity1_id=1,
    entity2_id=2,
    selected_entity_id=1  # entity1 won
), db)

# Ratings are automatically updated
```

### Get Comparison History

```python
from compere.modules.comparison import list_comparisons

# All comparisons
comparisons = list_comparisons(db=db, skip=0, limit=100)

# Filter by entity
entity_comparisons = list_comparisons(db=db, entity_id=1)
```

## Ratings and Leaderboards

### Get Rankings

```python
from compere.modules.rating import get_ratings

# Get all entities sorted by rating
leaderboard = get_ratings(db=db)

for rank, entity in enumerate(leaderboard, 1):
    print(f"{rank}. {entity.name}: {entity.rating:.0f}")
```

### Manual Rating Update

```python
from compere.modules.rating import update_elo_ratings
from compere.modules.models import Entity

# Get entities
entity1 = db.query(Entity).get(1)
entity2 = db.query(Entity).get(2)

# Manually update ratings
update_elo_ratings(db, entity1, entity2, winner_id=1)
```

## Multi-Armed Bandit

### Get Next Pair (UCB Algorithm)

```python
from compere.modules.mab import get_mab_next_comparison

# Get the optimal pair for comparison
result = get_mab_next_comparison(db=db)

print(f"Compare: {result['entity1'].name} vs {result['entity2'].name}")
```

### Direct UCB Usage

```python
from compere.modules.mab import UCB

# Initialize UCB with database session
ucb = UCB(db)

# Get UCB scores for all entities
scores = ucb.get_ucb_scores()

# Select optimal pair
entity1, entity2 = ucb.select_pair(exclude_recent=True)
```

## Complete Example

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from compere.modules.database import Base
from compere.modules.models import EntityCreate, ComparisonCreate
from compere.modules.entity import create_entity
from compere.modules.comparison import create_comparison
from compere.modules.rating import get_ratings
from compere.modules.mab import get_mab_next_comparison

# Setup
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Create entities
products = [
    ("iPhone 15", "Apple's latest smartphone"),
    ("Galaxy S24", "Samsung flagship"),
    ("Pixel 8", "Google's phone"),
]

for name, desc in products:
    create_entity(EntityCreate(name=name, description=desc, image_urls=[]), db)

# Simulate comparisons
comparisons_data = [
    (1, 2, 1),  # iPhone beats Galaxy
    (2, 3, 2),  # Galaxy beats Pixel
    (1, 3, 1),  # iPhone beats Pixel
]

for e1, e2, winner in comparisons_data:
    create_comparison(ComparisonCreate(
        entity1_id=e1,
        entity2_id=e2,
        selected_entity_id=winner
    ), db)

# Show rankings
print("Final Rankings:")
for entity in get_ratings(db=db):
    print(f"  {entity.name}: {entity.rating:.0f}")

# Get next suggested comparison
next_pair = get_mab_next_comparison(db=db)
print(f"\nNext comparison: {next_pair['entity1'].name} vs {next_pair['entity2'].name}")

db.close()
```

Output:
```
Final Rankings:
  iPhone 15: 1532
  Galaxy S24: 1500
  Pixel 8: 1468

Next comparison: Galaxy S24 vs Pixel 8
```

## Integration Patterns

### Flask Integration

```python
from flask import Flask, jsonify
from compere.modules.rating import get_ratings

app = Flask(__name__)

@app.route("/leaderboard")
def leaderboard():
    db = SessionLocal()
    try:
        ratings = get_ratings(db=db)
        return jsonify([{"name": e.name, "rating": e.rating} for e in ratings])
    finally:
        db.close()
```

### Jupyter Notebook

```python
import pandas as pd
from compere.modules.rating import get_ratings

ratings = get_ratings(db=db)
df = pd.DataFrame([
    {"name": e.name, "rating": e.rating, "id": e.id}
    for e in ratings
])
df.plot(x="name", y="rating", kind="bar", title="Entity Rankings")
```

### Batch Processing

```python
import csv
from compere.modules.models import EntityCreate, ComparisonCreate
from compere.modules.entity import create_entity
from compere.modules.comparison import create_comparison

# Load entities from CSV
with open("entities.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        create_entity(EntityCreate(
            name=row["name"],
            description=row["description"],
            image_urls=[]
        ), db)

# Load comparisons from CSV
with open("comparisons.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        create_comparison(ComparisonCreate(
            entity1_id=int(row["entity1_id"]),
            entity2_id=int(row["entity2_id"]),
            selected_entity_id=int(row["winner_id"])
        ), db)
```

## Session Management

Always close sessions when done:

```python
# Option 1: Manual close
db = SessionLocal()
try:
    # ... work with db
finally:
    db.close()

# Option 2: Context manager
from contextlib import contextmanager

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

with get_db() as db:
    ratings = get_ratings(db=db)
```
