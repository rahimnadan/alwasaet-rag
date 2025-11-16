@echo off
REM Startup script for Alwasaet RAG Application (Windows)

echo ==================================
echo Alwasaet RAG - Starting Server
echo ==================================

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Please edit .env and add your GROQ_API_KEY
    echo.
)

REM Check Python version
python --version
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt

echo.
echo ==================================
echo Setup complete!
echo ==================================
echo.
echo Starting FastAPI server on http://localhost:8000
echo.
echo Available interfaces:
echo   - Main Chat:       http://localhost:8000/
echo   - Admin Dashboard: http://localhost:8000/dashboard
echo   - Login Page:      http://localhost:8000/login
echo   - API Docs:        http://localhost:8000/docs
echo.
echo Default admin credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo ==================================
echo.

REM Start the server
python server.py
