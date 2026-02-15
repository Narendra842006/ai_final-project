@echo off
REM Quick Run Script - Starts Streamlit App

echo ========================================
echo Starting Smart Medical Triage System
echo ========================================
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ERROR: Streamlit not installed!
    echo Please run: install.bat first
    echo.
    pause
    exit /b 1
)

echo Starting Streamlit app...
echo.
echo App will open automatically in your browser.
echo If not, visit: http://localhost:8502
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run triage_app.py

pause
