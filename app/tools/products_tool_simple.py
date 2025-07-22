import os
import json
from typing import List, Dict, Any
from app.models.schemas import ToolResult, ProductResult

class SimpleProductKnowledgeBase:
    """Simple knowledge base for ZUS Coffee products without vector store"""
    
    def __init__(self):
        self.products_data = [
            {
                "id": "zus-tumbler-black",
                "name": "ZUS Coffee Tumbler Black",
                "description": "Premium insulated tumbler in sleek black design, perfect for keeping your coffee hot or cold for hours. Made with high-quality stainless steel.",
                "price": "RM 45.00",
                "category": "drinkware",
                "tags": "tumbler black stainless steel insulated hot cold",
                "image_url": "https://shop.zuscoffee.com/tumbler-black.jpg",
                "features": ["Double-wall insulation", "Leak-proof lid", "Easy grip design", "350ml capacity"]
            },
            {
                "id": "zus-mug-ceramic-white",
                "name": "ZUS Ceramic Mug White",
                "description": "Classic white ceramic mug with ZUS Coffee logo. Perfect for your morning coffee or afternoon tea. Microwave and dishwasher safe.",
                "price": "RM 25.00",
                "category": "drinkware",
                "tags": "mug ceramic white coffee tea microwave dishwasher",
                "image_url": "https://shop.zuscoffee.com/mug-white.jpg",
                "features": ["Ceramic material", "Microwave safe", "Dishwasher safe", "300ml capacity"]
            },
            {
                "id": "zus-bottle-glass",
                "name": "ZUS Glass Water Bottle",
                "description": "Eco-friendly glass water bottle with protective silicone sleeve. Perfect for staying hydrated throughout the day.",
                "price": "RM 35.00",
                "category": "drinkware",
                "tags": "bottle glass water eco-friendly silicone hydration",
                "image_url": "https://shop.zuscoffee.com/bottle-glass.jpg",
                "features": ["Borosilicate glass", "Silicone sleeve", "Leak-proof cap", "500ml capacity"]
            },
            {
                "id": "zus-coffee-beans-signature",
                "name": "ZUS Signature Blend Coffee Beans",
                "description": "Our signature coffee blend with notes of chocolate and caramel. Medium roast, perfect for espresso or drip coffee.",
                "price": "RM 28.00",
                "category": "coffee",
                "tags": "coffee beans signature blend chocolate caramel medium roast espresso drip",
                "image_url": "https://shop.zuscoffee.com/beans-signature.jpg",
                "features": ["100% Arabica", "Medium roast", "Chocolate & caramel notes", "250g pack"]
            },
            {
                "id": "zus-travel-mug-steel",
                "name": "ZUS Travel Mug Stainless Steel",
                "description": "Durable stainless steel travel mug with secure lid and comfortable handle. Ideal for coffee on the go.",
                "price": "RM 40.00",
                "category": "drinkware",
                "tags": "travel mug stainless steel secure lid handle portable coffee",
                "image_url": "https://shop.zuscoffee.com/travel-mug.jpg",
                "features": ["Stainless steel construction", "Secure flip lid", "Comfortable handle", "400ml capacity"]
            },
            {
                "id": "zus-cold-brew-bottle",
                "name": "ZUS Cold Brew Bottle",
                "description": "Specially designed bottle for cold brew coffee with built-in filter. Make perfect cold brew at home.",
                "price": "RM 50.00",
                "category": "drinkware",
                "tags": "cold brew bottle filter coffee home brewing special design",
                "image_url": "https://shop.zuscoffee.com/cold-brew.jpg",
                "features": ["Built-in filter", "Airtight seal", "Easy pour spout", "750ml capacity"]
            }
        ]

class ProductsTool:
    """Simple products tool without vector store dependency"""
    
    def __init__(self):
        self.knowledge_base = SimpleProductKnowledgeBase()
    
    async def execute(self, query: str, top_k: int = 5) -> ToolResult:
        """Execute product search using simple text matching"""
        try:
            query_lower = query.lower()
            
            # Simple keyword-based matching
            matching_products = []
            for product in self.knowledge_base.products_data:
                score = self._calculate_similarity(query_lower, product)
                if score > 0:
                    product_copy = product.copy()
                    product_copy['similarity_score'] = score
                    matching_products.append(product_copy)
            
            # Sort by similarity score
            matching_products.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Limit results
            matching_products = matching_products[:top_k]
            
            if not matching_products:
                return ToolResult(
                    success=False,
                    error_message="No products found matching your query",
                    tool_name="products"
                )
            
            # Convert to ProductResult format
            product_results = []
            for product in matching_products:
                product_result = ProductResult(
                    id=product["id"],
                    name=product["name"],
                    description=product["description"],
                    price=product.get("price"),
                    image_url=product.get("image_url"),
                    similarity_score=product["similarity_score"]
                )
                product_results.append(product_result)
            
            # Generate summary
            summary = self._generate_summary(query, product_results)
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": [result.dict() for result in product_results],
                    "summary": summary,
                    "total_found": len(product_results)
                },
                tool_name="products"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Product search error: {str(e)}",
                tool_name="products"
            )
    
    def _calculate_similarity(self, query: str, product: Dict[str, Any]) -> float:
        """Calculate simple similarity score based on keyword matching"""
        score = 0.0
        
        # Create searchable text
        searchable_text = f"{product['name']} {product['description']} {product['tags']} {product['category']}".lower()
        
        # Split query into keywords
        query_keywords = query.split()
        
        for keyword in query_keywords:
            if len(keyword) > 2:  # Skip very short words
                if keyword in searchable_text:
                    # Higher score for name matches
                    if keyword in product['name'].lower():
                        score += 2.0
                    # Medium score for description matches
                    elif keyword in product['description'].lower():
                        score += 1.5
                    # Lower score for tag matches
                    elif keyword in product['tags'].lower():
                        score += 1.0
                    # Minimal score for category matches
                    elif keyword in product['category'].lower():
                        score += 0.5
        
        # Normalize score
        if query_keywords:
            score = score / len(query_keywords)
        
        return score
    
    def _generate_summary(self, query: str, results: List[ProductResult]) -> str:
        """Generate summary of search results"""
        if not results:
            return "No products found matching your query."
        
        query_lower = query.lower()
        
        if "drinkware" in query_lower or "cup" in query_lower or "mug" in query_lower:
            drinkware_items = [r for r in results if "drinkware" in r.description.lower() or "mug" in r.name.lower() or "tumbler" in r.name.lower()]
            if drinkware_items:
                return f"I found {len(drinkware_items)} drinkware items including tumblers, mugs, and bottles. Our drinkware collection features high-quality materials like stainless steel and ceramic, perfect for enjoying your ZUS coffee."
        
        if "coffee" in query_lower and "bean" in query_lower:
            coffee_items = [r for r in results if "coffee" in r.description.lower() and "bean" in r.description.lower()]
            if coffee_items:
                return f"Our coffee selection includes premium blends perfect for different brewing methods. The signature blend features chocolate and caramel notes."
        
        if "tumbler" in query_lower:
            return "Our tumblers are designed to keep your beverages at the perfect temperature with double-wall insulation and leak-proof design."
        
        if "mug" in query_lower:
            return "Our mugs combine style and functionality, perfect for your daily coffee ritual at home or office."
        
        # Generic summary
        categories = set()
        for result in results:
            if "drinkware" in result.description.lower():
                categories.add("drinkware")
            if "coffee" in result.description.lower():
                categories.add("coffee")
        
        if categories:
            cat_str = " and ".join(categories)
            return f"I found {len(results)} products in our {cat_str} collection. These items are carefully selected to enhance your ZUS Coffee experience."
        
        return f"I found {len(results)} products that match your query. Each item is designed with quality and functionality in mind."
    
    def add_product(self, product: Dict[str, Any]):
        """Add a new product to the knowledge base"""
        self.knowledge_base.products_data.append(product)
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products in the knowledge base"""
        return self.knowledge_base.products_data
