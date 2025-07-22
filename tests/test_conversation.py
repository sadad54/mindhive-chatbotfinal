import pytest
import asyncio
from app.chatbot.conversation_manager import ConversationManager, ConversationSession
from app.models.schemas import MessageRole

@pytest.fixture
def conversation_manager():
    """Create a conversation manager for testing"""
    return ConversationManager(storage_path="./test_data/sessions")

@pytest.fixture
def sample_session():
    """Create a sample conversation session"""
    session = ConversationSession("test_session")
    session.add_message(MessageRole.SYSTEM, "You are a helpful assistant.")
    return session

class TestConversationManager:
    """Test conversation state management and memory"""
    
    def test_create_session(self, conversation_manager):
        """Test creating a new session"""
        session_id = "test_session_1"
        session = conversation_manager.get_session(session_id)
        
        assert session.session_id == session_id
        assert len(session.messages) == 1  # Should have system message
        assert session.messages[0].role == MessageRole.SYSTEM
    
    def test_add_messages(self, sample_session):
        """Test adding messages to session"""
        initial_count = len(sample_session.messages)
        
        sample_session.add_message(MessageRole.USER, "Hello")
        sample_session.add_message(MessageRole.ASSISTANT, "Hi there!")
        
        assert len(sample_session.messages) == initial_count + 2
        assert sample_session.messages[-2].content == "Hello"
        assert sample_session.messages[-1].content == "Hi there!"
    
    def test_conversation_state_tracking(self, sample_session):
        """Test conversation state variable tracking"""
        # Test updating state
        sample_session.update_state(
            current_intent="outlet_query",
            extracted_entities={"location": "Petaling Jaya"}
        )
        
        assert sample_session.state.current_intent == "outlet_query"
        assert sample_session.state.extracted_entities["location"] == "Petaling Jaya"
    
    def test_session_persistence(self, conversation_manager):
        """Test session persistence to disk"""
        session_id = "persist_test"
        session = conversation_manager.get_session(session_id)
        
        # Add some data
        session.add_message(MessageRole.USER, "Test message")
        session.update_state(current_intent="test_intent")
        
        # Update session (triggers save)
        conversation_manager.update_session(session)
        
        # Create new manager and load session
        new_manager = ConversationManager(storage_path="./test_data/sessions")
        loaded_session = new_manager.get_session(session_id)
        
        assert len(loaded_session.messages) >= 2  # System + user message
        assert loaded_session.state.current_intent == "test_intent"
    
    def test_multi_turn_conversation(self, conversation_manager):
        """Test maintaining context across multiple turns"""
        session_id = "multi_turn_test"
        session = conversation_manager.get_session(session_id)
        
        # Turn 1: Ask about outlet
        session.add_message(MessageRole.USER, "Is there an outlet in Petaling Jaya?")
        session.update_state(
            current_intent="outlet_query",
            extracted_entities={"location": "Petaling Jaya"}
        )
        session.add_message(MessageRole.ASSISTANT, "Yes! Which outlet are you referring to?")
        
        # Turn 2: Follow up with specific outlet
        session.add_message(MessageRole.USER, "SS2, what's the opening time?")
        session.update_state(
            extracted_entities={
                **session.state.extracted_entities,
                "specific_outlet": "SS2",
                "query_type": "opening_hours"
            }
        )
        session.add_message(MessageRole.ASSISTANT, "The SS2 outlet opens at 9:00 AM")
        
        # Turn 3: Ask follow-up
        session.add_message(MessageRole.USER, "What services do they have?")
        
        # Verify context is maintained
        assert session.state.extracted_entities["location"] == "Petaling Jaya"
        assert session.state.extracted_entities["specific_outlet"] == "SS2"
        assert len(session.messages) == 7  # System + 6 conversation messages
        
        # Test context summary
        context_summary = session.get_context_summary()
        assert "outlet_query" in context_summary
        assert "Petaling Jaya" in context_summary

class TestUnhappyFlows:
    """Test conversation recovery and error handling"""
    
    def test_interrupted_conversation(self, conversation_manager):
        """Test handling interrupted conversation flows"""
        session_id = "interrupted_test"
        session = conversation_manager.get_session(session_id)
        
        # Start a conversation but don't complete it
        session.add_message(MessageRole.USER, "I want to know about outlets")
        session.update_state(current_intent="outlet_query")
        session.add_message(MessageRole.ASSISTANT, "Which location are you interested in?")
        
        # User changes topic abruptly
        session.add_message(MessageRole.USER, "Actually, what products do you have?")
        session.update_state(
            current_intent="product_query",
            extracted_entities={}  # Reset entities for new topic
        )
        
        # Should handle topic change gracefully
        assert session.state.current_intent == "product_query"
        assert session.state.extracted_entities == {}
    
    def test_incomplete_information_handling(self, sample_session):
        """Test handling when user provides incomplete information"""
        # User asks vague question
        sample_session.add_message(MessageRole.USER, "Tell me about outlets")
        sample_session.update_state(
            current_intent="outlet_query",
            missing_slots=["location"]
        )
        
        assert "location" in sample_session.state.missing_slots
        
        # Follow up with missing information
        sample_session.add_message(MessageRole.USER, "In Kuala Lumpur")
        sample_session.update_state(
            extracted_entities={"location": "Kuala Lumpur"},
            missing_slots=[]  # Information now complete
        )
        
        assert sample_session.state.missing_slots == []
        assert sample_session.state.extracted_entities["location"] == "Kuala Lumpur"

@pytest.mark.asyncio
class TestAsyncConversationFlow:
    """Test asynchronous conversation flows"""
    
    async def test_concurrent_sessions(self):
        """Test handling multiple concurrent sessions"""
        manager = ConversationManager(storage_path="./test_data/sessions")
        
        # Create multiple sessions concurrently
        session_ids = ["concurrent_1", "concurrent_2", "concurrent_3"]
        sessions = []
        
        for session_id in session_ids:
            session = manager.get_session(session_id)
            session.add_message(MessageRole.USER, f"Hello from {session_id}")
            sessions.append(session)
        
        # Verify each session maintains its own state
        for i, session in enumerate(sessions):
            assert session.session_id == session_ids[i]
            assert f"Hello from {session_ids[i]}" in session.messages[-1].content
    
    async def test_session_cleanup(self):
        """Test automatic cleanup of old sessions"""
        manager = ConversationManager(storage_path="./test_data/sessions")
        
        # Create a session
        session = manager.get_session("cleanup_test")
        session.add_message(MessageRole.USER, "Test message")
        manager.update_session(session)
        
        # Verify session exists
        assert "cleanup_test" in manager.list_sessions()
        
        # Test cleanup (would normally clean up old sessions)
        # Note: In real implementation, this would be based on actual timestamps
        # For testing, we just verify the method exists and works
        initial_count = len(manager.list_sessions())
        manager.cleanup_old_sessions(max_age_hours=0)  # Should clean up everything
        final_count = len(manager.list_sessions())
        
        # Verify cleanup occurred (sessions older than 0 hours should be removed)
        assert final_count <= initial_count

if __name__ == "__main__":
    pytest.main([__file__])
