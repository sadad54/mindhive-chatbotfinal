@echo off
echo Starting Mindhive AI Chatbot Setup...
echo =====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found!

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run setup script
echo Running setup script...
python setup_data.py

echo.
echo =====================================
echo Setup completed successfully!
echo.
echo To start the application:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Start server: uvicorn app.main:app --reload
echo 3. Open http://localhost:8000 in your browser
echo.
echo For API documentation: http://localhost:8000/docs
echo =====================================
pause
