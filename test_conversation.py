#!/usr/bin/env python3
"""
Test script for conversation flows.
Tests the sequential conversation functionality (Part 1 of assessment).
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.chatbot.conversation_manager import ConversationManager
from app.chatbot.planner import AgenticPlanner

async def test_sequential_conversation():
    """Test the sequential conversation example from the assessment"""
    print("🧪 Testing Sequential Conversation Flow")
    print("=" * 50)
    
    # Initialize components
    conversation_manager = ConversationManager(storage_path="./test_data/sessions")
    planner = AgenticPlanner()
    
    # Test conversation flow
    session_id = "test_session"
    session = conversation_manager.get_session(session_id)
    
    conversations = [
        "Is there an outlet in Petaling Jaya?",
        "SS 2, what's the opening time?",
        "What services do they have?"
    ]
    
    for i, user_message in enumerate(conversations, 1):
        print(f"\n🔸 Turn {i}")
        print(f"User: {user_message}")
        
        # Add user message
        session.add_message("user", user_message)
        
        # Plan action
        action_plan = await planner.plan_action(user_message, session)
        print(f"Planned action: {action_plan.action_type} - {action_plan.intent}")
        
        # Execute action
        response = await planner.execute_action(action_plan, session)
        print(f"Assistant: {response.message}")
        
        # Add assistant response
        session.add_message("assistant", response.message)
        
        # Update session
        conversation_manager.update_session(session)
        
        print(f"Context: {session.get_context_summary()}")
    
    print("\n✅ Sequential conversation test completed!")

async def test_interrupted_flow():
    """Test interrupted conversation handling"""
    print("\n🧪 Testing Interrupted Conversation Flow")
    print("=" * 50)
    
    conversation_manager = ConversationManager(storage_path="./test_data/sessions")
    planner = AgenticPlanner()
    
    session_id = "interrupted_test"
    session = conversation_manager.get_session(session_id)
    
    # Start outlet conversation
    user_message = "Tell me about outlets"
    session.add_message("user", user_message)
    action_plan = await planner.plan_action(user_message, session)
    response = await planner.execute_action(action_plan, session)
    session.add_message("assistant", response.message)
    
    print(f"User: {user_message}")
    print(f"Assistant: {response.message}")
    
    # Interrupt with different topic
    user_message = "Actually, what products do you have?"
    session.add_message("user", user_message)
    action_plan = await planner.plan_action(user_message, session)
    response = await planner.execute_action(action_plan, session)
    session.add_message("assistant", response.message)
    
    print(f"User: {user_message}")
    print(f"Assistant: {response.message}")
    
    print("✅ Interrupted flow test completed!")

if __name__ == "__main__":
    asyncio.run(test_sequential_conversation())
    asyncio.run(test_interrupted_flow())
