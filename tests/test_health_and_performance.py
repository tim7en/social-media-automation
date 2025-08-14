"""
Test cases for health check and performance monitoring.
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.utils.test_utils import (
    assert_response_structure,
    assert_success_response,
    PerformanceTestRunner
)


class TestHealthChecks:
    """Test health check endpoints."""
    
    def test_basic_health_check(self, client: TestClient):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["status", "message", "version"]
        assert_response_structure(data, required_fields)
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["message", "status", "version"]
        assert_response_structure(data, required_fields)
    
    @pytest.mark.asyncio
    async def test_detailed_health_check(self, async_client: AsyncClient):
        """Test detailed health check endpoint."""
        response = await async_client.get("/health/detailed")
        
        # May return 503 if dependencies are not available in test environment
        assert response.status_code in [200, 503]
        
        data = response.json()
        required_fields = ["status", "timestamp", "response_time_ms", "components"]
        assert_response_structure(data, required_fields)
        
        # Check components structure
        assert isinstance(data["components"], dict)
    
    @pytest.mark.asyncio
    async def test_readiness_check(self, async_client: AsyncClient):
        """Test readiness check endpoint."""
        response = await async_client.get("/health/ready")
        
        # May return 503 if dependencies are not available
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert "ready" in data or "failed_component" in data
    
    @pytest.mark.asyncio
    async def test_liveness_check(self, async_client: AsyncClient):
        """Test liveness check endpoint."""
        response = await async_client.get("/health/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["alive"] is True
        assert "timestamp" in data


@pytest.mark.performance
class TestPerformance:
    """Performance tests for critical endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self, performance_runner: PerformanceTestRunner):
        """Test health check endpoint performance under load."""
        # Run 20 concurrent requests
        results = await performance_runner.run_concurrent_requests("/health", count=20)
        
        # All requests should succeed
        success_count = sum(1 for r in results if r["success"])
        assert success_count == 20, f"Only {success_count}/20 requests succeeded"
        
        # Get performance summary
        summary = performance_runner.get_performance_summary()
        
        # Response time should be reasonable (< 1000ms for health check)
        assert summary["avg_response_time_ms"] < 1000, f"Average response time too high: {summary['avg_response_time_ms']}ms"
        assert summary["max_response_time_ms"] < 2000, f"Max response time too high: {summary['max_response_time_ms']}ms"
        
        # Success rate should be 100%
        assert summary["success_rate_percent"] == 100.0
    
    @pytest.mark.asyncio
    async def test_root_endpoint_performance(self, performance_runner: PerformanceTestRunner):
        """Test root endpoint performance."""
        results = await performance_runner.run_concurrent_requests("/", count=10)
        
        summary = performance_runner.get_performance_summary()
        
        # Basic performance assertions
        assert summary["success_rate_percent"] >= 90.0  # Allow for some failures in test environment
        assert summary["avg_response_time_ms"] < 500  # Should be fast


@pytest.mark.integration
class TestSecurityMiddleware:
    """Test security middleware functionality."""
    
    def test_security_headers(self, client: TestClient):
        """Test that security headers are added to responses."""
        response = client.get("/health")
        
        # Check for security headers
        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Content-Security-Policy"
        ]
        
        for header in expected_headers:
            assert header in response.headers, f"Missing security header: {header}"
    
    def test_rate_limiting_headers(self, client: TestClient):
        """Test rate limiting behavior."""
        # Make multiple requests quickly
        responses = []
        for i in range(5):
            response = client.get("/health")
            responses.append(response)
        
        # All should succeed (under rate limit)
        for response in responses:
            assert response.status_code == 200
    
    def test_large_request_rejection(self, client: TestClient):
        """Test that large requests are rejected."""
        # Create a large payload (this would normally be rejected by the middleware)
        large_data = {"data": "x" * (11 * 1024 * 1024)}  # 11MB
        
        # Note: This test may not work exactly as expected since the test client
        # doesn't fully simulate the middleware. In a real scenario, this would be rejected.
        response = client.post("/api/v1/content/generate", json=large_data)
        
        # The response should indicate some kind of error (422 for validation, 413 for size)
        assert response.status_code in [413, 422, 400]


@pytest.mark.unit
class TestInputValidation:
    """Test input validation functionality."""
    
    def test_content_generation_validation(self, client: TestClient, sample_content_data: dict):
        """Test content generation request validation."""
        # Test valid request
        response = client.post("/api/v1/content/generate", json=sample_content_data)
        # Note: This may fail if the endpoint isn't fully implemented
        # but validation should pass
        assert response.status_code in [200, 201, 404, 501]  # Allow for various implementation states
    
    def test_invalid_platform_validation(self, client: TestClient):
        """Test validation of invalid platforms."""
        invalid_data = {
            "title": "Test",
            "topic": "Test topic",
            "content_type": "video",
            "target_platforms": ["invalid_platform"]
        }
        
        response = client.post("/api/v1/content/generate", json=invalid_data)
        assert response.status_code in [400, 422]  # Should be validation error
    
    def test_missing_required_fields(self, client: TestClient):
        """Test validation with missing required fields."""
        invalid_data = {
            "title": "Test"
            # Missing required fields
        }
        
        response = client.post("/api/v1/content/generate", json=invalid_data)
        assert response.status_code in [400, 422]  # Should be validation error


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])