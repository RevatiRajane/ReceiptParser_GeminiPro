# backend/app/models.py
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    quantity = Column(Float, default=1.0) # Can be 1 for single item, or 0.5 for half kg, etc.
    unit = Column(String, nullable=True) # e.g., kg, L, pcs
    purchase_date = Column(Date, default=datetime.utcnow)
    expiry_date = Column(Date, nullable=True)
    store_name = Column(String, nullable=True)
    # user_id = Column(Integer, ForeignKey("users.id")) # If you add users
    # owner = relationship("User", back_populates="items") # If you add users

# If you add users later:
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     items = relationship("PantryItem", back_populates="owner")