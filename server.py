"""
Main FastAPI server that serves both API endpoints and static files
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Import the API app from backend
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.main import app as api_app

# Get the API routes
app = api_app

# Serve static files
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
templates_path = os.path.join(frontend_path, "templates")
static_path = os.path.join(frontend_path, "static")

# Create static directory if it doesn't exist
os.makedirs(static_path, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Serve frontend HTML pages
@app.get("/login")
async def serve_login():
    """Serve login page"""
    return FileResponse(os.path.join(templates_path, "login.html"))

@app.get("/dashboard")
async def serve_dashboard():
    """Serve admin dashboard"""
    return FileResponse(os.path.join(templates_path, "dashboard.html"))

@app.get("/chat")
async def serve_chat():
    """Serve public chat interface"""
    return FileResponse(os.path.join(templates_path, "index.html"))

# Root redirects to chat
@app.get("/")
async def redirect_root():
    """Redirect root to chat interface"""
    return FileResponse(os.path.join(templates_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
