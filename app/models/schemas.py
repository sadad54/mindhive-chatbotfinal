from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationState(BaseModel):
    """Tracks conversation state variables"""
    current_intent: Optional[str] = None
    missing_slots: List[str] = []
    extracted_entities: Dict[str, Any] = {}
    last_action: Optional[str] = None
    outlet_context: Optional[Dict[str, Any]] = None
    product_context: Optional[Dict[str, Any]] = None
    calculation_context: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str = Field(default="default")

class ChatResponse(BaseModel):
    message: str
    session_id: str
    action_taken: Optional[str] = None
    entities_extracted: Optional[Dict[str, Any]] = None
    needs_followup: bool = False

class ActionPlan(BaseModel):
    """Represents a planned action by the agent"""
    action_type: str  # "ask", "call_tool", "finish", "clarify"
    intent: str
    missing_slots: List[str] = []
    tool_name: Optional[str] = None
    tool_params: Optional[Dict[str, Any]] = None
    response_template: Optional[str] = None

class ToolResult(BaseModel):
    """Result from tool execution"""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    tool_name: str

# Product API Models
class ProductQuery(BaseModel):
    query: str
    top_k: int = Field(default=5, le=20)

class ProductResult(BaseModel):
    id: str
    name: str
    description: str
    price: Optional[str] = None
    image_url: Optional[str] = None
    similarity_score: float

class ProductResponse(BaseModel):
    query: str
    results: List[ProductResult]
    summary: str
    total_found: int

# Outlet API Models
class OutletQuery(BaseModel):
    query: str

class OutletResult(BaseModel):
    id: int
    name: str
    location: str
    address: str
    opening_hours: str
    services: List[str] = []
    contact: Optional[str] = None

class OutletResponse(BaseModel):
    query: str
    sql_query: str
    results: List[OutletResult]
    total_found: int

# Calculator API Models
class CalculationRequest(BaseModel):
    expression: str

class CalculationResponse(BaseModel):
    expression: str
    result: Optional[float] = None
    error: Optional[str] = None
