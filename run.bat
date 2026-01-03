@echo off
echo Starting AI Recruiter Backend...
venv\Scripts\python.exe -m uvicorn main:app --reload
pause
