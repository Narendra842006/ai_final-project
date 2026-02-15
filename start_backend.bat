@echo off
REM Quick Start Script for FastAPI Backend

echo ========================================
echo Smart Medical Triage System Backend
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements_backend.txt
echo.

REM Start the server
echo ========================================
echo Starting FastAPI Server...
echo API Docs: http://localhost:8000/api/docs
echo Health Check: http://localhost:8000/health
echo ========================================
echo.

uvicorn backend.main:app --reload --port 8000

pause
