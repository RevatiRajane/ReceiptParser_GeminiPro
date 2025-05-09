# backend/app/receipt_processor.py
import pytesseract
from PIL import Image
import io
import re
from typing import List, Optional
from .schemas import ExtractedItem, ReceiptProcessResult # Import from local schemas

# --- TESSERACT CONFIGURATION ---
# import os
# from dotenv import load_dotenv
# load_dotenv()
# TESSERACT_PATH = os.getenv("TESSERACT_CMD")
# if TESSERACT_PATH:
#     pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
# else:
#     # Attempt to find Tesseract in common locations or rely on PATH
#     # You might need to adjust this based on your Tesseract installation
#     # For Windows: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#     # For Linux/macOS (if not in PATH): '/usr/local/bin/tesseract' or '/opt/homebrew/bin/tesseract'
#     pass


POTENTIAL_GROCERY_KEYWORDS = [
    "milk", "bread", "eggs", "cheese", "yogurt", "butter", "fruit", "vegetable",
    "apple", "banana", "orange", "potato", "tomato", "onion", "chicken", "beef",
    "pork", "fish", "rice", "pasta", "cereal", "flour", "sugar", "salt", "oil",
    "coffee", "tea", "juice", "soda", "water", "snack", "chips", "cookie", "frozen",
    "organic", "whole", "grain", "lean", "low fat", "gluten free", "canned",
    "beans", "lettuce", "spinach", "broccoli", "carrot", "berry", "berries","paneer"
]

NON_GROCERY_INDICATORS = [
    "CLOTHING", "APPAREL", "SHOES", "ELECTRONICS", "TOYS", "BOOKS", "GIFT CARD",
    "PHARMACY", "PRESCRIPTION", "OTC MED", "TAX", "BAG FEE", "TOTAL", "SUBTOTAL",
    "CASH", "CREDIT", "DEBIT", "CHANGE", "SAVINGS", "LOYALTY", "MEMBER", "BALANCE",
    "TRANSACTION", "AUTH CODE", "PIN VERIFIED", "REFUND", "CUSTOMER COPY", "STORE COPY"
]


def ocr_image(image_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Basic preprocessing (optional, experiment for better results)
        # image = image.convert('L') # Convert to grayscale
        # image = image.point(lambda x: 0 if x < 150 else 255) # Binarization example
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return ""

def identify_store(text: str) -> Optional[str]:
    text_lower = text.lower()
    if "walmart" in text_lower:
        return "Walmart"
    if "aldi" in text_lower:
        return "ALDI"
    if "costco" in text_lower:
        return "Costco"
    if "target" in text_lower:
        return "Target"
    if "kroger" in text_lower:
        return "Kroger"
    # Add more store identification logic
    return None

def is_potential_item_line(line: str) -> bool:
    """
    More refined filter to check if a line might represent an item.
    """
    line_lower = line.lower()
    stripped_line = line.strip()

    if not stripped_line or len(stripped_line) < 3:
        return False

    # Exclude lines with strong non-grocery indicators
    if any(indicator.lower() in line_lower for indicator in NON_GROCERY_INDICATORS):
        return False

    # Exclude lines that are mostly numbers or symbols (likely totals, card numbers, dates/times)
    if sum(c.isdigit() for c in stripped_line) > len(stripped_line) * 0.7: # More than 70% digits
        return False
    if not any(char.isalpha() for char in stripped_line): # No letters at all
        return False

    # Exclude common header/footer lines
    if "www." in line_lower or ".com" in line_lower or "@" in line_lower and " " not in line_lower: # email/website
        return False
    if "phone" in line_lower or "tel" in line_lower or re.match(r".*\d{3}[-.]\d{3}[-.]\d{4}.*", line_lower): # phone number
        return False
    if re.match(r"^\s*(\d{1,2}/\d{1,2}/\d{2,4})\s*$", stripped_line): # Date
        return False
    if re.match(r"^\s*(\d{1,2}:\d{2}(:\d{2})?\s*(am|pm)?)\s*$", stripped_line): # Time
        return False

    # A common pattern for items is text followed by a price (e.g., "ITEM NAME 12.34")
    if re.search(r"[a-zA-Z]", stripped_line) and re.search(r"\d+\.\d{2}\b", stripped_line):
        return True

    # Lines that might be items without an obvious price on the same line (e.g. multiline items or items where qty/price is on next line)
    # This is harder. For now, let's be a bit more inclusive if it has significant text content.
    if len(stripped_line.split()) >= 2 and sum(c.isalpha() for c in stripped_line) > len(stripped_line) * 0.5 :
         # Check if it contains any grocery keywords as a weaker signal
        if any(keyword in line_lower for keyword in POTENTIAL_GROCERY_KEYWORDS):
            return True

    return False


def parse_receipt_text(text: str, store: Optional[str]) -> List[ExtractedItem]:
    items: List[ExtractedItem] = []
    lines = text.split('\n')
    
    # print("\n--- Potential Item Lines ---")
    for line in lines:
        stripped_line = line.strip()
        if not is_potential_item_line(stripped_line):
            continue
        
        # print(f"Considering line: '{stripped_line}'")

        # Attempt to remove price and trailing codes (e.g., " 12.34 F", " 3.99 N X")
        # This regex tries to find a price at the end of the line, possibly followed by tax codes or other single letters.
        # It's greedy, so it will take the last price-like number.
        name_candidate = re.sub(r'\s+\d+\.\d{2}(\s+[A-Z]){0,2}\s*$', '', stripped_line).strip()
        name_candidate = re.sub(r'\s+@\s+\d+\.\d+', '', name_candidate).strip() # Remove " @ 1.23" (common for quantity pricing)

        # Simplistic quantity extraction (e.g., "2 APPLES", "1.5 LB BANANAS")
        quantity = 1.0
        item_name_final = name_candidate

        qty_match_leading_number = re.match(r"(\d+(\.\d+)?)\s*(?:ct|lb|kg|oz|ea|x)?\s+(.+)", name_candidate, re.IGNORECASE)
        if qty_match_leading_number:
            try:
                quantity = float(qty_match_leading_number.group(1))
                item_name_final = qty_match_leading_number.group(3).strip()
            except ValueError:
                pass # Stick with default quantity and full name_candidate

        # Further cleanup of item name
        item_name_final = re.sub(r'\b\d{4,}\b', '', item_name_final).strip() # Remove long numbers (likely UPCs, codes)
        item_name_final = re.sub(r'^\d+\s*X\s+', '', item_name_final, flags=re.IGNORECASE).strip() # Remove "2 X " at start
        item_name_final = ' '.join(item_name_final.split()) # Normalize whitespace

        # Final check: must have some alphabetical characters and be of reasonable length
        if len(item_name_final) > 2 and any(c.isalpha() for c in item_name_final):
            # Check if it's likely a grocery item based on keywords.
            # This is a simple filter; a more sophisticated approach is needed for high accuracy.
            is_grocery = any(gk.lower() in item_name_final.lower() for gk in POTENTIAL_GROCERY_KEYWORDS)
            
            # For this simplified version, we add if it passed `is_potential_item_line`
            # AND has a somewhat plausible name after cleaning.
            # A stronger grocery filter can be applied here if `is_grocery` is reliable.
            if is_grocery: # Only add if a grocery keyword is found
                items.append(ExtractedItem(name=item_name_final.title(), quantity=quantity))
            # else:
            # print(f"  Rejected (not grocery keyword): {item_name_final.title()}")


    # Basic duplicate merging (by name, summing quantity)
    merged_items_dict: dict[str, ExtractedItem] = {}
    for item in items:
        if item.name in merged_items_dict:
            merged_items_dict[item.name].quantity = (merged_items_dict[item.name].quantity or 0) + (item.quantity or 0)
        else:
            merged_items_dict[item.name] = item
    
    return list(merged_items_dict.values())


async def process_receipt_image(image_bytes: bytes) -> ReceiptProcessResult:
    raw_text = ocr_image(image_bytes)
    store_name = identify_store(raw_text)
    
    # print("---- RAW OCR TEXT ----")
    # print(raw_text)
    # print("---- END RAW OCR TEXT ----")

    extracted_items = parse_receipt_text(raw_text, store_name)

    # print("---- PARSED ITEMS ----")
    # for item in extracted_items:
    #     print(f"- Name: {item.name}, Qty: {item.quantity}")
    # print("---- END PARSED ITEMS ----")
    
    return ReceiptProcessResult(
        store_name=store_name,
        extracted_items=extracted_items,
        raw_text=raw_text
    )