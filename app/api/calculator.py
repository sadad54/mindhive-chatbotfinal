from fastapi import APIRouter, HTTPException
from app.models.schemas import CalculationRequest, CalculationResponse
from app.tools.calculator_tool import CalculatorTool

router = APIRouter()
calculator_tool = CalculatorTool()

@router.post("/calculate", response_model=CalculationResponse)
async def calculate(request: CalculationRequest):
    """
    Perform mathematical calculations.
    
    This endpoint can handle basic arithmetic operations like:
    - Addition: 2 + 3
    - Subtraction: 10 - 4
    - Multiplication: 5 * 6
    - Division: 20 / 4
    - Modulo: 17 % 5
    - Power: 2 ** 3
    """
    try:
        # Execute the calculation
        result = await calculator_tool.execute(expression=request.expression)
        
        if result.success:
            data = result.data
            return CalculationResponse(
                expression=data["expression"],
                result=data["result"]
            )
        else:
            return CalculationResponse(
                expression=request.expression,
                error=result.error_message
            )
        
    except Exception as e:
        return CalculationResponse(
            expression=request.expression,
            error=f"Calculation failed: {str(e)}"
        )

@router.get("/calculate")
async def calculate_get(expression: str):
    """
    GET endpoint for calculations (for simple testing).
    
    Example: /calculate?expression=2+3
    """
    try:
        # Validate expression
        if not calculator_tool.validate_expression(expression):
            raise HTTPException(status_code=400, detail="Invalid mathematical expression")
        
        # Execute the calculation
        result = await calculator_tool.execute(expression=expression)
        
        if result.success:
            return result.data
        else:
            raise HTTPException(status_code=400, detail=result.error_message)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")

@router.get("/calculate/validate")
async def validate_expression(expression: str):
    """
    Validate if an expression is safe to calculate.
    """
    try:
        is_valid = calculator_tool.validate_expression(expression)
        return {
            "expression": expression,
            "is_valid": is_valid,
            "message": "Expression is valid" if is_valid else "Expression contains invalid characters or structure"
        }
    except Exception as e:
        return {
            "expression": expression,
            "is_valid": False,
            "message": f"Validation error: {str(e)}"
        }
