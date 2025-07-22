# Mindhive AI Chatbot Assessment

A comprehensive chatbot system demonstrating state management, agentic planning, tool integration, RAG, and robust error handling.

## Architecture Overview

### Components

1. **FastAPI Backend** - Serves chatbot API and custom endpoints
2. **Conversation Manager** - Handles state management and memory
3. **Agentic Planner** - Intent parsing and action selection
4. **Tool Integration** - Calculator, RAG, and Text2SQL tools
5. **Vector Store** - FAISS for product knowledge base
6. **SQL Database** - SQLite for outlet information
7. **Frontend** - Simple web interface for testing

### Key Features

- Multi-turn conversation with state persistence
- Intent-based action planning
- External tool integration (Calculator API)
- RAG pipeline for product queries
- Text2SQL for outlet information
- Comprehensive error handling
- Security measures against malicious inputs

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ChatBot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup databases and vector store
python scripts/setup_data.py
```

### Running the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# Access the application
# - API docs: http://localhost:8000/docs
# - Chatbot interface: http://localhost:8000
```

## API Endpoints

### Chatbot

- `POST /chat` - Main chatbot conversation endpoint

### Custom APIs

- `GET /products?query=<query>` - Product knowledge base retrieval
- `GET /outlets?query=<query>` - Outlet information via Text2SQL
- `POST /calculate` - Calculator tool

### Health

- `GET /health` - Service health check

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_conversation.py
pytest tests/test_tools.py
pytest tests/test_unhappy_flows.py
```

### Manual Testing

Use the provided test scripts:

```bash
python scripts/test_conversation.py
python scripts/test_tools.py
python scripts/test_unhappy_flows.py
```

## Key Trade-offs

1. **Vector Store Choice**: FAISS for simplicity vs. Pinecone for production scalability
2. **Database**: SQLite for development vs. PostgreSQL for production
3. **State Management**: In-memory with persistence vs. Redis for distributed systems
4. **LLM Provider**: OpenAI for reliability vs. local models for privacy
5. **Frontend**: Simple HTML/JS vs. React for better UX

## Security Measures

- SQL injection prevention through parameterized queries
- Input validation and sanitization
- Rate limiting on API endpoints
- Error message sanitization
- API key management

## Future Enhancements

- Multi-user session management
- Advanced conversation analytics
- Integration with more external APIs
- Voice interface support
- Advanced security features
