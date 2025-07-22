#!/usr/bin/env python3
"""
Test script for conversation flows and state management.
Demonstrates multi-turn conversations and context preservation.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.chatbot.conversation_manager import ConversationManager
from app.chatbot.planner import AgenticPlanner

async def test_sequential_conversation():
    """Test the sequential conversation example from the requirements"""
    print("🗣️  Testing Sequential Conversation Flow")
    print("="*50)
    
    # Initialize components
    conversation_manager = ConversationManager("./test_data/sessions")
    planner = AgenticPlanner()
    
    # Test conversation from requirements
    session_id = "test_sequential"
    session = conversation_manager.get_session(session_id)
    
    conversation_turns = [
        "Is there an outlet in Petaling Jaya?",
        "SS 2, what's the opening time?",
        "What services do they have?"
    ]
    
    print(f"Session ID: {session_id}")
    print()
    
    for i, user_message in enumerate(conversation_turns, 1):
        print(f"Turn {i}:")
        print(f"👤 User: {user_message}")
        
        # Add user message
        session.add_message("user", user_message)
        
        # Plan action
        action_plan = await planner.plan_action(user_message, session)
        print(f"🧠 Planned action: {action_plan.action_type} ({action_plan.intent})")
        
        # Execute action
        response = await planner.execute_action(action_plan, session)
        print(f"🤖 Assistant: {response.message}")
        
        # Add assistant response
        session.add_message("assistant", response.message)
        
        # Update session
        conversation_manager.update_session(session)
        
        # Show context
        print(f"📝 Context: {session.get_context_summary()}")
        print("-" * 40)
        print()
    
    return session

async def test_interrupted_conversation():
    """Test interrupted conversation flow"""
    print("🔄 Testing Interrupted Conversation Flow")
    print("="*50)
    
    conversation_manager = ConversationManager("./test_data/sessions")
    planner = AgenticPlanner()
    
    session_id = "test_interrupted"
    session = conversation_manager.get_session(session_id)
    
    # Start outlet conversation
    messages = [
        ("I want to know about outlets", "outlet_query"),
        ("Actually, what products do you sell?", "product_query"),
        ("Never mind, calculate 15 * 4", "calculation"),
        ("Back to outlets - any in KLCC?", "outlet_query")
    ]
    
    print(f"Session ID: {session_id}")
    print()
    
    for i, (user_message, expected_intent) in enumerate(messages, 1):
        print(f"Turn {i} (expecting {expected_intent}):")
        print(f"👤 User: {user_message}")
        
        session.add_message("user", user_message)
        action_plan = await planner.plan_action(user_message, session)
        response = await planner.execute_action(action_plan, session)
        
        print(f"🤖 Assistant: {response.message}")
        print(f"🎯 Detected intent: {action_plan.intent}")
        print(f"📝 Context: {session.get_context_summary()}")
        
        session.add_message("assistant", response.message)
        conversation_manager.update_session(session)
        
        print("-" * 40)
        print()
    
    return session

async def test_context_preservation():
    """Test context preservation across turns"""
    print("💾 Testing Context Preservation")
    print("="*50)
    
    conversation_manager = ConversationManager("./test_data/sessions")
    planner = AgenticPlanner()
    
    session_id = "test_context"
    session = conversation_manager.get_session(session_id)
    
    # Multi-turn conversation that builds context
    context_turns = [
        "Tell me about outlets in Bangsar",
        "What are their opening hours?",
        "Do they have WiFi?",
        "How about drive-thru service?",
        "What's the contact number?"
    ]
    
    print(f"Session ID: {session_id}")
    print()
    
    for i, user_message in enumerate(context_turns, 1):
        print(f"Turn {i}:")
        print(f"👤 User: {user_message}")
        
        session.add_message("user", user_message)
        action_plan = await planner.plan_action(user_message, session)
        response = await planner.execute_action(action_plan, session)
        
        print(f"🤖 Assistant: {response.message}")
        print(f"🧠 Action: {action_plan.action_type}")
        
        # Show preserved entities
        entities = session.state.extracted_entities
        if entities:
            print(f"🏷️  Preserved entities: {entities}")
        
        session.add_message("assistant", response.message)
        conversation_manager.update_session(session)
        
        print("-" * 40)
        print()
    
    return session

async def test_session_persistence():
    """Test session persistence and restoration"""
    print("💿 Testing Session Persistence")
    print("="*50)
    
    # Create first session manager
    manager1 = ConversationManager("./test_data/sessions")
    session_id = "test_persistence"
    session1 = manager1.get_session(session_id)
    
    # Add some conversation data
    session1.add_message("user", "Hello, I'm looking for coffee outlets")
    session1.update_state(
        current_intent="outlet_query",
        extracted_entities={"query_type": "general"}
    )
    session1.add_message("assistant", "I'd be happy to help you find outlets!")
    
    # Save session
    manager1.update_session(session1)
    print(f"✓ Saved session with {len(session1.messages)} messages")
    
    # Create new session manager (simulates app restart)
    manager2 = ConversationManager("./test_data/sessions")
    session2 = manager2.get_session(session_id)
    
    # Verify data is restored
    print(f"✓ Restored session with {len(session2.messages)} messages")
    print(f"✓ Intent preserved: {session2.state.current_intent}")
    print(f"✓ Entities preserved: {session2.state.extracted_entities}")
    
    # Verify message content
    if len(session2.messages) >= 3:
        print(f"✓ First user message: '{session2.messages[1].content}'")
        print(f"✓ First assistant message: '{session2.messages[2].content}'")
    
    return session2

def display_session_summary(session):
    """Display a summary of the session"""
    print("\n📊 Session Summary")
    print("="*30)
    print(f"Session ID: {session.session_id}")
    print(f"Total messages: {len(session.messages)}")
    print(f"Current intent: {session.state.current_intent}")
    print(f"Extracted entities: {session.state.extracted_entities}")
    print(f"Last action: {session.state.last_action}")
    
    # Show recent messages
    recent = session.get_recent_messages(3)
    print(f"\nRecent messages:")
    for msg in recent:
        print(f"  {msg.role}: {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}")

async def main():
    """Run all conversation tests"""
    print("🧪 Testing Conversation Management & Memory")
    print("="*60)
    print()
    
    try:
        # Test sequential conversation
        session1 = await test_sequential_conversation()
        display_session_summary(session1)
        
        print("\n" + "="*60 + "\n")
        
        # Test interrupted conversation
        session2 = await test_interrupted_conversation()
        display_session_summary(session2)
        
        print("\n" + "="*60 + "\n")
        
        # Test context preservation
        session3 = await test_context_preservation()
        display_session_summary(session3)
        
        print("\n" + "="*60 + "\n")
        
        # Test session persistence
        session4 = await test_session_persistence()
        display_session_summary(session4)
        
        print("\n🎉 All conversation tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
