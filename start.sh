#!/bin/bash
# Startup script for Alwasaet RAG Application

set -e

echo "=================================="
echo "Alwasaet RAG - Starting Server"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env and add your GROQ_API_KEY"
    echo ""
fi

# Check for GROQ_API_KEY
source .env 2>/dev/null || true
if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key" ]; then
    echo "⚠️  GROQ_API_KEY not configured in .env"
    echo "Please get an API key from https://console.groq.com/"
    echo "and add it to your .env file"
    echo ""
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "🐍 Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo "=================================="
echo ""
echo "🚀 Starting FastAPI server on http://localhost:8000"
echo ""
echo "Available interfaces:"
echo "  • Main Chat:       http://localhost:8000/"
echo "  • Admin Dashboard: http://localhost:8000/dashboard"
echo "  • Login Page:      http://localhost:8000/login"
echo "  • API Docs:        http://localhost:8000/docs"
echo ""
echo "Default admin credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

# Start the server
python server.py
