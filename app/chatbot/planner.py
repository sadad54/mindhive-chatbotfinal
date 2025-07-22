import re
import json
from typing import Dict, List, Optional, Any
from app.models.schemas import ActionPlan, ChatResponse, ToolResult
from app.chatbot.conversation_manager import ConversationSession
from app.tools.calculator_tool import CalculatorTool
from app.tools.products_tool_simple import ProductsTool
from app.tools.outlets_tool import OutletsTool

class IntentClassifier:
    """Classifies user intents and extracts entities"""
    
    def __init__(self):
        self.intent_patterns = {
            "outlet_query": [
                r"outlet.*in\s+([^?]+)",
                r"store.*in\s+([^?]+)",
                r"location.*in\s+([^?]+)",
                r"branch.*in\s+([^?]+)",
                r"opening.*hours?",
                r"what.*time.*open",
                r"when.*open",
                r"close.*time"
            ],
            "product_query": [
                r"(drink|coffee|beverage|cup|mug|tumbler|bottle)",
                r"product.*(?:info|detail|spec)",
                r"what.*(?:sell|have|offer)",
                r"menu",
                r"drinkware"
            ],
            "calculation": [
                r"calculate|compute|math",
                r"\d+\s*[\+\-\*\/\%]\s*\d+",
                r"what.*is.*\d+.*[\+\-\*\/\%].*\d+",
                r"add|subtract|multiply|divide|plus|minus|times"
            ],
            "greeting": [
                r"^(hi|hello|hey|good\s+(?:morning|afternoon|evening))",
                r"how.*(?:are|do)"
            ],
            "general_info": [
                r"what.*(?:can|do).*you.*do",
                r"help.*me",
                r"information.*about"
            ]
        }
    
    def classify_intent(self, message: str) -> str:
        """Classify the intent of the user message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return "unknown"
    
    def extract_entities(self, message: str, intent: str) -> Dict[str, Any]:
        """Extract entities based on intent"""
        entities = {}
        message_lower = message.lower()
        
        if intent == "outlet_query":
            # Extract location
            location_match = re.search(r"(?:in|at)\s+([^?]+)", message_lower)
            if location_match:
                entities["location"] = location_match.group(1).strip()
            
            # Extract specific outlet reference
            ss2_match = re.search(r"ss\s*2", message_lower)
            if ss2_match:
                entities["specific_outlet"] = "SS2"
            
            # Extract time-related queries
            if re.search(r"opening|open|hour", message_lower):
                entities["query_type"] = "opening_hours"
        
        elif intent == "product_query":
            # Extract product types
            product_types = ["drinkware", "coffee", "drink", "beverage", "cup", "mug", "tumbler", "bottle"]
            for product_type in product_types:
                if product_type in message_lower:
                    entities["product_type"] = product_type
                    break
        
        elif intent == "calculation":
            # Extract mathematical expressions
            math_match = re.search(r"(\d+\s*[\+\-\*\/\%\^\(\)]\s*\d+.*)", message)
            if math_match:
                entities["expression"] = math_match.group(1).strip()
            else:
                # Try to extract numbers for basic operations
                numbers = re.findall(r"\d+(?:\.\d+)?", message)
                operators = re.findall(r"[\+\-\*\/\%]|plus|minus|times|divide", message_lower)
                if len(numbers) >= 2 and operators:
                    # Convert word operators to symbols
                    op_map = {"plus": "+", "minus": "-", "times": "*", "divide": "/"}
                    op = operators[0]
                    if op in op_map:
                        op = op_map[op]
                    entities["expression"] = f"{numbers[0]} {op} {numbers[1]}"
        
        return entities

class AgenticPlanner:
    """Plans and executes actions based on conversation context"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.tools = {
            "calculator": CalculatorTool(),
            "products": ProductsTool(),
            "outlets": OutletsTool()
        }
    
    async def plan_action(self, message: str, session: ConversationSession) -> ActionPlan:
        """Plan the next action based on user message and session context"""
        
        # Classify intent and extract entities
        intent = self.intent_classifier.classify_intent(message)
        entities = self.intent_classifier.extract_entities(message, intent)
        
        # Update session state
        session.update_state(
            current_intent=intent,
            extracted_entities={**session.state.extracted_entities, **entities}
        )
        
        # Plan action based on intent
        if intent == "greeting":
            return ActionPlan(
                action_type="finish",
                intent=intent,
                response_template="Hello! I'm here to help you with ZUS Coffee outlets, products, and calculations. What can I do for you today?"
            )
        
        elif intent == "general_info":
            return ActionPlan(
                action_type="finish",
                intent=intent,
                response_template="I can help you with: 1) Finding ZUS Coffee outlets and their details, 2) Information about ZUS products and drinkware, 3) Simple calculations. What would you like to know?"
            )
        
        elif intent == "outlet_query":
            return await self._plan_outlet_action(entities, session)
        
        elif intent == "product_query":
            return await self._plan_product_action(entities, session)
        
        elif intent == "calculation":
            return await self._plan_calculation_action(entities, session)
        
        else:
            return ActionPlan(
                action_type="clarify",
                intent="unknown",
                response_template="I'm not sure I understand. I can help with outlet information, product queries, or calculations. Could you please rephrase your question?"
            )
    
    async def _plan_outlet_action(self, entities: Dict, session: ConversationSession) -> ActionPlan:
        """Plan action for outlet queries"""
        missing_slots = []
        
        # Check what information we have
        location = entities.get("location") or session.state.extracted_entities.get("location")
        specific_outlet = entities.get("specific_outlet") or session.state.extracted_entities.get("specific_outlet")
        query_type = entities.get("query_type", "general")
        
        if not location and not specific_outlet:
            missing_slots.append("location")
        
        if missing_slots:
            return ActionPlan(
                action_type="ask",
                intent="outlet_query",
                missing_slots=missing_slots,
                response_template="Which location are you interested in? For example, you can ask about outlets in Petaling Jaya, Kuala Lumpur, or a specific area like SS2."
            )
        
        # We have enough information to make the query
        query = f"{location or specific_outlet}"
        if query_type == "opening_hours":
            query += " opening hours"
        
        return ActionPlan(
            action_type="call_tool",
            intent="outlet_query",
            tool_name="outlets",
            tool_params={"query": query}
        )
    
    async def _plan_product_action(self, entities: Dict, session: ConversationSession) -> ActionPlan:
        """Plan action for product queries"""
        product_type = entities.get("product_type") or session.state.extracted_entities.get("product_type")
        
        # Always proceed with the query, use "drinkware" as default if no specific type
        query = product_type or "drinkware coffee products"
        
        return ActionPlan(
            action_type="call_tool",
            intent="product_query",
            tool_name="products",
            tool_params={"query": query}
        )
    
    async def _plan_calculation_action(self, entities: Dict, session: ConversationSession) -> ActionPlan:
        """Plan action for calculation queries"""
        expression = entities.get("expression") or session.state.extracted_entities.get("expression")
        
        if not expression:
            return ActionPlan(
                action_type="ask",
                intent="calculation",
                missing_slots=["expression"],
                response_template="What calculation would you like me to perform? For example: '2 + 3' or 'calculate 15 * 4'"
            )
        
        return ActionPlan(
            action_type="call_tool",
            intent="calculation",
            tool_name="calculator",
            tool_params={"expression": expression}
        )
    
    async def execute_action(self, action_plan: ActionPlan, session: ConversationSession) -> ChatResponse:
        """Execute the planned action"""
        
        if action_plan.action_type == "finish":
            return ChatResponse(
                message=action_plan.response_template,
                session_id=session.session_id,
                action_taken="finish"
            )
        
        elif action_plan.action_type == "ask":
            return ChatResponse(
                message=action_plan.response_template,
                session_id=session.session_id,
                action_taken="ask_for_info",
                needs_followup=True
            )
        
        elif action_plan.action_type == "clarify":
            return ChatResponse(
                message=action_plan.response_template,
                session_id=session.session_id,
                action_taken="clarify"
            )
        
        elif action_plan.action_type == "call_tool":
            return await self._execute_tool_call(action_plan, session)
        
        else:
            return ChatResponse(
                message="I encountered an unexpected error. Please try again.",
                session_id=session.session_id,
                action_taken="error"
            )
    
    async def _execute_tool_call(self, action_plan: ActionPlan, session: ConversationSession) -> ChatResponse:
        """Execute a tool call"""
        tool_name = action_plan.tool_name
        tool_params = action_plan.tool_params or {}
        
        if tool_name not in self.tools:
            return ChatResponse(
                message=f"Sorry, the {tool_name} tool is not available right now.",
                session_id=session.session_id,
                action_taken="tool_error"
            )
        
        try:
            # Execute the tool
            tool = self.tools[tool_name]
            result = await tool.execute(**tool_params)
            
            # Update session context with result
            self._update_session_with_result(session, tool_name, result)
            
            # Generate response based on tool result
            if result.success:
                response_message = self._format_tool_response(tool_name, result, action_plan.intent)
                return ChatResponse(
                    message=response_message,
                    session_id=session.session_id,
                    action_taken=f"tool_call_{tool_name}",
                    entities_extracted=session.state.extracted_entities
                )
            else:
                return ChatResponse(
                    message=f"I encountered an error: {result.error_message}",
                    session_id=session.session_id,
                    action_taken="tool_error"
                )
        
        except Exception as e:
            return ChatResponse(
                message=f"Sorry, I encountered an error while processing your request: {str(e)}",
                session_id=session.session_id,
                action_taken="execution_error"
            )
    
    def _update_session_with_result(self, session: ConversationSession, tool_name: str, result: ToolResult):
        """Update session context with tool result"""
        if tool_name == "outlets":
            session.update_state(outlet_context=result.data)
        elif tool_name == "products":
            session.update_state(product_context=result.data)
        elif tool_name == "calculator":
            session.update_state(calculation_context=result.data)
        
        session.update_state(last_action=f"tool_call_{tool_name}")
    
    def _format_tool_response(self, tool_name: str, result: ToolResult, intent: str) -> str:
        """Format the response based on tool result"""
        if tool_name == "calculator":
            data = result.data
            return f"The result of {data['expression']} is {data['result']}"
        
        elif tool_name == "outlets":
            data = result.data
            if not data.get("results"):
                return "I couldn't find any outlets matching your query. Could you try a different location?"
            
            outlets = data["results"]
            if len(outlets) == 1:
                outlet = outlets[0]
                response = f"I found the {outlet['name']} outlet:\n"
                response += f"📍 {outlet['address']}\n"
                response += f"🕐 {outlet['opening_hours']}\n"
                if outlet.get("services"):
                    response += f"🛍️ Services: {', '.join(outlet['services'])}"
                return response
            else:
                response = f"I found {len(outlets)} outlets:\n\n"
                for outlet in outlets[:3]:  # Limit to first 3
                    response += f"• {outlet['name']} - {outlet['location']}\n"
                    response += f"  {outlet['opening_hours']}\n\n"
                if len(outlets) > 3:
                    response += f"... and {len(outlets) - 3} more outlets."
                return response
        
        elif tool_name == "products":
            data = result.data
            if not data.get("results"):
                return "I couldn't find any products matching your query. Try asking about drinkware, coffee, or ZUS products."
            
            response = data.get("summary", "Here are the products I found:")
            
            # Add some specific products
            products = data["results"][:3]  # Show top 3
            if products:
                response += "\n\nTop products:\n"
                for product in products:
                    response += f"• {product['name']}"
                    if product.get('price'):
                        response += f" - {product['price']}"
                    response += "\n"
            
            return response
        
        return "I've processed your request successfully."
