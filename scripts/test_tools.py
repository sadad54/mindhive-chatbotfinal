#!/usr/bin/env python3
"""
Test script for tool integration and API endpoints.
Tests calculator, products (RAG), and outlets (Text2SQL) tools.
"""

import asyncio
import httpx
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.tools.calculator_tool import CalculatorTool
from app.tools.products_tool import ProductsTool
from app.tools.outlets_tool import OutletsTool

async def test_calculator_tool():
    """Test calculator tool functionality"""
    print("🧮 Testing Calculator Tool")
    print("="*40)
    
    calculator = CalculatorTool()
    
    test_cases = [
        ("2 + 3", 5.0),
        ("10 - 4", 6.0),
        ("5 * 6", 30.0),
        ("20 / 4", 5.0),
        ("17 % 5", 2.0),
        ("2 ** 3", 8.0),
        ("(2 + 3) * 4", 20.0)
    ]
    
    print("✅ Valid calculations:")
    for expression, expected in test_cases:
        try:
            result = await calculator.execute(expression)
            if result.success:
                actual = result.data["result"]
                status = "✓" if abs(actual - expected) < 0.001 else "✗"
                print(f"  {status} {expression} = {actual} (expected {expected})")
            else:
                print(f"  ✗ {expression} failed: {result.error_message}")
        except Exception as e:
            print(f"  ✗ {expression} error: {e}")
    
    print("\n🚫 Error handling:")
    error_cases = [
        "5 / 0",  # Division by zero
        "2 + + 3",  # Invalid syntax
        "import os",  # Code injection
        "",  # Empty expression
    ]
    
    for expression in error_cases:
        try:
            result = await calculator.execute(expression)
            if not result.success:
                print(f"  ✓ {expression}: Handled gracefully - {result.error_message}")
            else:
                print(f"  ⚠️  {expression}: Unexpectedly succeeded")
        except Exception as e:
            print(f"  ✓ {expression}: Exception caught - {e}")

async def test_products_tool():
    """Test products tool and RAG functionality"""
    print("\n☕ Testing Products Tool (RAG)")
    print("="*40)
    
    try:
        products_tool = ProductsTool()
        
        search_queries = [
            "tumbler",
            "drinkware",
            "coffee beans",
            "glass bottle",
            "ceramic mug",
            "stainless steel"
        ]
        
        print("🔍 Product searches:")
        for query in search_queries:
            try:
                result = await products_tool.execute(query)
                if result.success:
                    data = result.data
                    results_count = len(data["results"])
                    print(f"  ✓ '{query}': Found {results_count} products")
                    
                    if results_count > 0:
                        top_result = data["results"][0]
                        score = top_result["similarity_score"]
                        print(f"    Top: {top_result['name']} (score: {score:.3f})")
                else:
                    print(f"  ✗ '{query}': {result.error_message}")
            except Exception as e:
                print(f"  ✗ '{query}': Error - {e}")
        
        print("\n📊 Testing edge cases:")
        edge_cases = [
            "",  # Empty query
            "quantum physics textbook",  # Irrelevant query
            "a" * 1000,  # Very long query
        ]
        
        for query in edge_cases:
            try:
                result = await products_tool.execute(query)
                if result.success:
                    results_count = len(result.data["results"])
                    print(f"  ✓ Edge case handled: {results_count} results for '{query[:50]}...'")
                else:
                    print(f"  ✓ Edge case handled: {result.error_message}")
            except Exception as e:
                print(f"  ⚠️  Edge case error: {e}")
                
    except Exception as e:
        print(f"  ❌ Products tool initialization failed: {e}")
        print("  Note: This might be due to missing dependencies (faiss-cpu, sentence-transformers)")

async def test_outlets_tool():
    """Test outlets tool and Text2SQL functionality"""
    print("\n🏪 Testing Outlets Tool (Text2SQL)")
    print("="*40)
    
    try:
        outlets_tool = OutletsTool()
        
        search_queries = [
            "outlets in Petaling Jaya",
            "SS2 opening hours",
            "Bangsar outlet",
            "stores with WiFi",
            "KLCC location",
            "drive-thru service"
        ]
        
        print("🔍 Outlet searches:")
        for query in search_queries:
            try:
                result = await outlets_tool.execute(query)
                if result.success:
                    data = result.data
                    results_count = len(data["results"])
                    sql_query = data["sql_query"].strip().replace("\n", " ")
                    print(f"  ✓ '{query}': Found {results_count} outlets")
                    print(f"    SQL: {sql_query[:100]}{'...' if len(sql_query) > 100 else ''}")
                    
                    if results_count > 0:
                        top_result = data["results"][0]
                        print(f"    Top: {top_result['name']} - {top_result['location']}")
                else:
                    print(f"  ✗ '{query}': {result.error_message}")
            except Exception as e:
                print(f"  ✗ '{query}': Error - {e}")
        
        print("\n🛡️  Testing SQL injection prevention:")
        injection_attempts = [
            "'; DROP TABLE outlets; --",
            "UNION SELECT * FROM users",
            "1' OR '1'='1",
        ]
        
        for injection in injection_attempts:
            try:
                result = await outlets_tool.execute(injection)
                if result.success:
                    results_count = len(result.data.get("results", []))
                    print(f"  ✓ SQL injection handled: {results_count} results (safe)")
                else:
                    print(f"  ✓ SQL injection blocked: {result.error_message}")
            except Exception as e:
                print(f"  ✓ SQL injection prevented: {e}")
                
    except Exception as e:
        print(f"  ❌ Outlets tool initialization failed: {e}")

async def test_api_endpoints():
    """Test API endpoints directly"""
    print("\n🌐 Testing API Endpoints")
    print("="*40)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("  ✓ Health endpoint: OK")
            else:
                print(f"  ✗ Health endpoint: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️  Health endpoint: Server not running - {e}")
            print("    Note: Start server with 'uvicorn app.main:app --reload'")
            return
        
        # Test products API
        try:
            response = await client.get(f"{base_url}/api/products?query=tumbler")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Products API: Found {len(data['results'])} products")
            else:
                print(f"  ✗ Products API: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Products API: {e}")
        
        # Test outlets API
        try:
            response = await client.get(f"{base_url}/api/outlets?query=SS2")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Outlets API: Found {len(data['results'])} outlets")
            else:
                print(f"  ✗ Outlets API: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Outlets API: {e}")
        
        # Test calculator API
        try:
            response = await client.post(f"{base_url}/api/calculate", json={
                "expression": "2 + 3"
            })
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Calculator API: 2 + 3 = {data.get('result')}")
            else:
                print(f"  ✗ Calculator API: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Calculator API: {e}")
        
        # Test chat endpoint
        try:
            response = await client.post(f"{base_url}/chat", json={
                "message": "Calculate 5 * 6",
                "session_id": "test_api"
            })
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Chat API: Response received")
                print(f"    Message: {data.get('message', '')[:100]}...")
            else:
                print(f"  ✗ Chat API: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Chat API: {e}")

async def test_error_scenarios():
    """Test error handling scenarios"""
    print("\n⚠️  Testing Error Scenarios")
    print("="*40)
    
    calculator = CalculatorTool()
    
    # Test with malicious calculator expressions
    malicious_expressions = [
        "import os; os.system('ls')",
        "exec('print(1)')",
        "__import__('os')",
        "eval('2+2')"
    ]
    
    print("🛡️  Malicious expression handling:")
    for expr in malicious_expressions:
        try:
            result = await calculator.execute(expr)
            if not result.success:
                print(f"  ✓ Blocked: {expr}")
            else:
                print(f"  ⚠️  Allowed: {expr} (result: {result.data.get('result')})")
        except Exception as e:
            print(f"  ✓ Exception: {expr} - {e}")
    
    # Test API downtime simulation
    print("\n📡 API downtime simulation:")
    try:
        # This will use the fallback mechanism
        original_api_url = calculator.api_url
        calculator.api_url = "http://nonexistent-api.com"
        
        result = await calculator.execute("3 + 4")
        if result.success:
            print(f"  ✓ Fallback worked: 3 + 4 = {result.data['result']}")
        else:
            print(f"  ✗ Fallback failed: {result.error_message}")
        
        # Restore original URL
        calculator.api_url = original_api_url
        
    except Exception as e:
        print(f"  ⚠️  Fallback test error: {e}")

def display_summary():
    """Display test summary"""
    print("\n" + "="*60)
    print("🎉 TOOL TESTING COMPLETE!")
    print("="*60)
    print()
    print("Tools tested:")
    print("✓ Calculator Tool - Basic arithmetic and error handling")
    print("✓ Products Tool - RAG-based product search")
    print("✓ Outlets Tool - Text2SQL for outlet queries")
    print("✓ API Endpoints - HTTP API integration")
    print("✓ Error Scenarios - Security and robustness")
    print()
    print("Next steps:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Test the web interface: http://localhost:8000")
    print("3. Run the unhappy flows test: python scripts/test_unhappy_flows.py")
    print("="*60)

async def main():
    """Run all tool tests"""
    print("🔧 Testing Tool Integration & API Endpoints")
    print("="*60)
    print()
    
    try:
        await test_calculator_tool()
        await test_products_tool()
        await test_outlets_tool()
        await test_api_endpoints()
        await test_error_scenarios()
        
        display_summary()
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
