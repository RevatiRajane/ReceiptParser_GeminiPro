# backend/app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import schemas, receipt_processor # No database related modules

app = FastAPI(title="Grocery Receipt Processor API")

# CORS Configuration
origins = [
    "http://localhost:3000",  # Default for Create React App
    "http://localhost:3001",
    "http://localhost:5173",  # Default for Vite
    # Add your frontend's actual origin if different
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

@app.post("/upload-receipt/", response_model=schemas.ReceiptProcessResult)
async def upload_and_process_receipt(file: UploadFile = File(...)):
    """
    Accepts an image file, performs OCR, and attempts to extract grocery items.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        # You could also try to support PDF here by converting PDF to image first
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    contents = await file.read()
    try:
        result = await receipt_processor.process_receipt_image(contents)
        return result
    except Exception as e:
        print(f"Unhandled error in process_receipt_image: {e}") # Log for server debugging
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the receipt: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Welcome to the Grocery Receipt Processor. Use the /upload-receipt/ endpoint to process receipts."}

# To run: uvicorn app.main:app --reload (from backend/ directory)