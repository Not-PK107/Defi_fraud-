@echo off
REM Quick Start Script for DeFi Fraud Detection (Windows)
REM ========================================================

echo.
echo ================================================================
echo   🛡️  Aegis DeFi Fraud Detection - Quick Start
echo ================================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure Python 3.8+ is installed
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo.
    echo Installing dependencies...
    echo This may take a few minutes...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo ⚠️  WARNING: .env file not found!
    echo.
    echo Please create a .env file with your API keys:
    echo   1. Copy .env.example to .env
    echo   2. Edit .env and add your credentials
    echo.
    echo Press any key to create .env from template...
    pause >nul
    copy .env.example .env
    echo.
    echo ✅ .env file created. Please edit it with your API keys.
    echo.
    notepad .env
)

REM Check if model files exist
if not exist "notebooks\models\fraud_model.pkl" (
    echo.
    echo ⚠️  WARNING: ML model files not found!
    echo Please ensure model files exist in notebooks/models/
    echo.
)

echo.
echo ================================================================
echo   🚀 Starting Server...
echo ================================================================
echo.
echo   Frontend: http://localhost:5000
echo   API Docs: http://localhost:5000/api/health
echo.
echo   Press Ctrl+C to stop the server
echo ================================================================
echo.

REM Start the Flask server
python backend/server.py

pause
