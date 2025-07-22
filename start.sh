#!/bin/bash

echo "Starting Mindhive AI Chatbot Server..."
echo "======================================"

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start the server
echo "Starting FastAPI server..."
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
