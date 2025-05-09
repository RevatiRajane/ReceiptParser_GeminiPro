# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List

class ExtractedItem(BaseModel):
    name: str
    quantity: Optional[float] = 1.0 # Default to 1 if not parsed
    # unit: Optional[str] = None # Could add if you parse units
    # price: Optional[float] = None # Could add if you parse prices

class ReceiptProcessResult(BaseModel):
    store_name: Optional[str] = None
    extracted_items: List[ExtractedItem]
    raw_text: str # For debugging or display