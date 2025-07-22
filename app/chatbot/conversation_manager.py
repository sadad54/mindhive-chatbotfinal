from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from app.models.schemas import Message, ConversationState, MessageRole

class ConversationSession:
    """Manages a single conversation session with state persistence"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[Message] = []
        self.state = ConversationState()
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_message(self, role: MessageRole, content: str):
        """Add a message to the conversation history"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_recent_messages(self, limit: int = 5) -> List[Message]:
        """Get the most recent messages"""
        return self.messages[-limit:] if len(self.messages) > limit else self.messages
    
    def update_state(self, **kwargs):
        """Update conversation state"""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
    
    def get_context_summary(self) -> str:
        """Generate a summary of current conversation context"""
        recent_messages = self.get_recent_messages(3)
        context_parts = []
        
        if self.state.current_intent:
            context_parts.append(f"Current intent: {self.state.current_intent}")
        
        if self.state.outlet_context:
            context_parts.append(f"Outlet context: {self.state.outlet_context}")
        
        if self.state.product_context:
            context_parts.append(f"Product context: {self.state.product_context}")
        
        if self.state.extracted_entities:
            context_parts.append(f"Entities: {self.state.extracted_entities}")
        
        context_summary = " | ".join(context_parts) if context_parts else "No specific context"
        
        # Add recent conversation
        if recent_messages:
            conversation_summary = " -> ".join([
                f"{msg.role}: {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}"
                for msg in recent_messages
            ])
            return f"{context_summary} | Recent: {conversation_summary}"
        
        return context_summary
    
    def to_dict(self) -> dict:
        """Convert session to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in self.messages
            ],
            "state": self.state.dict(),
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationSession':
        """Create session from dictionary"""
        session = cls(data["session_id"])
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.last_activity = datetime.fromisoformat(data["last_activity"])
        
        # Restore messages
        for msg_data in data["messages"]:
            message = Message(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"])
            )
            session.messages.append(message)
        
        # Restore state
        session.state = ConversationState(**data["state"])
        
        return session

class ConversationManager:
    """Manages multiple conversation sessions with persistence"""
    
    def __init__(self, storage_path: str = "./data/sessions"):
        self.storage_path = storage_path
        self.sessions: Dict[str, ConversationSession] = {}
        self._ensure_storage_dir()
        self._load_sessions()
    
    def _ensure_storage_dir(self):
        """Ensure storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _get_session_file(self, session_id: str) -> str:
        """Get file path for session"""
        return os.path.join(self.storage_path, f"{session_id}.json")
    
    def _load_sessions(self):
        """Load existing sessions from disk"""
        if not os.path.exists(self.storage_path):
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                session_id = filename[:-5]  # Remove .json
                try:
                    with open(os.path.join(self.storage_path, filename), 'r') as f:
                        data = json.load(f)
                        session = ConversationSession.from_dict(data)
                        self.sessions[session_id] = session
                except Exception as e:
                    print(f"Error loading session {session_id}: {e}")
    
    def get_session(self, session_id: str) -> ConversationSession:
        """Get or create a conversation session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationSession(session_id)
            # Add initial system message
            self.sessions[session_id].add_message(
                MessageRole.SYSTEM,
                "You are a helpful assistant for ZUS Coffee. You can help with outlet information, product queries, and calculations."
            )
        
        return self.sessions[session_id]
    
    def update_session(self, session: ConversationSession):
        """Update and persist a session"""
        self.sessions[session.session_id] = session
        self._save_session(session)
    
    def _save_session(self, session: ConversationSession):
        """Save session to disk"""
        try:
            session_file = self._get_session_file(session.session_id)
            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving session {session.session_id}: {e}")
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        session_file = self._get_session_file(session_id)
        if os.path.exists(session_file):
            os.remove(session_file)
    
    def list_sessions(self) -> List[str]:
        """List all session IDs"""
        return list(self.sessions.keys())
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up sessions older than specified hours"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        sessions_to_delete = []
        for session_id, session in self.sessions.items():
            if session.last_activity.timestamp() < cutoff_time:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            self.delete_session(session_id)
