import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.tools.calculator_tool import CalculatorTool
from app.tools.products_tool import ProductsTool
from app.tools.outlets_tool import OutletsTool
from app.models.schemas import ToolResult

@pytest.fixture
def calculator_tool():
    return CalculatorTool()

@pytest.fixture
def products_tool():
    return ProductsTool()

@pytest.fixture
def outlets_tool():
    return OutletsTool()

class TestCalculatorTool:
    """Test calculator tool functionality and error handling"""
    
    @pytest.mark.asyncio
    async def test_basic_calculations(self, calculator_tool):
        """Test basic arithmetic operations"""
        test_cases = [
            ("2 + 3", 5.0),
            ("10 - 4", 6.0),
            ("5 * 6", 30.0),
            ("20 / 4", 5.0),
            ("17 % 5", 2.0),
            ("2 ** 3", 8.0)
        ]
        
        for expression, expected in test_cases:
            result = await calculator_tool.execute(expression)
            assert result.success
            assert result.data["result"] == expected
            assert result.data["expression"] == expression
    
    @pytest.mark.asyncio
    async def test_calculator_error_handling(self, calculator_tool):
        """Test calculator error handling for invalid inputs"""
        error_cases = [
            "2 / 0",  # Division by zero
            "2 + + 3",  # Invalid syntax
            "import os",  # Code injection attempt
            "print('hello')",  # Non-math expression
            "2 + abc",  # Invalid variables
        ]
        
        for expression in error_cases:
            result = await calculator_tool.execute(expression)
            assert not result.success
            assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_calculator_api_fallback(self, calculator_tool):
        """Test fallback to local evaluation when API is down"""
        # Mock the external API to fail
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("API Error")
            
            result = await calculator_tool.execute("2 + 3")
            assert result.success
            assert result.data["result"] == 5.0
            assert result.data["method"] == "local_eval"
    
    def test_expression_validation(self, calculator_tool):
        """Test expression validation"""
        valid_expressions = ["2 + 3", "10 * 5", "(2 + 3) * 4"]
        invalid_expressions = ["import os", "print()", "2 + abc"]
        
        for expr in valid_expressions:
            assert calculator_tool.validate_expression(expr)
        
        for expr in invalid_expressions:
            assert not calculator_tool.validate_expression(expr)

class TestProductsTool:
    """Test products tool and RAG functionality"""
    
    @pytest.mark.asyncio
    async def test_product_search(self, products_tool):
        """Test basic product search functionality"""
        result = await products_tool.execute("tumbler")
        
        assert result.success
        assert "results" in result.data
        assert len(result.data["results"]) > 0
        
        # Check if tumbler products are found
        tumbler_found = any("tumbler" in product["name"].lower() 
                          for product in result.data["results"])
        assert tumbler_found
    
    @pytest.mark.asyncio
    async def test_product_search_empty_query(self, products_tool):
        """Test product search with empty or nonsensical query"""
        result = await products_tool.execute("")
        # Should still return some results or handle gracefully
        assert result.success or "empty query" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_product_search_no_results(self, products_tool):
        """Test product search when no relevant products found"""
        result = await products_tool.execute("quantum physics textbook")
        
        # Should handle gracefully - either no results or very low similarity
        if result.success:
            if result.data["results"]:
                # If results returned, they should have low similarity scores
                for product in result.data["results"]:
                    assert product["similarity_score"] < 0.5
        else:
            assert "no products found" in result.error_message.lower()

class TestOutletsTool:
    """Test outlets tool and Text2SQL functionality"""
    
    @pytest.mark.asyncio
    async def test_outlet_location_query(self, outlets_tool):
        """Test querying outlets by location"""
        result = await outlets_tool.execute("outlets in Petaling Jaya")
        
        assert result.success
        assert "results" in result.data
        assert len(result.data["results"]) > 0
        
        # Check if Petaling Jaya outlets are found
        pj_found = any("petaling jaya" in outlet["location"].lower() 
                      for outlet in result.data["results"])
        assert pj_found
    
    @pytest.mark.asyncio
    async def test_outlet_hours_query(self, outlets_tool):
        """Test querying outlet opening hours"""
        result = await outlets_tool.execute("SS2 outlet opening hours")
        
        assert result.success
        assert "results" in result.data
        
        if result.data["results"]:
            outlet = result.data["results"][0]
            assert "opening_hours" in outlet
            assert outlet["opening_hours"] is not None
    
    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self, outlets_tool):
        """Test SQL injection prevention"""
        malicious_queries = [
            "'; DROP TABLE outlets; --",
            "UNION SELECT * FROM users",
            "INSERT INTO outlets VALUES",
            "DELETE FROM outlets WHERE"
        ]
        
        for query in malicious_queries:
            result = await outlets_tool.execute(query)
            # Should either fail safely or return empty results
            assert not result.success or len(result.data.get("results", [])) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_location_query(self, outlets_tool):
        """Test querying for non-existent locations"""
        result = await outlets_tool.execute("outlets in Mars")
        
        assert result.success
        # Should return empty results for non-existent locations
        assert len(result.data["results"]) == 0

class TestToolIntegration:
    """Test tool integration and error recovery"""
    
    @pytest.mark.asyncio
    async def test_tool_timeout_handling(self, calculator_tool):
        """Test handling of tool timeouts"""
        # Mock a timeout scenario
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = asyncio.TimeoutError()
            
            result = await calculator_tool.execute("2 + 3")
            # Should fallback to local calculation
            assert result.success
            assert result.data["result"] == 5.0
    
    @pytest.mark.asyncio
    async def test_tool_network_error_recovery(self, calculator_tool):
        """Test recovery from network errors"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("Network error")
            
            result = await calculator_tool.execute("5 * 6")
            # Should still work with local fallback
            assert result.success
            assert result.data["result"] == 30.0

class TestUnhappyFlowScenarios:
    """Test comprehensive unhappy flow scenarios"""
    
    @pytest.mark.asyncio
    async def test_missing_parameters(self):
        """Test handling of missing parameters"""
        calculator = CalculatorTool()
        
        # Empty expression
        result = await calculator.execute("")
        assert not result.success
        
        # Whitespace only
        result = await calculator.execute("   ")
        assert not result.success
    
    @pytest.mark.asyncio
    async def test_malformed_requests(self, outlets_tool):
        """Test handling of malformed requests"""
        malformed_queries = [
            None,  # Would be handled by API validation
            "",     # Empty query
            "   ",  # Whitespace only
            "SELECT * FROM non_existent_table",  # Invalid table
            "This is not a query at all just random text" * 100  # Very long nonsensical query
        ]
        
        for query in malformed_queries:
            if query is not None:  # Skip None as it would be caught by API validation
                result = await outlets_tool.execute(query)
                # Should handle gracefully without crashing
                assert isinstance(result, ToolResult)
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion(self, products_tool):
        """Test handling of resource exhaustion scenarios"""
        # Test with very large query
        large_query = "drinkware " * 1000
        
        result = await products_tool.execute(large_query)
        # Should handle without crashing
        assert isinstance(result, ToolResult)
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_usage(self):
        """Test concurrent usage of tools"""
        calculator = CalculatorTool()
        
        # Create multiple concurrent calculation tasks
        tasks = []
        for i in range(10):
            tasks.append(calculator.execute(f"{i} + {i}"))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All results should be successful
        for i, result in enumerate(results):
            assert isinstance(result, ToolResult)
            if result.success:
                assert result.data["result"] == i + i

if __name__ == "__main__":
    pytest.main([__file__])
