from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from app.chatbot.conversation_manager import ConversationManager
from app.chatbot.planner import AgenticPlanner
from app.api.products import router as products_router
from app.api.outlets import router as outlets_router
from app.api.calculator import router as calculator_router
from app.models.schemas import ChatRequest, ChatResponse

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Mindhive AI Chatbot",
    description="Assessment project demonstrating multi-turn conversations, agentic planning, tool integration, and RAG",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(products_router, prefix="/api", tags=["products"])
app.include_router(outlets_router, prefix="/api", tags=["outlets"])
app.include_router(calculator_router, prefix="/api", tags=["calculator"])

# Initialize chatbot components
conversation_manager = ConversationManager()
planner = AgenticPlanner()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the chatbot interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """Main chatbot conversation endpoint"""
    try:
        # Get or create conversation session
        session = conversation_manager.get_session(chat_request.session_id)
        
        # Add user message to conversation history
        session.add_message("user", chat_request.message)
        
        # Use planner to determine next action
        action_plan = await planner.plan_action(
            message=chat_request.message,
            session=session
        )
        
        # Execute the planned action
        response = await planner.execute_action(action_plan, session)
        
        # Add assistant response to conversation history
        session.add_message("assistant", response.message)
        
        # Update session state
        conversation_manager.update_session(session)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mindhive-chatbot"}

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get conversation session data"""
    session = conversation_manager.get_session(session_id)
    return {
        "session_id": session.session_id,
        "messages": session.messages,
        "state": session.state
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
