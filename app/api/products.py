from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ProductQuery, ProductResponse
from app.tools.products_tool_simple import ProductsTool

router = APIRouter()
products_tool = ProductsTool()

@router.get("/products", response_model=ProductResponse)
async def search_products(
    query: str = Query(..., description="Search query for products"),
    top_k: int = Query(5, description="Number of results to return", le=20)
):
    """
    Search for products in the ZUS Coffee knowledge base using RAG.
    
    This endpoint uses a vector store to find relevant products based on
    semantic similarity to the user's query.
    """
    try:
        # Execute the product search
        result = await products_tool.execute(query=query, top_k=top_k)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error_message)
        
        # Return the response in the expected format
        return ProductResponse(**result.data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product search failed: {str(e)}")

@router.get("/products/all")
async def get_all_products():
    """Get all products in the knowledge base"""
    try:
        products = products_tool.get_all_products()
        return {
            "products": products,
            "total": len(products)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve products: {str(e)}")

@router.post("/products/add")
async def add_product(product_data: dict):
    """Add a new product to the knowledge base (admin endpoint)"""
    try:
        # Validate required fields
        required_fields = ["id", "name", "description", "category"]
        for field in required_fields:
            if field not in product_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        products_tool.add_product(product_data)
        return {"message": "Product added successfully", "product_id": product_data["id"]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add product: {str(e)}")
