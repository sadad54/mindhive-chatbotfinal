from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import OutletQuery, OutletResponse
from app.tools.outlets_tool import OutletsTool

router = APIRouter()
outlets_tool = OutletsTool()

@router.get("/outlets", response_model=OutletResponse)
async def search_outlets(
    query: str = Query(..., description="Natural language query for outlets")
):
    """
    Search for ZUS Coffee outlets using natural language queries.
    
    This endpoint converts natural language to SQL queries and returns
    outlet information including location, hours, and services.
    
    Examples:
    - "outlets in Petaling Jaya"
    - "SS2 outlet opening hours"
    - "stores with drive-thru"
    """
    try:
        # Execute the outlet search
        result = await outlets_tool.execute(query=query)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error_message)
        
        # Return the response in the expected format
        return OutletResponse(**result.data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outlet search failed: {str(e)}")

@router.get("/outlets/all")
async def get_all_outlets():
    """Get all outlets in the database"""
    try:
        outlets = outlets_tool.get_all_outlets()
        return {
            "outlets": outlets,
            "total": len(outlets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve outlets: {str(e)}")

@router.post("/outlets/add")
async def add_outlet(outlet_data: dict):
    """Add a new outlet to the database (admin endpoint)"""
    try:
        # Validate required fields
        required_fields = ["name", "location", "address", "opening_hours"]
        for field in required_fields:
            if field not in outlet_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        outlets_tool.add_outlet(outlet_data)
        return {"message": "Outlet added successfully", "outlet_name": outlet_data["name"]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add outlet: {str(e)}")

@router.get("/outlets/schema")
async def get_database_schema():
    """Get the database schema for outlets (for debugging Text2SQL)"""
    return {
        "table": "outlets",
        "columns": [
            {"name": "id", "type": "INTEGER", "description": "Unique outlet identifier"},
            {"name": "name", "type": "TEXT", "description": "Outlet name"},
            {"name": "location", "type": "TEXT", "description": "General location (area/city)"},
            {"name": "address", "type": "TEXT", "description": "Full address"},
            {"name": "opening_hours", "type": "TEXT", "description": "Operating hours"},
            {"name": "services", "type": "TEXT", "description": "JSON array of available services"},
            {"name": "contact", "type": "TEXT", "description": "Contact information"},
            {"name": "latitude", "type": "REAL", "description": "GPS latitude"},
            {"name": "longitude", "type": "REAL", "description": "GPS longitude"}
        ]
    }
