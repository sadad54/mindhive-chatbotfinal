#!/bin/bash

echo "Starting Mindhive AI Chatbot Setup..."
echo "====================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "Python found!"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run setup script
echo "Running setup script..."
python setup_data.py

echo ""
echo "====================================="
echo "Setup completed successfully!"
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start server: uvicorn app.main:app --reload"
echo "3. Open http://localhost:8000 in your browser"
echo ""
echo "For API documentation: http://localhost:8000/docs"
echo "====================================="
