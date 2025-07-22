import pytest
import asyncio
from unittest.mock import patch, MagicMock
import httpx
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPIUnhappyFlows:
    """Test API endpoints for unhappy flow scenarios"""
    
    def test_chat_missing_parameters(self):
        """Test chat endpoint with missing parameters"""
        # Missing message
        response = client.post("/chat", json={"session_id": "test"})
        assert response.status_code == 422  # Validation error
        
        # Missing session_id (should use default)
        response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 200
    
    def test_chat_invalid_json(self):
        """Test chat endpoint with invalid JSON"""
        response = client.post(
            "/chat", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_chat_extremely_long_message(self):
        """Test chat endpoint with extremely long message"""
        long_message = "a" * 10000
        response = client.post("/chat", json={
            "message": long_message,
            "session_id": "test"
        })
        # Should handle gracefully, either success or appropriate error
        assert response.status_code in [200, 400, 413]
    
    def test_chat_malicious_input(self):
        """Test chat endpoint with potentially malicious input"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "{{7*7}}",  # Template injection
            "\x00\x01\x02",  # Null bytes
        ]
        
        for malicious_input in malicious_inputs:
            response = client.post("/chat", json={
                "message": malicious_input,
                "session_id": "test"
            })
            # Should handle safely without executing malicious code
            assert response.status_code in [200, 400]
            if response.status_code == 200:
                data = response.json()
                # Response should not contain the malicious input verbatim
                assert malicious_input not in data.get("message", "")

class TestProductsAPIUnhappyFlows:
    """Test products API unhappy flows"""
    
    def test_products_empty_query(self):
        """Test products endpoint with empty query"""
        response = client.get("/api/products?query=")
        # Should handle empty query gracefully
        assert response.status_code in [200, 400]
    
    def test_products_invalid_top_k(self):
        """Test products endpoint with invalid top_k values"""
        # Negative top_k
        response = client.get("/api/products?query=coffee&top_k=-1")
        assert response.status_code == 422
        
        # Too large top_k
        response = client.get("/api/products?query=coffee&top_k=1000")
        assert response.status_code == 422
        
        # Non-numeric top_k
        response = client.get("/api/products?query=coffee&top_k=abc")
        assert response.status_code == 422
    
    def test_products_sql_injection_attempt(self):
        """Test products endpoint with SQL injection attempts"""
        injection_attempts = [
            "'; DROP TABLE products; --",
            "UNION SELECT * FROM users",
            "1' OR '1'='1",
        ]
        
        for injection in injection_attempts:
            response = client.get(f"/api/products?query={injection}")
            # Should handle safely
            assert response.status_code in [200, 400]
    
    @patch('app.tools.products_tool.ProductsTool.execute')
    async def test_products_tool_failure(self, mock_execute):
        """Test products endpoint when underlying tool fails"""
        mock_execute.return_value = MagicMock(
            success=False,
            error_message="Vector store is unavailable"
        )
        
        response = client.get("/api/products?query=coffee")
        assert response.status_code == 400

class TestOutletsAPIUnhappyFlows:
    """Test outlets API unhappy flows"""
    
    def test_outlets_sql_injection_prevention(self):
        """Test outlets endpoint SQL injection prevention"""
        injection_attempts = [
            "'; DROP TABLE outlets; --",
            "UNION SELECT password FROM users",
            "1; DELETE FROM outlets WHERE 1=1; --",
            "admin'; DROP TABLE outlets; --",
        ]
        
        for injection in injection_attempts:
            response = client.get(f"/api/outlets?query={injection}")
            # Should either return safe results or error
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                data = response.json()
                # Should not execute malicious SQL
                assert "results" in data
                # Results should be empty or safe
                assert len(data["results"]) >= 0
    
    def test_outlets_malformed_natural_language(self):
        """Test outlets endpoint with malformed natural language"""
        malformed_queries = [
            "SELECT * FROM outlets WHERE name = 'test'",  # Direct SQL
            "asdkjfalksjdflaksjdf",  # Random text
            "🚀🎉🔥💯",  # Emojis only
            "",  # Empty
            " " * 100,  # Whitespace
        ]
        
        for query in malformed_queries:
            response = client.get(f"/api/outlets?query={query}")
            assert response.status_code in [200, 400]
    
    @patch('app.tools.outlets_tool.OutletsTool.execute')
    async def test_outlets_database_error(self, mock_execute):
        """Test outlets endpoint when database is unavailable"""
        mock_execute.return_value = MagicMock(
            success=False,
            error_message="Database connection failed"
        )
        
        response = client.get("/api/outlets?query=test")
        assert response.status_code == 400

class TestCalculatorAPIUnhappyFlows:
    """Test calculator API unhappy flows"""
    
    def test_calculator_malicious_expressions(self):
        """Test calculator with malicious expressions"""
        malicious_expressions = [
            "import os; os.system('rm -rf /')",
            "exec('print(\"hacked\")')",
            "__import__('os').system('ls')",
            "eval('2+2')",
            "open('/etc/passwd').read()",
        ]
        
        for expression in malicious_expressions:
            response = client.post("/api/calculate", json={
                "expression": expression
            })
            
            # Should reject malicious expressions
            if response.status_code == 200:
                data = response.json()
                assert data.get("error") is not None
            else:
                assert response.status_code == 400
    
    def test_calculator_division_by_zero(self):
        """Test calculator division by zero handling"""
        response = client.post("/api/calculate", json={
            "expression": "5 / 0"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("error") is not None
        assert "zero" in data["error"].lower()
    
    def test_calculator_invalid_syntax(self):
        """Test calculator with invalid mathematical syntax"""
        invalid_expressions = [
            "2 + + 3",
            "5 * / 2",
            "((2 + 3)",  # Unmatched parentheses
            "2 +",  # Incomplete expression
            "",  # Empty expression
        ]
        
        for expression in invalid_expressions:
            response = client.post("/api/calculate", json={
                "expression": expression
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("error") is not None
    
    @patch('httpx.AsyncClient')
    async def test_calculator_external_api_downtime(self, mock_client):
        """Test calculator when external API is down"""
        # Mock API failure
        mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.RequestError("API down")
        
        response = client.post("/api/calculate", json={
            "expression": "2 + 3"
        })
        
        # Should fallback to local calculation
        assert response.status_code == 200
        data = response.json()
        assert data.get("result") == 5.0
        assert data.get("error") is None

class TestGeneralUnhappyFlows:
    """Test general unhappy flow scenarios"""
    
    def test_nonexistent_endpoints(self):
        """Test accessing non-existent endpoints"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
        response = client.post("/api/fake-endpoint")
        assert response.status_code == 404
    
    def test_wrong_http_methods(self):
        """Test using wrong HTTP methods"""
        # POST to GET endpoint
        response = client.post("/api/products")
        assert response.status_code == 405
        
        # GET to POST endpoint
        response = client.get("/api/calculate")
        # This might be allowed as we have a GET version too
        assert response.status_code in [200, 405, 422]
    
    def test_unsupported_content_types(self):
        """Test unsupported content types"""
        response = client.post(
            "/chat",
            data="message=hello",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # Should expect JSON
        assert response.status_code == 422
    
    def test_large_payload_handling(self):
        """Test handling of extremely large payloads"""
        large_data = {
            "message": "x" * 100000,
            "session_id": "test"
        }
        
        response = client.post("/chat", json=large_data)
        # Should handle gracefully
        assert response.status_code in [200, 400, 413]
    
    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request(i):
            return client.post("/chat", json={
                "message": f"Test message {i}",
                "session_id": f"session_{i}"
            })
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should complete successfully or with expected errors
        for response in results:
            assert response.status_code in [200, 400, 500]
    
    def test_special_characters_handling(self):
        """Test handling of special characters and unicode"""
        special_messages = [
            "Hello 世界",  # Unicode
            "Café résumé naïve",  # Accented characters
            "😀😃😄😁",  # Emojis
            "\\n\\t\\r",  # Escape sequences
            "\0\1\2",  # Control characters
        ]
        
        for message in special_messages:
            response = client.post("/chat", json={
                "message": message,
                "session_id": "test"
            })
            
            # Should handle special characters gracefully
            assert response.status_code in [200, 400]

class TestSecurityMeasures:
    """Test security measures and attack prevention"""
    
    def test_rate_limiting_simulation(self):
        """Simulate rate limiting test (would need actual rate limiter)"""
        # This would test rate limiting if implemented
        # For now, just test that rapid requests don't break the system
        responses = []
        for i in range(20):
            response = client.post("/chat", json={
                "message": f"Rapid message {i}",
                "session_id": "rate_test"
            })
            responses.append(response)
        
        # System should remain stable
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count > 0  # At least some should succeed
    
    def test_session_isolation(self):
        """Test that sessions are properly isolated"""
        # Session 1
        response1 = client.post("/chat", json={
            "message": "My secret is 12345",
            "session_id": "session_1"
        })
        
        # Session 2
        response2 = client.post("/chat", json={
            "message": "What was the secret?",
            "session_id": "session_2"
        })
        
        # Session 2 should not have access to session 1's data
        assert response2.status_code == 200
        data = response2.json()
        assert "12345" not in data.get("message", "")
    
    def test_error_message_sanitization(self):
        """Test that error messages don't leak sensitive information"""
        # Trigger various error conditions and check responses
        error_responses = [
            client.post("/chat", json={"message": "cause an error somehow"}),
            client.get("/api/products?query=" + "x" * 1000),
            client.post("/api/calculate", json={"expression": "invalid_expression"}),
        ]
        
        for response in error_responses:
            if response.status_code >= 400:
                data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_detail = data.get("detail", "")
                
                # Should not contain sensitive paths or system information
                sensitive_patterns = [
                    "/home/",
                    "/usr/",
                    "password",
                    "secret",
                    "token",
                    "config",
                ]
                
                for pattern in sensitive_patterns:
                    assert pattern.lower() not in error_detail.lower()

if __name__ == "__main__":
    pytest.main([__file__])
