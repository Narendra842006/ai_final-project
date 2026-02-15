@echo off
REM Complete Installation Script (Frontend + Backend)

echo ========================================
echo Smart Medical Triage System
echo COMPLETE Installation (Frontend + Backend)
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8 or higher from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo Step 1/2: Installing Frontend (Streamlit) dependencies...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Frontend installation failed!
    pause
    exit /b 1
)
echo.

echo Step 2/2: Installing Backend (FastAPI) dependencies...
echo.
pip install -r requirements_backend.txt
if errorlevel 1 (
    echo ERROR: Backend installation failed!
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✅ Installation Complete!
echo ========================================
echo.
echo Next Steps:
echo.
echo 1. Start Backend (Terminal 1):
echo    start_backend.bat
echo.
echo 2. Start Frontend (Terminal 2):
echo    streamlit run triage_app.py
echo.
echo 3. Open browser:
echo    Frontend: http://localhost:8502
echo    Backend API: http://localhost:8000/api/docs
echo.
pause
