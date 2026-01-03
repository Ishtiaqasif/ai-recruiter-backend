# AI Recruiter Backend

Backend API for the AI Recruiter system, built with FastAPI and LangChain.

## Prerequisites

- Python 3.10+
- MongoDB running locally or accessible via URI

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **Unix/MacOS:** `source venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Setup environment variables:
   - Create a `.env` file based on your configuration requirements.

## Running the Application

### Option 1: Using the Startup Script (Windows)
Double-click `run.bat` or execute it from the terminal:
```powershell
.\run.bat
```

### Option 2: Manual Start
Activate your virtual environment and run:
```bash
uvicorn main:app --reload
```
OR
```bash
python main.py
```

## API Documentation

Once running, access the interactive API docs at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
