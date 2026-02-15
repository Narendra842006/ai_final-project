@echo off
REM Quick Installation Script for Smart Medical Triage System

echo ========================================
echo Smart Medical Triage System
echo Installation Script
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

echo Installing Streamlit Frontend dependencies...
echo.
pip install -r requirements.txt
echo.

echo ========================================
echo Installation Complete! ✅
echo ========================================
echo.
echo To run the Streamlit app, use:
echo   streamlit run triage_app.py
echo.
echo To also install Backend (optional), run:
echo   pip install -r requirements_backend.txt
echo.
pause
