# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def create_pantry_item(db: Session, item: schemas.PantryItemCreate):
    db_item = models.PantryItem(
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        purchase_date=item.purchase_date if item.purchase_date else datetime.utcnow().date(),
        expiry_date=item.expiry_date,
        store_name=item.store_name
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_pantry_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PantryItem).offset(skip).limit(limit).all()

def get_pantry_item(db: Session, item_id: int):
    return db.query(models.PantryItem).filter(models.PantryItem.id == item_id).first()

def delete_pantry_item(db: Session, item_id: int):
    db_item = db.query(models.PantryItem).filter(models.PantryItem.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False