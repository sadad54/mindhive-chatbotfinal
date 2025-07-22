import os
import json
import httpx
from typing import List, Dict, Any
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models.schemas import ToolResult, ProductResult

class ProductVectorStore:
    """Vector store for product knowledge base using FAISS"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.products = []
        self.embeddings = None
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
    
    def add_products(self, products: List[Dict[str, Any]]):
        """Add products to the vector store"""
        self.products = products
        
        # Create text representations for embedding
        texts = []
        for product in products:
            text = f"{product['name']} {product['description']} {product.get('category', '')} {product.get('tags', '')}"
            texts.append(text)
        
        # Generate embeddings
        embeddings = self.model.encode(texts)
        self.embeddings = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for similarity
        faiss.normalize_L2(self.embeddings)  # Normalize for cosine similarity
        self.index.add(self.embeddings)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar products"""
        if self.index is None:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.products):
                product = self.products[idx].copy()
                product['similarity_score'] = float(score)
                results.append(product)
        
        return results
    
    def save(self, path: str):
        """Save vector store to disk"""
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        if self.index is not None:
            faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        
        # Save products and embeddings
        with open(os.path.join(path, "products.json"), 'w') as f:
            json.dump(self.products, f, indent=2)
        
        if self.embeddings is not None:
            np.save(os.path.join(path, "embeddings.npy"), self.embeddings)
    
    def load(self, path: str):
        """Load vector store from disk"""
        if not os.path.exists(path):
            return False
        
        try:
            # Load FAISS index
            index_path = os.path.join(path, "index.faiss")
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
            
            # Load products
            products_path = os.path.join(path, "products.json")
            if os.path.exists(products_path):
                with open(products_path, 'r') as f:
                    self.products = json.load(f)
            
            # Load embeddings
            embeddings_path = os.path.join(path, "embeddings.npy")
            if os.path.exists(embeddings_path):
                self.embeddings = np.load(embeddings_path)
            
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False

class ProductKnowledgeBase:
    """Knowledge base for ZUS Coffee products"""
    
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
    """Tool for product knowledge base retrieval using RAG"""
    
    def __init__(self, vector_store_path: str = "./data/vector_store"):
        self.vector_store_path = vector_store_path
        self.vector_store = ProductVectorStore()
        self.knowledge_base = ProductKnowledgeBase()
        self._initialize()
    
    def _initialize(self):
        """Initialize the vector store"""
        # Try to load existing vector store
        if not self.vector_store.load(self.vector_store_path):
            # Create new vector store
            print("Creating new product vector store...")
            self.vector_store.add_products(self.knowledge_base.products_data)
            self.vector_store.save(self.vector_store_path)
            print("Product vector store created and saved.")
    
    async def execute(self, query: str, top_k: int = 5) -> ToolResult:
        """Execute product search using RAG"""
        try:
            # Search for relevant products
            search_results = self.vector_store.search(query, top_k)
            
            if not search_results:
                return ToolResult(
                    success=False,
                    error_message="No products found matching your query",
                    tool_name="products"
                )
            
            # Convert to ProductResult format
            product_results = []
            for product in search_results:
                product_result = ProductResult(
                    id=product["id"],
                    name=product["name"],
                    description=product["description"],
                    price=product.get("price"),
                    image_url=product.get("image_url"),
                    similarity_score=product["similarity_score"]
                )
                product_results.append(product_result)
            
            # Generate AI summary
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
    
    def _generate_summary(self, query: str, results: List[ProductResult]) -> str:
        """Generate AI summary of search results"""
        if not results:
            return "No products found matching your query."
        
        # Simple rule-based summary generation
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
        # Rebuild vector store
        self.vector_store.add_products(self.knowledge_base.products_data)
        self.vector_store.save(self.vector_store_path)
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products in the knowledge base"""
        return self.knowledge_base.products_data
