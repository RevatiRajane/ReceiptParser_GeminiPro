# Receipt Scanner

## Application Overview

1. **Frontend (React)**: Uploading a receipt image.
2. **Backend (Python/FastAPI)**: Receiving the image, performing OCR, parsing for grocery items.
3. **Frontend (React)**: Displaying the extracted grocery items.

## Project Structure

### I. Backend

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app definition and routes
│   ├── schemas.py          # Pydantic schemas for request/response
│   └── receipt_processor.py # OCR and parsing logic
├── venv/                   # Virtual environment
├── requirements.txt
└── .env                    # Optional: for TESSERACT_CMD if needed
```

### II. Frontend (React)
Display Only (code is in frontend repo)

1. Project Setup (Frontend - if not already done):
```bash
npx create-vite frontend --template react # Or create-react-app
cd frontend
npm install axios
```

## Running the Application

### 1. Install Tesseract OCR (Crucial for the backend)

- **macOS**: 
  ```bash
  brew install tesseract tesseract-lang
  ```
  
- **Windows**: 
  Download installer from Tesseract at UB Mannheim. Ensure Tesseract is in your PATH or set `pytesseract.pytesseract.tesseract_cmd` in `receipt_processor.py`.
  
- **Linux (Ubuntu/Debian)**: 
  ```bash
  sudo apt-get update && sudo apt-get install tesseract-ocr libtesseract-dev tesseract-ocr-eng
  ```

### 2. Backend

- Navigate to the backend directory.
- Create and activate a virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/macOS
  # venv\Scripts\activate    # Windows
  ```
- Install dependencies: 
  ```bash
  pip install -r requirements.txt
  ```
- Run the FastAPI server: 
  ```bash
  uvicorn app.main:app --reload
  ```
  (It will typically run on http://localhost:8000)

### 3. Frontend

- Navigate to the frontend directory.
- Install dependencies: 
  ```bash
  npm install
  ```
- Run the React development server: 
  ```bash
  npm run dev  # for Vite
  # or
  npm start    # for Create React App
  ```
  (It will typically run on http://localhost:5173 or http://localhost:3000)
