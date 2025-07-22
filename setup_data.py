#!/usr/bin/env python3
"""
Setup script for the Mindhive AI Chatbot project.
This script initializes the database, vector store, and sample data.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def setup_database():
    """Setup the outlets database with sample data"""
    print("Setting up outlets database...")
    
    from app.tools.outlets_tool import OutletsTool
    
    # Initialize the outlets tool (this will create the database)
    outlets_tool = OutletsTool()
    
    print("✅ Outlets database setup complete!")
    return outlets_tool

async def setup_vector_store():
    """Setup the products vector store"""
    print("Setting up products vector store...")
    
    from app.tools.products_tool import ProductsTool
    
    # Initialize the products tool (this will create the vector store)
    products_tool = ProductsTool()
    
    print("✅ Products vector store setup complete!")
    return products_tool

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/sessions",
        "data/vector_store",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("Creating .env file...")
        env_content = """# OpenAI API Key (optional - for advanced features)
OPENAI_API_KEY=your_openai_api_key_here

# Calculator API (fallback available)
CALCULATOR_API_URL=http://api.mathjs.org/v4

# Database configuration
DATABASE_URL=sqlite:///./data/chatbot.db

# Vector store path
VECTOR_STORE_PATH=./data/vector_store

# Application settings
LOG_LEVEL=INFO
SESSION_STORAGE_PATH=./data/sessions
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

async def main():
    """Main setup function"""
    print("🚀 Setting up Mindhive AI Chatbot...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Setup database and vector store
    await setup_database()
    await setup_vector_store()
    
    print("=" * 50)
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the server: uvicorn app.main:app --reload")
    print("3. Open http://localhost:8000 in your browser")
    print("\nAPI Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())
