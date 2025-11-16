#!/bin/bash

# Start the FastAPI backend
echo "Starting FastAPI backend..."
cd /home/runner/work/alwasaet-rag/alwasaet-rag
python backend.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start the Next.js frontend
echo "Starting Next.js frontend..."
cd /home/runner/work/alwasaet-rag/alwasaet-rag/frontend
npm run dev &
FRONTEND_PID=$!

echo "====================================="
echo "Alwasaet RAG Application is running!"
echo "====================================="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "====================================="
echo "Press Ctrl+C to stop all services"
echo "====================================="

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Wait for both processes
wait
