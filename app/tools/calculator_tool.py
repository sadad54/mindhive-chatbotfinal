import httpx
import re
import ast
import operator
from typing import Dict, Any
from app.models.schemas import ToolResult

class CalculatorTool:
    """Tool for performing mathematical calculations"""
    
    def __init__(self, api_url: str = "http://api.mathjs.org/v4"):
        self.api_url = api_url
        self.safe_operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '%': operator.mod,
            '**': operator.pow,
            '^': operator.pow
        }
    
    async def execute(self, expression: str) -> ToolResult:
        """Execute a calculation"""
        try:
            # First try to use external API
            result = await self._try_external_api(expression)
            if result is not None:
                return ToolResult(
                    success=True,
                    data={
                        "expression": expression,
                        "result": result,
                        "method": "external_api"
                    },
                    tool_name="calculator"
                )
            
            # Fallback to local safe evaluation
            result = self._safe_eval(expression)
            return ToolResult(
                success=True,
                data={
                    "expression": expression,
                    "result": result,
                    "method": "local_eval"
                },
                tool_name="calculator"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Calculation error: {str(e)}",
                tool_name="calculator"
            )
    
    async def _try_external_api(self, expression: str) -> float:
        """Try to use external math API"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Clean expression for API
                clean_expr = self._clean_expression(expression)
                
                response = await client.post(
                    self.api_url,
                    data={"expr": clean_expr},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    result = response.text.strip()
                    # Try to parse the result as a number
                    try:
                        return float(result)
                    except ValueError:
                        # If it's not a simple number, try to evaluate it safely
                        return self._safe_eval(result)
                
        except (httpx.RequestError, httpx.TimeoutException):
            # API is down or timeout, will use fallback
            pass
        
        return None
    
    def _clean_expression(self, expression: str) -> str:
        """Clean and validate expression"""
        # Remove whitespace
        expr = expression.strip()
        
        # Replace common text operators
        replacements = {
            'x': '*',
            'X': '*',
            '×': '*',
            '÷': '/',
            '^': '**'
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
        
        # Validate that expression only contains safe characters
        allowed_chars = set('0123456789+-*/%.() ')
        if not all(c in allowed_chars for c in expr):
            raise ValueError("Expression contains invalid characters")
        
        return expr
    
    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate a mathematical expression"""
        # Clean the expression
        expr = self._clean_expression(expression)
        
        # Use AST to parse and evaluate safely
        try:
            node = ast.parse(expr, mode='eval')
            result = self._eval_node(node.body)
            return float(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def _eval_node(self, node):
        """Recursively evaluate AST nodes"""
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ValueError("Division by zero")
                return left / right
            elif isinstance(node.op, ast.Mod):
                return left % right
            elif isinstance(node.op, ast.Pow):
                return left ** right
            else:
                raise ValueError(f"Unsupported operation: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            else:
                raise ValueError(f"Unsupported unary operation: {type(node.op)}")
        else:
            raise ValueError(f"Unsupported node type: {type(node)}")
    
    def validate_expression(self, expression: str) -> bool:
        """Validate if expression is safe to evaluate"""
        try:
            self._clean_expression(expression)
            return True
        except ValueError:
            return False
