from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    image_urls = Column(String)  # Store as JSON string
    rating = Column(Float, default=1500.0)

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    entity1_id = Column(Integer, ForeignKey("entities.id"))
    entity2_id = Column(Integer, ForeignKey("entities.id"))
    selected_entity_id = Column(Integer, ForeignKey("entities.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    entity1 = relationship("Entity", foreign_keys=[entity1_id])
    entity2 = relationship("Entity", foreign_keys=[entity2_id])
    selected_entity = relationship("Entity", foreign_keys=[selected_entity_id])
