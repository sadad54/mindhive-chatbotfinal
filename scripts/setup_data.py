#!/usr/bin/env python3
"""
Setup script for initializing the chatbot data and databases.
This script creates the necessary directories, databases, and vector stores.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.tools.outlets_tool import OutletDatabase
from app.tools.products_tool import ProductsTool

def create_directories():
    """Create necessary directories"""
    directories = [
        "./data",
        "./data/sessions",
        "./data/vector_store",
        "./test_data",
        "./test_data/sessions",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_outlets_database():
    """Setup and populate outlets database"""
    print("\n📍 Setting up outlets database...")
    
    try:
        db = OutletDatabase("./data/outlets.db")
        print("✓ Outlets database created and populated with sample data")
        
        # Verify data
        with sqlite3.connect("./data/outlets.db") as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM outlets")
            count = cursor.fetchone()[0]
            print(f"✓ Database contains {count} outlet records")
            
    except Exception as e:
        print(f"✗ Error setting up outlets database: {e}")
        return False
    
    return True

def setup_products_vector_store():
    """Setup products vector store"""
    print("\n☕ Setting up products vector store...")
    
    try:
        products_tool = ProductsTool("./data/vector_store")
        print("✓ Products vector store created and initialized")
        
        # Verify vector store
        all_products = products_tool.get_all_products()
        print(f"✓ Vector store contains {len(all_products)} product records")
        
    except Exception as e:
        print(f"✗ Error setting up products vector store: {e}")
        print("Note: This might be due to missing dependencies (faiss-cpu, sentence-transformers)")
        print("Vector store will be created when the application starts.")
        return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\n🔧 Setting up environment configuration...")
    
    env_file = ".env"
    env_example_file = ".env.example"
    
    if not os.path.exists(env_file) and os.path.exists(env_example_file):
        try:
            with open(env_example_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print(f"✓ Created {env_file} from {env_example_file}")
            print("⚠️  Please update the .env file with your actual API keys")
            
        except Exception as e:
            print(f"✗ Error creating .env file: {e}")
            return False
    else:
        print(f"✓ Environment file already exists or example not found")
    
    return True

def test_database_connections():
    """Test database connections"""
    print("\n🧪 Testing database connections...")
    
    # Test outlets database
    try:
        with sqlite3.connect("./data/outlets.db") as conn:
            cursor = conn.execute("SELECT name FROM outlets LIMIT 1")
            result = cursor.fetchone()
            if result:
                print(f"✓ Outlets database test passed: Found outlet '{result[0]}'")
            else:
                print("⚠️  Outlets database is empty")
    except Exception as e:
        print(f"✗ Outlets database test failed: {e}")
    
    # Test products vector store directory
    if os.path.exists("./data/vector_store"):
        files = os.listdir("./data/vector_store")
        if files:
            print(f"✓ Products vector store test passed: Found {len(files)} files")
        else:
            print("⚠️  Products vector store directory is empty")
    else:
        print("⚠️  Products vector store directory not found")

def display_summary():
    """Display setup summary"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Update .env file with your OpenAI API key")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start the application: uvicorn app.main:app --reload")
    print("4. Access the chatbot at: http://localhost:8000")
    print("5. View API docs at: http://localhost:8000/docs")
    print()
    print("Test endpoints:")
    print("• Chat: POST /chat")
    print("• Products: GET /api/products?query=drinkware")
    print("• Outlets: GET /api/outlets?query=SS2")
    print("• Calculator: POST /api/calculate")
    print()
    print("Run tests with: pytest")
    print("="*60)

def main():
    """Main setup function"""
    print("🚀 Setting up Mindhive AI Chatbot...")
    print("="*60)
    
    # Create directories
    create_directories()
    
    # Setup databases and vector stores
    setup_outlets_database()
    setup_products_vector_store()
    
    # Create environment file
    create_env_file()
    
    # Test connections
    test_database_connections()
    
    # Display summary
    display_summary()

if __name__ == "__main__":
    main()
